import sys
sys.path.append('./')
import os
from typing import List 
from fastapi import HTTPException, Depends,Request,Form, UploadFile, File
from sqlalchemy.orm import Session 
from starlette import status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from starlette.exceptions import HTTPException as StarletteHTTPException
from config.connection import get_db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import models.models as models
import schemas.schemas as schemas
import datetime
from fastapi import APIRouter
from config.connection import get_db
from config.config import https_url_for
from config.config import pwd_context, hash_password
from config.config import verify_session

# router  = APIRouter(prefix='/users', tags=['Users'])
router  = APIRouter()
templates = Jinja2Templates(directory="templates")


templates.env.globals["https_url_for"] = https_url_for

UPLOAD_DIR = "uploaded_files"  # Directory to save uploaded files
os.makedirs(UPLOAD_DIR, exist_ok=True)





@router.get("/")
def root():
    return RedirectResponse("/login")
@router.get("/login", response_class=HTMLResponse)
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "body_class": "bg-primary"})


@router.post("/login")
def login_user(request: Request, email:str=Form(...), password:str=Form(...), db:Session=Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user or not pwd_context.verify(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "body_class": "bg-primary", "error": "Invalid username or password"})
    
    response = RedirectResponse("/admin", status_code=303)
    response.set_cookie(key="username", value=user.username, httponly=True, )  # Set cookie for 1 hour
    return response


@router.get("/logout")
def logout():
    response = RedirectResponse("/login", status_code=303)
    response.delete_cookie(key="username")
    return response

@router.get('/admin', response_class=HTMLResponse)
def index(request:Request,db:Session = Depends(get_db), auth:str=Depends(verify_session)):
    try:
        username = request.cookies.get("username", "Guest")
        users = db.query(models.User).all()
        user = db.query(models.User).filter(models.User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        role = user.role
        agents = db.query(models.Agent).all()
        data = {
            "columns": ["ID", "NUMERO DE TITRE", "NNI", "NOM COMPLET", "DATE DE NAISSANCE", "LIEU DE NAISSANCE", "CATEGORIE", "TELEPHONE", "NOM DE DOCUMENT"],  # Adjust based on your User model
            "rows": [[agent.id, agent.title_number, agent.nni, agent.fullname, 
                    agent.date_of_birth,agent.birth_place,agent.category,agent.telephone, agent.document_path.replace("\\", "/")] for agent in agents]
        }
        
        return templates.TemplateResponse("index.html",{"request":request, "body_class": "sb-nav-fixed", "data":data, "username":username, "role":role})
    except SQLAlchemyError as e:
    
        raise HTTPException(status_code=500, detail="A database error occurred.")
    
    except Exception as e:
                # Log unexpected errors
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred.")
    


@router.get("/admin/users-table", response_class=HTMLResponse)
async def users_table(request: Request,db: Session = Depends(get_db),auth:str=Depends(verify_session)):
    username = request.cookies.get("username", None)

    # Fetch the user from the database based on the username
    user = db.query(models.User).filter(models.User.username == username).first()
    
    # Check if the user exists and if their role is 'admin'
    if not user or user.role != 'admin':
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only.")
    
    users = db.query(models.User).all()
    data = {
        "columns": ["ID", "First Name", "Last Name", "Username", "Email", "Gender", "Is active"],  # Adjust based on your User model
        "rows": [[user.id, user.first_name, user.last_name, user.username, user.email,user.gender,user.role] for user in users]
    }
    return templates.TemplateResponse("users_table.html", {"request": request, "body_class": "sb-nav-fixed", "data":data})




@router.get("/admin/agents-table", response_class=HTMLResponse)
async def agents_table(request: Request,db: Session = Depends(get_db),auth:str=Depends(verify_session)):
    username = request.cookies.get("username", None)

    if not username:
        raise HTTPException(status_code=403, detail="Access forbidden: Missing credentials.")

    admin_user = db.query(models.User).filter(models.User.username == username).first()
    # Check if the user exists and if their role is 'admin'
    if not admin_user or admin_user.role != 'admin':
        raise HTTPException(status_code=403, detail="Access forbidden: Admins only.")
    
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
    print(admin_user.role)
    return templates.TemplateResponse("agents_table.html", 
                                      {"request": request, 
                                       "body_class": "sb-nav-fixed", 
                                       "data":table_data,
                                       "role":admin_user.role})






@router.post('/admin/create-user', status_code=status.HTTP_201_CREATED, response_model=List[schemas.UserResponse])
def create_user(request:Request,
                first_name:str = Form(...),
                last_name:str = Form(...),
                username:str = Form(...),
                email:str = Form(...),
                password:str = Form(...),
                gender:str = Form(...),
                db:Session = Depends(get_db),
                auth:str=Depends(verify_session)):
    
    try:
        hashed_pw = hash_password(password)
        new_user = models.User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            gender=gender,
            role="user",
            hashed_password=hashed_pw

        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
       
        return  RedirectResponse("/admin", status_code=303)
    
    except IntegrityError as e:
        db.rollback()
        if "psycopg2.errors.UniqueViolation" in str(e):
            raise HTTPException(
                status_code=StarletteHTTPException.status_code, 
                detail="A record with this NNI or this Numero de titre already exists. Please verify the data and try again."
            )
    
        raise HTTPException(
            status_code=StarletteHTTPException.status_code, 
            detail="An unexpected error occurred. Please contact the administrator."

        )

    except Exception as e:
        raise HTTPException(
            status_code=StarletteHTTPException.status_code, 
            detail="We couldn't create a user for you."
        )
    


@router.post('/admin/create-agent', status_code=status.HTTP_201_CREATED, response_model=List[schemas.AgentResponse])
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
                 db:Session=Depends(get_db),
                 auth:str=Depends(verify_session)):
    form_data = await request.form()
    error_message = None
    file_path = f"{UPLOAD_DIR}/{document.filename}"#Path(UPLOAD_DIR) /document.filename
    with open(file_path, 'wb') as file:
        content = await document.read()
        file.write(content)
    try:
        # file_path = f"uploaded_file/{document.filename}"
        # with open(file_path, "wb") as file:
        #      file.write( await document.read())
        new_agent = models.Agent(
                nni=nni, 
                title_number=title_number, 
                fullname=fullname,
                category=category,
                date_of_birth=date_of_birth,
                birth_place=birth_place,
                telephone=telephone,
                address=address,
                document_path = str(file_path)
                )
        db.add(new_agent)
        db.commit()
        db.refresh(new_agent)
        return templates.TemplateResponse(
            "create_agent.html",
            {"request": request, "success_message": "Agent created successfully!"}
        )
    
    except IntegrityError as e:
            db.rollback()
            if "ix_agents_nni" in str(e.orig):
                error_message = "This NNI already exists. Please try a different one."
            else:
                error_message = "An unexpected error occurred. Please try again later."
 
    return templates.TemplateResponse(
            "create_agent.html",
            {"request": request, "error_message": error_message, "form_data": form_data}
        )
        
   

@router.delete("/admin/delete-agent/{agent_id}")
async def delete_agent(agent_id: int, db: Session = Depends(get_db),auth:str=Depends(verify_session)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found.")
    db.delete(agent)
    db.commit()
    return {"message": "Agent deleted successfully."}


@router.delete("/admin/delete-user/{username}", status_code=status.HTTP_200_OK)
def delete_user(username:int, db:Session = Depends(get_db),auth:str=Depends(verify_session)):
    user = db.query(models.User).filter(models.User.username==username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(user)
    db.commit()
    return {"detail": f"User {username} deleted successfully"}





# Edit Agent section

@router.get("/admin/get-agent/{agent_id}")
async def get_agent(agent_id: int, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found.")
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
    }


@router.put("/admin/edit-agent/{agent_id}")
async def edit_agent(agent_id: int, updated_data: dict, db: Session = Depends(get_db)):
    agent = db.query(models.Agent).filter(models.Agent.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found.")
    
    for key, value in updated_data.items():
        setattr(agent, key, value)
    db.commit()
    db.refresh(agent)
    return {"message": "Agent updated successfully."}



@router.get("/password", response_class=HTMLResponse)
def password(request: Request):
    return templates.TemplateResponse("password.html", {"request": request, "body_class": "bg-primary"})


@router.get("/register", response_class=HTMLResponse)
def register(request: Request,auth:str=Depends(verify_session)):
    return templates.TemplateResponse("register.html", {"request": request, "body_class": "bg-primary"})


@router.get("/register-agent", response_class=HTMLResponse)
def register_agent(request: Request,auth:str=Depends(verify_session)):
    return templates.TemplateResponse("create_agent.html",{"request":request, "body_class": "sb-nav-fixed"})


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




