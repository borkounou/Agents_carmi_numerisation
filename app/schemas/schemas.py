from typing import List, Optional
from pydantic import BaseModel, Field
import datetime


class DossierPerduBase(BaseModel):
    title_number:str
    fullname:str
    category:str
    folder:str
    class Config:
        from_attributes = True

class DossierPerduCreate(DossierPerduBase):
    class Config:
        from_attributes = True 

class DossierPerduResponse(BaseModel):
    title_number:str
    fullname:str
    category:str
    folder:str


class DossierPerdu(DossierPerduCreate):
    id: int
    class Config:
        from_attributes = True



#----------------------------------------------------------------

class DossierNoNumeriserBase(BaseModel):
    title_number:str
    fullname:str
    category:str
    class Config:
        from_attributes = True

class DossierNoNumeriserCreate(DossierNoNumeriserBase):
    class Config:
        from_attributes = True 

class DossierNoNumeriserResponse(BaseModel):
    title_number:str
    fullname:str
    category:str


class DossierNoNumeriser(DossierNoNumeriserCreate):
    id: int
    class Config:
        from_attributes = True
class AgentBase(BaseModel):
    nni:int
    title_number:str
    fullname:str
    category:str
    date_of_birth:datetime.date
    birth_place:str
    telephone:str
    address:str
    profile_path:Optional[str] = "profiles/profile_default.png"
    document_path:str
    class Config:
        from_attributes = True


class AgentCreate(AgentBase):
    class Config:
        from_attributes = True 
   
class AgentResponse(BaseModel):
    nni:int
    title_number:str
    fullname:str
    category:str
    date_of_birth:datetime.date
    birth_place:str
    telephone:str
    address:str
    profile_path:Optional[str] = "profiles/profile_default.png"
    document_path:str
    


class Agent(AgentCreate):
    id: int
    class Config:
        from_attributes = True

class UserBase(BaseModel):
    first_name:str
    last_name:str
    username:str
    email:str
    gender:str
    role:Optional[str] ="user"
    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    first_name:str
    last_name:str
    username:str
    email:str
    gender:str
    role:str


class UserCreate(UserBase):
    password: str
    class Config:
        from_attributes = True 


class User(UserCreate):
    id: int
    class Config:
        from_attributes = True


