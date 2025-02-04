import secrets 
import hashlib
from fastapi import Request, HTTPException,status
import os
from datetime import datetime,timezone
import jwt # 
import time 
# import logging 
from typing import Optional 
# from starlette import status
from passlib.context import CryptContext

SECRET_KEY = os.getenv("SECRET_KEY")
SECRET_KEY="3573edbd14471f053794e5f1f0f3483fb31cbe31e4cf40afe198ee0f36cb7914"
ALGORITHM = "HS256"

# logging.basicConfig(level=logging.DEBUG)
csrf_secret = os.getenv("CSRF_SECRET_KEY")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain_password:str, hashed_password:str)->str:
    return pwd_context.verify(plain_password, hashed_password)

# Correct way to get the current UTC time as a timezone-aware datetime object
current_utc_time = datetime.now(timezone.utc)

def create_session_token(username:str, expires_in:int = 7200, ip:Optional[str]=None,user_agent:Optional[str]=None)->str:
    current_time = int(time.time())

    payload = {
        "sub":username,
        "iat":current_time,
        "exp":current_time + expires_in,
        "ip":ip,
        "user_agent":user_agent
    }

    return jwt.encode(payload,SECRET_KEY, algorithm=ALGORITHM)


def verify_session(request: Request):
    token = request.cookies.get("session_token")
    if not token:
        # logging.error("No session token found in cookies")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="La session utilisateur est invalide ou expirée."
        )
    try:
        # Decode and validate the token 
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"leeway":10})
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token de session invalide."
            )
        # Optional: Bind the session to the user's IP and User-Agent
        request_ip = request.client.host
        request_user_agent = request.headers.get("user-agent")
        # logging.debug(f"Token payload: {payload}")
        # logging.debug(f"Request IP: {request_ip}, Token IP: {payload.get('ip')}")

        if payload.get("ip") and payload["ip"] !=request_ip:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Le token de session n'est pas valide pour cette adresse IP."
            )
        if payload.get("user_agent") and payload["user_agent"]!=request_user_agent:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Le token de session n'est pas valide pour cet appareil."

            )
        
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Le token de session a expiré"
        )
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de session invalide."
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


