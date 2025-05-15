import sys
sys.path.append('./')
import os
from typing import List 
from fastapi import HTTPException, Depends,Request,Form, UploadFile, File, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from starlette import status
from sqlalchemy import cast, String
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse,JSONResponse
from typing import List, Optional
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import models.models as models
import schemas.schemas as schemas
import datetime
from sqlalchemy.sql import text 
from sqlalchemy import or_
from fastapi import APIRouter
from config.connection import get_db
from config.config import https_url_for
from config.config import pwd_context, hash_password
import json
from config.config import verify_session, create_session_token


# router  = APIRouter(prefix='/users', tags=['Users'])
router  = APIRouter()
templates = Jinja2Templates(directory="templates")


templates.env.globals["https_url_for"] = https_url_for

UPLOAD_DIR = "uploaded_files"  # Directory to save uploaded files
os.makedirs(UPLOAD_DIR, exist_ok=True)
UPLOAD_PROFILE ="profiles"
os.makedirs(UPLOAD_PROFILE, exist_ok=True)



@router.get("/")
def root():
    return RedirectResponse("/login")
@router.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "body_class": "bg-light"})


@router.post("/login")
def login_user(request: Request, email:str=Form(...), password:str=Form(...), db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "body_class": "bg-light", "error": "Mot de passe ou addresse email invalide"})
    
    session_token = create_session_token(
        username=email,
        ip=request.client.host,
        user_agent=request.headers.get("user-agent"),

    )

    log_entry = models.ActivityLog(
        user_id=user.id,
        action="LOGIN",
        details=f"User logged in from IP {request.client.host}"
        # ip=request.client.host,
        # user_agent=request.headers.get("user-agent"),
        # timestamp=datetime.datetime.now(),
    )
    db.add(log_entry)
    db.commit()
    response = RedirectResponse("/admin", status_code=303)
    response.set_cookie(key="session_token", value=session_token, httponly=True, secure=False,samesite="strict")  # Set cookie for 1 hour
    return response


@router.get("/logout")
def logout(request:Request, db:Session=Depends(get_db), auth:str=Depends(verify_session)):
    user = db.query(models.User).filter(models.User.email==auth).first()
    log_entry = models.ActivityLog(
        user_id=user.id,
        action="logout",
        details=f"User logged out",
    )
    db.add(log_entry)
    db.commit()

    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(key="username")
    return response

@router.get('/admin', response_class=HTMLResponse)
def index(request:Request,
          db:Session = Depends(get_db), 
          auth:str=Depends(verify_session),
          draw: Optional[int] = Query(1),  # DataTables parameter
          start: Optional[int] = Query(0),  # DataTables parameter (offset)
          length: Optional[int] = Query(10),  # DataTables parameter (page size)
          search_value: Optional[str] = Query(None),  
          category_filter: Optional[str] = Query(None),
          column_filter: Optional[str] = Query(None),
          column_value: Optional[str] = Query(None)
          ):
    try:


        user = db.query(models.User).filter(models.User.email == auth).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        role = user.role
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            query = db.query(
                models.Agent.id,
                models.Agent.title_number,
                models.Agent.nni,
                models.Agent.fullname,
                models.Agent.date_of_birth,
                models.Agent.birth_place,
                models.Agent.category,
                models.Agent.telephone,
                func.replace(models.Agent.document_path, '\\', '/').label('document_path')
            )

            if search_value:
                    query = query.filter(
                    models.Agent.title_number.ilike(f"%{search_value}%") |
                    models.Agent.fullname.ilike(f"%{search_value}%") |
                    cast(models.Agent.nni, String).ilike(f"%{search_value}%") |
                    models.Agent.birth_place.ilike(f"%{search_value}%") |
                    models.Agent.category.ilike(f"%{search_value}%") |
                    models.Agent.telephone.ilike(f"%{search_value}%") 
                )
                    
            if category_filter and category_filter !="all":
                query = query.filter(models.Agent.category == category_filter)
                    

            total_records = query.count()
            agents = query.offset(start).limit(length).all()
                # Single COUNT query


            data = [{
                "id": agent.id,
                "title_number": agent.title_number,
                "nni": agent.nni,
                "fullname": agent.fullname,
                "date_of_birth":agent.date_of_birth.isoformat() if agent.date_of_birth else None,
                "birth_place": agent.birth_place,
                "category": agent.category,
                "telephone": agent.telephone,
                "document_path": agent.document_path
            } for agent in agents]


            return JSONResponse({
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": total_records,  # Use filtered count if search is applied
                "data": data
        })



        unique_category = db.query(models.Agent.category).distinct().all()
        category_list = [agent[0] for agent in unique_category] if unique_category else []

        # Single COUNT query
        counts = db.execute(text("""
            SELECT 
                (SELECT COUNT(*) FROM agents),
                (SELECT COUNT(*) FROM dossiers_non_numerise),
                (SELECT COUNT(*) FROM dossier_perdu)
        """)).fetchone()

        total_agents, total_non_numerise, total_perdu = counts

        all_total = total_agents + total_non_numerise + total_perdu

        return templates.TemplateResponse("index.html",
                                            {"request":request, 
                                            "body_class": "sb-nav-fixed", 
                                            "username":user.username, 
                                            "role":role, 
                                            "total_agents":total_agents, 
                                            "total_manquant":total_non_numerise, 
                                            "total_perdu":total_perdu, "all_total":all_total, 
                                            "columns": ["ID", "NUMERO DE TITRE", "NNI", "NOM COMPLET", 
                                                        "DATE DE NAISSANCE", "LIEU DE NAISSANCE", 
                                                        "CATEGORIE", "TELEPHONE", "NOM DE DOCUMENT"],

                                            "category_list": category_list
                                            })
    except SQLAlchemyError as e:
    
        raise HTTPException(status_code=500, detail="Une erreur produite dans la base des données.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quelque chose ne va pas! Ressayer encore!! ou {str(e)}")




@router.get("/admin/agents-table", response_class=HTMLResponse)
async def agents_table(request:Request,
          db:Session = Depends(get_db), 
          auth:str=Depends(verify_session),
          draw: Optional[int] = Query(1),  # DataTables parameter
          start: Optional[int] = Query(0),  # DataTables parameter (offset)
          length: Optional[int] = Query(10),  # DataTables parameter (page size)
          search_value: Optional[str] = Query(None),  
          category_filter: Optional[str] = Query(None),
          column_filter: Optional[str] = Query(None),
          column_value: Optional[str] = Query(None)
):
    

    user = db.query(models.User).filter(models.User.email == auth).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
        
    role = user.role
    categories = db.query(models.Category.name).all()
    categories= [category[0] for category in categories]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            query = db.query(
                models.Agent.id,
                models.Agent.title_number,
                models.Agent.nni,
                models.Agent.fullname,
                models.Agent.date_of_birth,
                models.Agent.birth_place,
                models.Agent.category,
                models.Agent.telephone,
                func.replace(models.Agent.document_path, '\\', '/').label('document_path')
            )

            if search_value:
                    query = query.filter(
                    models.Agent.title_number.ilike(f"%{search_value}%") |
                    # models.Agent.nni.contains(search_value) |
                    models.Agent.fullname.ilike(f"%{search_value}%") |
                    cast(models.Agent.nni, String).ilike(f"%{search_value}%") |
                    # models.Agent.date_of_birth.contains(search_value) |
                    models.Agent.birth_place.ilike(f"%{search_value}%") |
                    models.Agent.category.ilike(f"%{search_value}%") |
                    models.Agent.telephone.ilike(f"%{search_value}%") 
                )
                    

            if category_filter and category_filter !="all":
                query = query.filter(models.Agent.category == category_filter)

            

            if column_filter and column_value: 
                 try:

                    selected_columns = json.loads(column_filter)
                    if selected_columns:  # If any columns selected
                        filters = []
                        for col in selected_columns:
                            if hasattr(models.Agent, col):
                                column = getattr(models.Agent, col)
                                filters.append(column.ilike(f"%{column_value}%"))
                            
                        if filters:
                            query = query.filter(or_(*filters))
                 except json.JSONDecodeError:
                        
                        pass
                    

            total_records = query.count()    
            agents = query.offset(start).limit(length).all()
                # Single COUNT query

            data = [{
                "id": agent.id,
                "title_number": agent.title_number,
                "nni": agent.nni,
                "fullname": agent.fullname,
                "date_of_birth":agent.date_of_birth.isoformat() if agent.date_of_birth else None,
                "birth_place": agent.birth_place,
                "category": agent.category,
                "telephone": agent.telephone,
                "document_path": agent.document_path
            } for agent in agents]

            return JSONResponse({
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": total_records,  # Use filtered count if search is applied
                "data": data
        })

    unique_category = db.query(models.Agent.category).distinct().all()
    category_list = [agent[0] for agent in unique_category] if unique_category else []

    
    return templates.TemplateResponse("agents_table.html",
                                            {"request":request, 
                                            "body_class": "sb-nav-fixed", 
                                            "username":user.username, 
                                            "role":role, 
                                            "categories": categories,
                                            "columns": ["ID", "NUMERO DE TITRE", "NNI", "NOM COMPLET", 
                                                        "DATE DE NAISSANCE", "LIEU DE NAISSANCE", 
                                                        "CATEGORIE", "TELEPHONE", "NOM DE DOCUMENT"],


                                            "category_list": category_list
                                            })




@router.get("/admin/users-table", response_class=HTMLResponse)
async def users_table(request:Request,
          db:Session = Depends(get_db), 
          auth:str=Depends(verify_session),
          draw: Optional[int] = Query(1),  # DataTables parameter
          start: Optional[int] = Query(0),  # DataTables parameter (offset)
          length: Optional[int] = Query(10),  # DataTables parameter (page size)
          search_value: Optional[str] = Query(None)):

    admin_user = db.query(models.User).filter(models.User.email== auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user:
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs uniquement. vous n'avez pas droit 😊😊")
    
    role = admin_user.role

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            query = db.query(
                models.User.id,
                models.User.first_name,
                models.User.last_name,
                models.User.email,
                models.User.username,
                models.User.role,
                models.User.created_at

            )

            if search_value:
                    query = query.filter(
                    models.User.first_name.ilike(f"%{search_value}%") |
                    models.User.last_name.ilike(f"%{search_value}%") |
                    models.User.username.ilike(f"%{search_value}%") |
                    models.User.email.ilike(f"%{search_value}%")  
                )
                    
            total_records = query.count()    
            agents = query.offset(start).limit(length).all()
                # Single COUNT query

#  "date_of_birth":agent.date_of_birth.isoformat() if agent.date_of_birth else None,
            data = [{
                "id": agent.id,
                "first_name": agent.first_name,
                "last_name": agent.last_name,
                "email": agent.email,
                "username": agent.username,
                "role": agent.role,
                "created_at":agent.created_at.isoformat() if agent.created_at else None
                } for agent in agents]

            return JSONResponse({
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": total_records,  # Use filtered count if search is applied
                "data": data
        })

    return templates.TemplateResponse("users_table.html",
                                            {"request":request, 
                                            "body_class": "sb-nav-fixed", 
                                            "username":admin_user.username, 
                                            "role":role, 
                                            "columns": ["ID", "Prenom", "Nom",  "Email",  "Nom Utilisateur","Role", "Date de Creation"]
                                            })



@router.get("/admin/dossier-no-numeriser", response_class=HTMLResponse)
def get_dossier_no_numeriser(request:Request,
          db:Session = Depends(get_db), 
          auth:str=Depends(verify_session),
          draw: Optional[int] = Query(1),  # DataTables parameter
          start: Optional[int] = Query(0),  # DataTables parameter (offset)
          length: Optional[int] = Query(10),  # DataTables parameter (page size)
          search_value: Optional[str] = Query(None)):

    admin_user = db.query(models.User).filter(models.User.email== auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user:
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs uniquement. vous n'avez pas droit 😊😊")
    
    role = admin_user.role
    categories = db.query(models.Category.name).all()
    categories= [category[0] for category in categories]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            query = db.query(
                models.DossierNoNumeriser.id,
                models.DossierNoNumeriser.title_number,
                models.DossierNoNumeriser.fullname,
                models.DossierNoNumeriser.category
            )

            if search_value:
                    query = query.filter(
                    models.DossierNoNumeriser.title_number.ilike(f"%{search_value}%") |
                    models.DossierNoNumeriser.fullname.ilike(f"%{search_value}%") |
                    models.DossierNoNumeriser.category.ilike(f"%{search_value}%")
                )
                    
            total_records = query.count()    
            agents = query.offset(start).limit(length).all()
                # Single COUNT query

            data = [{
                "id": agent.id,
                "title_number": agent.title_number,
                "fullname": agent.fullname,
                "category": agent.category} for agent in agents]

            return JSONResponse({
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": total_records,  # Use filtered count if search is applied
                "data": data
        })

    return templates.TemplateResponse("dossier_manquant.html",
                                            {"request":request, 
                                            "body_class": "bg-light", 
                                            "username":admin_user.username, 
                                            "role":role, 
                                            "categories":categories,
                                            "columns": ["ID", "NUMERO DE TITRE",  "NOM COMPLET", "CATEGORIE"]
                                            })



@router.get("/admin/listes-dossiermanquant", response_class=HTMLResponse)
def manquants_details(request:Request,
          db:Session = Depends(get_db), 
          auth:str=Depends(verify_session),
          draw: Optional[int] = Query(1),  # DataTables parameter
          start: Optional[int] = Query(0),  # DataTables parameter (offset)
          length: Optional[int] = Query(10),  # DataTables parameter (page size)
          search_value: Optional[str] = Query(None), ):
    admin_user = db.query(models.User).filter(models.User.email== auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user:
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs uniquement. vous n'avez pas droit 😊😊")
    
    role = admin_user.role

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            query = db.query(
                models.DossierNoNumeriser.id,
                models.DossierNoNumeriser.title_number,
                models.DossierNoNumeriser.fullname,
                models.DossierNoNumeriser.category,
            )

            if search_value:
                    query = query.filter(
                    models.DossierNoNumeriser.title_number.ilike(f"%{search_value}%") |
                    models.DossierNoNumeriser.fullname.ilike(f"%{search_value}%") |
                    models.DossierNoNumeriser.category.ilike(f"%{search_value}%") 
                )
                    
            total_records = query.count()    
            agents = query.offset(start).limit(length).all()
                # Single COUNT query

            data = [{
                "id": agent.id,
                "title_number": agent.title_number,
                "fullname": agent.fullname,
                "category": agent.category} for agent in agents]

            return JSONResponse({
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": total_records,  # Use filtered count if search is applied
                "data": data
        })

    return templates.TemplateResponse("manquants_details.html",
                                            {"request":request, 
                                            "body_class": "bg-light", 
                                            "username":admin_user.username, 
                                            "role":role, 
                    
                                            "columns": ["ID", "NUMERO DE TITRE",  "NOM COMPLET", "CATEGORIE"]
                                            })



@router.get("/admin/dossier-perdu", response_class=HTMLResponse)
async def get_dossier_perdu(request:Request,
          db:Session = Depends(get_db), 
          auth:str=Depends(verify_session),
          draw: Optional[int] = Query(1),  # DataTables parameter
          start: Optional[int] = Query(0),  # DataTables parameter (offset)
          length: Optional[int] = Query(10),  # DataTables parameter (page size)
          search_value: Optional[str] = Query(None), ):
    admin_user = db.query(models.User).filter(models.User.email== auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user:
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs uniquement. vous n'avez pas droit 😊😊")
    
    role = admin_user.role

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            query = db.query(
                models.DossierPerdu.id,
                models.DossierPerdu.title_number,
                models.DossierPerdu.fullname,
                models.DossierPerdu.category,
                models.DossierPerdu.folder
            )

            if search_value:
                    query = query.filter(
                    models.DossierPerdu.title_number.ilike(f"%{search_value}%") |
                    models.DossierPerdu.fullname.ilike(f"%{search_value}%") |
                    models.DossierPerdu.category.ilike(f"%{search_value}%") |
                    models.DossierPerdu.folder.ilike(f"%{search_value}%")
                )
                    
            total_records = query.count()    
            agents = query.offset(start).limit(length).all()
                # Single COUNT query

            data = [{
                "id": agent.id,
                "title_number": agent.title_number,
                "fullname": agent.fullname,
                "category": agent.category,
                "folder":agent.folder
                } for agent in agents]

            return JSONResponse({
                "draw": draw,
                "recordsTotal": total_records,
                "recordsFiltered": total_records,  # Use filtered count if search is applied
                "data": data
        })

    return templates.TemplateResponse("dossier_perdu.html",
                                            {"request":request, 
                                            "body_class": "bg-light", 
                                            "username":admin_user.username, 
                                            "role":role, 
                    
                                            "columns": ["ID", "NUMERO DE TITRE",  "NOM COMPLET", "CATEGORIE","DOSSIER NUMERO"]
                                            })
   

@router.get("/admin/list-dossieregares", response_class=HTMLResponse)
def egares_details(request: Request, db:Session = Depends(get_db),auth:str=Depends(verify_session)):
    admin_user = db.query(models.User).filter(models.User.email== auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user:
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs uniquement. vous n'avez pas droit 😊😊")
    dossiers = db.query(models.DossierPerdu).all()
    data = {
        "columns": ["ID", "NUMERO DE TITRE", "Fullname", "Categorie","Dossier Numero"],  # Adjust based on your User model
        "rows": [[dossier.id, dossier.title_number ,dossier.fullname, dossier.category, dossier.folder] for dossier in dossiers]
    }

    return templates.TemplateResponse("egares_details.html", {"request": request, "body_class": "bg-light","data":data,"role":admin_user.role,"username":admin_user.username})



@router.get("/admin/dossier-manquant", response_class=HTMLResponse)
def get_dossier_manquant(request: Request, db:Session = Depends(get_db),auth:str=Depends(verify_session)):
    admin_user = db.query(models.User).filter(models.User.email== auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user:
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs uniquement. vous n'avez pas droit 😊😊")
    dossiers = db.query(models.DossierNoNumeriser).all()
    data = {
        "columns": ["ID", "NUMERO DE TITRE", "Nom Complet", "Categorie","Dossier Numero"],  # Adjust based on your User model
        "rows": [[dossier.id, dossier.title_number ,dossier.fullname, dossier.category, dossier.folder] for dossier in dossiers]
    }

    return templates.TemplateResponse("dossier_manquant.html", {"request": request, "body_class": "bg-light","data":data,"role":admin_user.role,"username":admin_user.username})


#================================================================


@router.get("/admin/agents-details", response_class=HTMLResponse)
async def agents_details(request: Request,db: Session = Depends(get_db),auth:str=Depends(verify_session)):

    user = db.query(models.User).filter(models.User.email == auth).first()
    # Check if the user exists and if their role is 'admin'
    if not user or user.role != 'admin':
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")
    
    agents = db.query(models.Agent).all()
    table_data = {
        "columns": ["ID", "NUMERO DE TITRE", "NNI", "NOM COMPLET", 
                    "DATE DE NAISSANCE", "LIEU DE NAISSANCE", 
                    "CATEGORIE",  "TELEPHONE","DOCUMENT"
                    ],  # Adjust based on your User model
        "rows": [[agent.id, agent.title_number, agent.nni, agent.fullname, 
                  agent.date_of_birth,agent.birth_place,agent.category, 
                  agent.telephone,
                   agent.document_path.replace("\\", "/")
                  ] 
                  for agent in agents]
    }
    return templates.TemplateResponse("agents_details.html", 
                                      {"request": request, 
                                       "body_class": "sb-nav-fixed", 
                                       "data":table_data,
                                       "role":user.role})


@router.get("/admin/register-user", response_class=HTMLResponse)
def register(request: Request, db:Session = Depends(get_db),auth:str=Depends(verify_session)):
    admin_user = db.query(models.User).filter(models.User.email== auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user or admin_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Accès interdit : Cette action est réservée aux administrateurs. Vous n'êtes pas autorisé à créer un utilisateur.")
    return templates.TemplateResponse("register.html", {"request": request, "body_class": "bg-light"})

@router.get("/admin/create-dossier-no-numeriser", response_class=HTMLResponse)
def create_dossier_no_numeriser(request: Request, db:Session = Depends(get_db),auth:str=Depends(verify_session)):
    admin_user = db.query(models.User).filter(models.User.email== auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user:
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs uniquement. vous n'avez pas droit de creer un utilisateur")
    
    categories = db.query(models.Category.name).all()
    categories= [category[0] for category in categories]
    return templates.TemplateResponse("create_dossier_manquant.html", {"request": request, "body_class": "bg-light", "categories": categories})



@router.get("/admin/create-category", response_class=HTMLResponse)
def create_category(request: Request, db:Session = Depends(get_db),auth:str=Depends(verify_session)):
    admin_user = db.query(models.User).filter(models.User.email== auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user:
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs uniquement. vous n'avez pas droit de creer un utilisateur")
    return templates.TemplateResponse("create_category.html", {"request": request, "body_class": "bg-light"})


@router.post('/admin/create-category',status_code=status.HTTP_201_CREATED, response_model=List[schemas.CategoryResponse])
async def create_category(request:Request, 
                 name:str=Form(...),
                 db:Session=Depends(get_db),
                 auth:str=Depends(verify_session)):
    
    admin_user = db.query(models.User).filter(models.User.email == auth).first()
    try:
        form_data = await request.form()
        error_message = None
        if not admin_user:
            raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs accrédités uniquement.")
        new_category = models.Category(name=name)
        db.add(new_category)
        db.commit()
        db.refresh(new_category)
        return templates.TemplateResponse(
            "create_category.html",
            {"request": request, "success_message": f"La catégorie {name} a été ajouté avec succès !"}
        )
    except IntegrityError as e:
            db.rollback()
            if "ix_name" in str(e.orig):
                error_message = "Un enregistrement avec ce NNI ou ce numéro de titre existe déjà. Merci de vérifier les informations et de réessayer."
            else:
                error_message = "Une erreur inattendue s'est produite. Veuillez réessayer plus tard."
 
    return templates.TemplateResponse(
            "create_category.html",
            {"request": request, "error_message": error_message, "form_data": form_data}
        )

@router.post('/admin/create-dossier-no-numeriser',status_code=status.HTTP_201_CREATED, response_model=List[schemas.DossierNoNumeriserResponse])
async def create_dossier_no_numeriser(request:Request, 
                 title_number:str=Form(...),
                 fullname:str=Form(...),
                 category:str=Form(...),
                 db:Session=Depends(get_db),
                 auth:str=Depends(verify_session)):
    
    admin_user = db.query(models.User).filter(models.User.email == auth).first()
    try:
        form_data = await request.form()
        error_message = None
        if not admin_user:
            raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs accrédités uniquement.")
        

        categories = db.query(models.Category.name).all()
        categories= [category[0] for category in categories]
        new_dossier = models.DossierNoNumeriser(
            title_number=title_number,
            fullname=fullname,
            category=category
        )
        db.add(new_dossier)
        db.commit()
        db.refresh(new_dossier)
        return templates.TemplateResponse(
            "create_dossier_manquant.html",
            {"request": request, "success_message": f"Le dossier manquant de numero de titre {title_number} a été ajouté avec succès !", "categories": categories}
        )
    except IntegrityError as e:
            db.rollback()
            if "ix_dossiers_non_numerise_title_number" in str(e.orig):
                error_message = "Un enregistrement avec ce numéro de titre existe déjà dans la table des dossiers manquants. Veuillez vérifier les informations et réessayer."
            else:
                error_message = "Une erreur inattendue s'est produite. Veuillez réessayer plus tard."
 
    return templates.TemplateResponse(
            "create_dossier_manquant.html",
            {"request": request, "error_message": error_message, "form_data": form_data,"categories": categories}
        )


#================================================================
@router.get("/admin/create-dossier-perdu", response_class=HTMLResponse)
def create_dossier_no_numeriser(request: Request, db:Session = Depends(get_db),auth:str=Depends(verify_session)):
    admin_user = db.query(models.User).filter(models.User.email== auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user:
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs uniquement. vous n'avez pas droit de creer un utilisateur")
    
    categories = db.query(models.Category.name).all()
    categories= [category[0] for category in categories]
    return templates.TemplateResponse("create_dossier_perdu.html", {"request": request, "body_class": "bg-light", "categories": categories})

#================================================================


@router.post('/admin/create-dossier-perdu',status_code=status.HTTP_201_CREATED, response_model=List[schemas.DossierPerduResponse])
async def create_dossier_perdu(request:Request, 
                 title_number:str=Form(...),
                 fullname:str=Form(...),
                 category:str=Form(...),
                 folder:str=Form(...),
                 db:Session=Depends(get_db),
                 auth:str=Depends(verify_session)):
    
    admin_user = db.query(models.User).filter(models.User.email == auth).first()
    try:
        form_data = await request.form()
        error_message = None
        if not admin_user:
            raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux utilisateurs accrédités uniquement.")
        
        categories = db.query(models.Category.name).all()
        categories= [category[0] for category in categories]
        new_dossier = models.DossierPerdu(
            title_number=title_number,
            fullname=fullname,
            category=category,
            folder=folder
        )
        db.add(new_dossier)
        db.commit()
        db.refresh(new_dossier)
        return templates.TemplateResponse(
            "create_dossier_perdu.html",
            {"request": request, "success_message": f"Le dossier égaré de {fullname} a été ajouté avec succès !", "categories": categories}
        )
    except IntegrityError as e:
            db.rollback()
            if "ix_dossier_perdu_title_number" in str(e.orig):
                error_message = "Un enregistrement avec ce numéro de titre existe déjà dans la table des dossiers égarés. Veuillez vérifier les informations et réessayer."
            else:
                error_message = "Une erreur inattendue s'est produite. Veuillez réessayer plus tard."
 
    return templates.TemplateResponse(
            "create_dossier_perdu.html",
            {"request": request, "error_message": error_message, "form_data": form_data, "categories": categories}
        )



@router.post('/admin/create-user', status_code=status.HTTP_201_CREATED, response_model=List[schemas.UserResponse])
async def create_user(request:Request,
                first_name:str = Form(...),
                last_name:str = Form(...),
                username:str = Form(...),
                email:str = Form(...),
                password:str = Form(...),
                gender:str = Form(...),
                role:str = Form(...),
                db:Session = Depends(get_db),
                auth:str=Depends(verify_session)
                ):

    
    try:
        
        admin_user = db.query(models.User).filter(models.User.email== auth).first()
    # Check if the user exists and if their role is 'admin'
        if not admin_user or admin_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement. vous n'avez pas droit de creer un utilisateur")
        form_data = await request.form()
        error_message = None
        hashed_pw = hash_password(password)
        new_user = models.User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            gender=gender,
            role=role,
            hashed_password=hashed_pw

        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "success_message": f"Vous avez créer avec succés l'utilisateurs d'email: {email}!"}
        )
    

    except IntegrityError as e:
            db.rollback()
            if "ix_users_email" in str(e.orig) or "ix_users_username" in str(e.orig):
                error_message = "Un enregistrement avec ce email ou ce Nom d'utilisateur existe déjà. Veuillez vérifier les données et réessayer."
            else:
                error_message = "Une erreur inattendue s'est produite. Veuillez réessayer plus tard."

    return templates.TemplateResponse(
            "register.html",
            {"request": request, "error_message": error_message, "form_data": form_data}
        )
       
    
@router.post('/admin/create-agent', status_code=status.HTTP_201_CREATED)
async def create_agent(request:Request,
                 nni:int=Form(...),
                 title_number:str=Form(...),
                 fullname:str=Form(...),
                 category:str=Form(...),
                 date_of_birth:datetime.date=Form(...),
                 birth_place:str=Form(...),
                 telephone:str=Form(...),
                 address:str=Form(...),
                 document: UploadFile = File(...),
                 profile:Optional[UploadFile] = File(None),
                 db:Session=Depends(get_db),
                 auth:str=Depends(verify_session)):
    
    
    try:
        admin_user = db.query(models.User).filter(models.User.email == auth).first()

        if not admin_user:
            raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")


        categories = db.query(models.Category.name).all()
        categories= [category[0] for category in categories]
        dossier_no_numeriser= db.query(models.DossierNoNumeriser).filter(models.DossierNoNumeriser.title_number==title_number).first()
        dossier_perdu = db.query(models.DossierPerdu).filter(models.DossierPerdu.title_number==title_number).first()
        message = f"Vous avez créer avec succés l'agent de NNI: {nni}!"
        
        if dossier_no_numeriser:
            error_message = f"L'agent avec Numéro de titre {title_number} existe déjà dans Dossier non numerisé."
            return templates.TemplateResponse("create_agent.html",  {"request":request,"error_message":error_message, "categories":categories})
        
        if dossier_perdu:
            error_message = f"L'agent avec Numéro de titre {title_number} existe déjà dans Dossier égaré ou perdu."
            return templates.TemplateResponse("create_agent.html",  {"request":request,"error_message":error_message, "categories":categories})
        form_data = await request.form()
        error_message = None
        file_path = f"{UPLOAD_DIR}/{document.filename}"
        with open(file_path, 'wb') as file:
            content = await document.read()
            file.write(content)


        if profile and profile.filename: 
            profile_image_path =f"{UPLOAD_PROFILE}/{profile.filename}"
            with open(profile_image_path, 'wb') as f:
                content = await profile.read()
                f.write(content)

        else:
           
            profile_image_path = f"{UPLOAD_PROFILE}/profile_default.png"
        
        new_agent = models.Agent(
                nni=nni, 
                title_number=title_number, 
                fullname=fullname,
                category=category,
                date_of_birth=date_of_birth,
                birth_place=birth_place,
                telephone=telephone,
                address=address,
                document_path = str(file_path),
                profile_path =str(profile_image_path) 
                )
        db.add(new_agent)

        log_entry = models.ActivityLog(
            user_id = admin_user.id,
            action = "Ajout de l'agent",
            details = f"{admin_user.username} a ajouté le dossier d'agent de: numéro de titre: {title_number},  nom complet: {fullname}, catégorie: {category}"
        )
        db.add(log_entry)
        db.commit()
        db.refresh(new_agent)
        return templates.TemplateResponse("create_agent.html",{"request": request, "success_message": message, "categories":categories})
    
    except IntegrityError as e:
            db.rollback()
            if "ix_agents_nni" in str(e.orig) or "ix_agents_title_number" in str(e.orig):
                error_message = "Un enregistrement avec ce NNI ou ce Numéro de titre existe déjà. Veuillez vérifier les données et réessayer."
            else:
                error_message = "Une erreur inattendue s'est produite. Veuillez réessayer plus tard."
 
    return templates.TemplateResponse("create_agent.html",{"request": request, "error_message": error_message, "form_data": form_data, "categories":categories})
        
   

@router.delete("/admin/delete-agent/{agent_id}", status_code=status.HTTP_200_OK)
async def delete_agent(request:Request,agent_id: int, db: Session = Depends(get_db),auth:str=Depends(verify_session)):


    admin_user = db.query(models.User).filter(models.User.email == auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user or admin_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Cet agent n'existe pas.")
    db.delete(agent)
    db.commit()
    return {"message": "Suppression de l'agent avec succés."}


#============================================================================

@router.delete("/admin/delete-perdu/{agent_id}", status_code=status.HTTP_200_OK)
async def delete_perdu(request:Request,agent_id: int, db: Session = Depends(get_db),auth:str=Depends(verify_session)):


    admin_user = db.query(models.User).filter(models.User.email == auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user or admin_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")
    dossier = db.query(models.DossierPerdu).filter(models.DossierPerdu.id == agent_id).first()
    if not dossier:
        raise HTTPException(status_code=404, detail="Cet agent n'existe pas.")
    db.delete(dossier)
    db.commit()
    return {"message": "Suppression de l'agent avec succés."}


@router.delete("/admin/delete-manquant/{agent_id}", status_code=status.HTTP_200_OK)
async def delete_manquant(request:Request,agent_id: int, db: Session = Depends(get_db),auth:str=Depends(verify_session)):


    admin_user = db.query(models.User).filter(models.User.email == auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user or admin_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")
    dossier = db.query(models.DossierNoNumeriser).filter(models.DossierNoNumeriser.id == agent_id).first()
    if not dossier:
        raise HTTPException(status_code=404, detail="Cet agent n'existe pas.")
    db.delete(dossier)
    db.commit()
    return {"message": "Suppression de l'agent avec succés."}


#============================================================================


@router.delete("/admin/delete-user/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(request:Request, user_id:int, db:Session = Depends(get_db),auth:str=Depends(verify_session)):

    admin_user = db.query(models.User).filter(models.User.email == auth).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user or admin_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")
    user = db.query(models.User).filter(models.User.id==user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable")
    db.delete(user)
    db.commit()
    return {"detail": f"Suppression de l'utilisateur avec succés."}



# Edit Agent section

@router.get("/admin/get-agent/{agent_id}")
async def get_agent(request:Request,agent_id: int, db: Session = Depends(get_db), auth:str=Depends(verify_session)):
    # Fetch the user from the database based on the username
    user = db.query(models.User).filter(models.User.email == auth).first()
    # Check if the user exists and if their role is 'admin'
    if not user or user.role != 'admin':
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent introuvable.")
    return {
        "id": agent.id,
        "nni": agent.nni,
        "title_number": agent.title_number,
        "fullname": agent.fullname,
        "date_of_birth": agent.date_of_birth,
        "birth_place": agent.birth_place,
        "category": agent.category,
        "address": agent.address,
        "telephone": agent.telephone,
        # "document": agent.document_path.replace("\\", "/")  # Replace backslashes with forward slashes for correct file path in browser.
        
    }



#============================================================================
@router.get("/admin/get-dossier-perdu/{agent_id}")
async def get_perdu(request:Request,agent_id: int, db: Session = Depends(get_db), auth:str=Depends(verify_session)):
    # Fetch the user from the database based on the username
    user = db.query(models.User).filter(models.User.email == auth).first()
    # Check if the user exists and if their role is 'admin'
    if not user or user.role != 'admin':
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")
    dossier = db.query(models.DossierPerdu).filter(models.DossierPerdu.id == agent_id).first()
    if not dossier:
        raise HTTPException(status_code=404, detail="Agent introuvable.")
    return {
        "id": dossier.id,
        "title_number": dossier.title_number,
        "fullname": dossier.fullname,
        "category": dossier.category,
        "folder": dossier.folder,
        
    }



@router.get("/admin/get-dossier-manquant/{agent_id}")
async def get_manquant(request:Request,agent_id: int, db: Session = Depends(get_db), auth:str=Depends(verify_session)):
    # Fetch the user from the database based on the username
    user = db.query(models.User).filter(models.User.email == auth).first()
    # Check if the user exists and if their role is 'admin'
    if not user or user.role != 'admin':
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")
    dossier = db.query(models.DossierNoNumeriser).filter(models.DossierNoNumeriser.id == agent_id).first()
    if not dossier:
        raise HTTPException(status_code=404, detail="Agent introuvable.")
    return {
        "id": dossier.id,
        "title_number": dossier.title_number,
        "fullname": dossier.fullname,
        "category": dossier.category,
       
        
    }


#============================================================================

@router.get("/admin/categories-data")
def get_categories_data(request:Request,db:Session=Depends(get_db), auth:str=Depends(verify_session)):
    query = text("""
        SELECT 
            category, COUNT(*) AS count 
        FROM 
            agents 
        GROUP BY 
            category;
    """)
    result = db.execute(query).fetchall()
    
    data = [{"category": row[0], "count": row[1]} for row in result]
    return {"data": data}


@router.get("/admin/categories-birth-data")
def get_categories_birth_data(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            category, 
            EXTRACT(YEAR FROM date_of_birth) AS birth_year,
            COUNT(*) AS count 
        FROM 
            agents 
        GROUP BY 
            category, birth_year;
    """)
    result = db.execute(query).fetchall()
    data = {}
    for row in result:
        category, birth_year, count = row
        if category not in data:
            data[category] = {}
        data[category][birth_year] = count
    return {"data": data}


@router.get("/admin/detail-agent/{agent_id}", response_class=HTMLResponse)
async def agent_details(request:Request,agent_id: int, db: Session = Depends(get_db), auth:str =Depends(verify_session)):
    try:
      
        admin_user = db.query(models.User).filter(models.User.email == auth).first()
        agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
        
        if not admin_user or admin_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")

        if not agent:
            raise HTTPException(status_code=404, detail="Cet agent n'existe pas dans la base de données.")
        agent_data =  {
            "id": agent.id,
            "nni": agent.nni,
            "title_number": agent.title_number,
            "fullname": agent.fullname,
            "date_of_birth": agent.date_of_birth,
            "birth_place": agent.birth_place,
            "category": agent.category,
            "address": agent.address,
            "telephone": agent.telephone,
            "document": agent.document_path.replace("\\", "/"),# Replace backslashes with forward slashes for correct file path in browser.
            "profile":agent.profile_path#.replace("\\", "/"),# Replace backslashes with forward slashes
            
        }

        return templates.TemplateResponse("agent_details.html", {"request": request, "agent": agent_data})
    
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=str(e)
        )



@router.put("/admin/edit-agent/{agent_id}")
async def edit_agent(
    request: Request,
    agent_id: int,
    nni: Optional[int] = Form(None),
    title_number: Optional[str] = Form(None),
    fullname: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    date_of_birth: datetime.date = Form(...),
    birth_place: Optional[str] = Form(None),
    telephone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    document: Optional[UploadFile] = File(None),
    profile: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    auth: str = Depends(verify_session),
):
    try:
        admin_user = db.query(models.User).filter(models.User.email == auth).first()

        if not admin_user or admin_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")

        agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
        if not agent:
            raise HTTPException(status_code=404, detail="Agent inexistant.")
        

        log_entry = models.ActivityLog(
            user_id = admin_user.id,
            action = "Modifier l'agent",
            details = f"{admin_user.username} a modifié le dossier d'agent: numéro de titre: {title_number},  nom complet: {fullname}, catégorie: {category}, date de naissance: {date_of_birth}, lieu de naissance: {birth_place}, téléphone: {telephone}, l'adresse: {address}"
        )
        db.add(log_entry)

        # Update agent details
        agent.nni = nni
        agent.title_number = title_number
        agent.fullname = fullname
        agent.date_of_birth = date_of_birth
        agent.birth_place = birth_place
        agent.category = category
        agent.telephone = telephone
        agent.address = address

        if document and document.filename:
            document_path = f"{UPLOAD_DIR}/{document.filename}"
            with open(document_path, "wb") as f:
                content = await document.read()
                f.write(content)
            agent.document_path = document_path.replace("\\", "/")

        if profile and profile.filename:
            profile_path = f"{UPLOAD_PROFILE}/{profile.filename}"
            with open(profile_path, "wb") as f:
                content = await profile.read()
                f.write(content)
            agent.profile_path = profile_path.replace("\\", "/")

        db.commit()
        db.refresh(agent)
        return {"message": "Mise à jour correcte!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Nous ne pouvons pas modifier cet agent. Contacter l'administrateur. {str(e)}"
        )
    



@router.get("/admin/activity-logs", response_model=List[schemas.ActivityLogResponse])
def get_activity_logs(request:Request,db: Session = Depends(get_db), auth: str = Depends(verify_session)):
    admin_user = db.query(models.User).filter(models.User.email == auth).first()
    if not admin_user or admin_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")

    # logs = db.query(models.ActivityLog).filter(models.ActivityLog.user_id == user_id).all()
    logs = db.query(models.ActivityLog).all()
    table_data = {
        "columns": ["ID", "User ID", "Action", "Details", "Timestamp"],  # Adjust based on your User model
        "rows": [[log.id,log.user_id, log.action, log.details , log.timestamp] for log in logs]}
  
    return  templates.TemplateResponse(
            "activity_logs.html",
            {"request": request, "data":table_data}
        )

# Edit perdu section:
@router.put("/admin/edit-perdu/{perdu_id}")
async def edit_perdu(
    request: Request,
    perdu_id: int,
    title_number: Optional[str] = Form(None),
    fullname: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    folder: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    auth: str = Depends(verify_session),
):
    try:
        admin_user = db.query(models.User).filter(models.User.email == auth).first()

        if not admin_user or admin_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")

        dossier = db.query(models.DossierPerdu).filter(models.DossierPerdu.id == perdu_id).first()
        if not dossier:
            raise HTTPException(status_code=404, detail="Agent inexistant.")
        

        log_entry = models.ActivityLog(
            user_id = admin_user.id,
            action = "Modifier l'agent",
            details = f"{admin_user.username} a modifié le dossier perdu: numéro titre: {title_number},  nom complet: {fullname}, catégorie: {category}"
        )
        db.add(log_entry)

        # Update agent details
        dossier.title_number = title_number
        dossier.fullname = fullname
        dossier.category = category
        dossier.folder = folder

        db.commit()
        db.refresh(dossier)
        return {"message": "Mise à jour correcte!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Nous ne pouvons pas modifier cet agent. Contacter l'administrateur. {str(e)}"
        )




@router.put("/admin/edit-manquant/{manquant_id}")
async def edit_manquant(
    request: Request,
    manquant_id: int,
    title_number: Optional[str] = Form(None),
    fullname: Optional[str] = Form(None),
    category: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    auth: str = Depends(verify_session),
):
    try:
        admin_user = db.query(models.User).filter(models.User.email == auth).first()

        if not admin_user or admin_user.role != 'admin':
            raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")

        dossier = db.query(models.DossierNoNumeriser).filter(models.DossierNoNumeriser.id == manquant_id).first()
        if not dossier:
            raise HTTPException(status_code=404, detail="Agent inexistant.")

        # Update agent details
        dossier.title_number = title_number
        dossier.fullname = fullname
        dossier.category = category
      

        db.commit()
        db.refresh(dossier)
        return {"message": "Mise à jour correcte!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Nous ne pouvons pas modifier cet agent. Contacter l'administrateur. {str(e)}"
        )


#================================================================




@router.get("/password", response_class=HTMLResponse)
def password(request: Request):
    return templates.TemplateResponse("password.html", {"request": request, "body_class": "bg-primary"})

@router.get("/charts", response_class=HTMLResponse)
def charts(request: Request):
    return templates.TemplateResponse("charts.html", {"request": request, "body_class": "sb-nav-fixed"})



@router.get("/admin/register-agent", response_class=HTMLResponse)
def register_agent(request: Request, db: Session = Depends(get_db),auth:str=Depends(verify_session)):
    user = db.query(models.User).filter(models.User.email == auth).first()
    # Check if the user exists and if their role is 'admin'
    categories = db.query(models.Category.name).all()
    categories= [category[0] for category in categories]
    if not user:
        raise HTTPException(status_code=403, detail="Accès interdit : Réservé aux administrateurs uniquement.")
    return templates.TemplateResponse("create_agent.html",{"request":request, "body_class": "sb-nav-fixed", "role": user.role, "username": user.username, "categories": categories})


@router.get("/light-nav", response_class=HTMLResponse)
async def light_nav(request: Request):
    return templates.TemplateResponse("layout-sidenav-light", {"request": request, "body_class": "sb-nav-fixed"})


@router.get("/layoutstatic", response_class=HTMLResponse)
async def layoutstatic(request: Request):
    return templates.TemplateResponse("layout-static.html", {"request": request, "body_class": ""})


@router.get("/401", response_class=HTMLResponse)
async def layout_error_401(request: Request):
    return templates.TemplateResponse("401.html", {"request": request, "body_class": ""})

@router.get("/404", response_class=HTMLResponse)
async def layout_error_404(request: Request):
    return templates.TemplateResponse("404.html", {"request": request, "body_class": ""})

@router.get("/500", response_class=HTMLResponse)
async def layout_error_500(request: Request):
    return templates.TemplateResponse("500.html", {"request": request, "body_class": ""})


@router.get('/{id}', response_model=schemas.UserCreate, status_code=status.HTTP_200_OK)
def get_one_user(id:int, db:Session =Depends(get_db)):
    id_user= db.query(models.User).filter(models.User.id==id).first()
    if id_user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"The user id:{id} you requested for does not exist")
    return id_user





