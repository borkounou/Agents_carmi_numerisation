import secrets 
import hashlib
from fastapi import Request, HTTPException,status
import os
from datetime import datetime, timedelta
import jwt # 
from typing import Optional 
# from starlette import status
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY="3573edbd14471f053794e5f1f0f3483fb31cbe31e4cf40afe198ee0f36cb7914"
ALGORITHM = "HS256"


csrf_secret = os.getenv("CSRF_SECRET_KEY")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str)->str:
    return pwd_context.verify(plain_password, hashed_password)


def create_session_token(username:str, expires_in:int = 3600, ip:Optional[str]=None,user_agent:Optional[str]=None)->str:
    payload = {
        "sub":username,
        "exp":datetime.utcnow()+timedelta(seconds=expires_in),
        "ip":ip,
        "user_agent":user_agent
    }

    return jwt.encode(payload,SECRET_KEY, algorithm=ALGORITHM)

def verify_session(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User session is invalid or expired"
        )
    try:
        # Decode and validate the token 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid session token"
            )
        # Optional: Bind the session to the user's IP and User-Agent
        request_ip = request.client.host
        request_user_agent = request.headers.get("user-agent")

        if payload.get("ip") and payload["ip"] !=request_ip:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session token is not valid for this IP address"
            )
        if payload.get("user_agent") and payload["user_agent"]!=request_user_agent:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session token is not valid for this device"

            )
        
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session token has expired"
        )
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid session token"
        )

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


