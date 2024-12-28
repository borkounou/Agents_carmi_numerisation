import secrets 
import hashlib
from fastapi import Request, HTTPException
import os
from starlette import status
from passlib.context import CryptContext

csrf_secret = os.getenv("CSRF_SECRET_KEY")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str)->str:
    return pwd_context.verify(plain_password, hashed_password)


def verify_session(request: Request):
    username = request.cookies.get("username")
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User session is invalid or expired"
        )
    return username 

def generate_csrf_token() -> str:
    token_data= f"{secrets.token_urlsafe(32)}{csrf_secret}"
    csrf_token = hashlib.sha256(token_data.encode()).hexdigest()
    return csrf_token


def get_csrf_token(request:Request):
    return request.cookies.get("csrf_token")


def https_url_for(request:Request, name:str, **path_params:any)->str:
    http_url = request.url_for(name, **path_params)
    https_url = str(http_url).replace("http", "https",1)

    return http_url