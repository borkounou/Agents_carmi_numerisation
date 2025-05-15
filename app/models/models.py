
from sqlalchemy import Column, Integer, String,TIMESTAMP,text,Date, ForeignKey,DateTime
from sqlalchemy.sql import func 

from sqlalchemy.orm import declarative_base, relationship




Base = declarative_base()
# from app.config.config import Base



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True,unique=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    gender = Column(String)
    role=Column(String, default="user")
    hashed_password = Column(String)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))
    activity_logs = relationship("ActivityLog", back_populates="user")



class Agent(Base):
    __tablename__ = "agents"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    nni = Column(Integer, unique=True, index=True, nullable=True, default=9999999999)
    title_number = Column(String, nullable=False, unique=True, index=True)
    fullname = Column(String, nullable=False, index=True)
    date_of_birth = Column(Date, nullable=False)
    birth_place = Column(String, nullable=False)
    category = Column(String,nullable=False, index=True)
    address = Column(String, default="")
    document_path = Column(String, nullable=False)  
    profile_path= Column(String, default="profiles/profile_default.png", nullable=True)
    telephone = Column(String, default="0000000000", nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))



class DossierNoNumeriser(Base):
    __tablename__ = "dossiers_non_numerise"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    title_number = Column(String, nullable=False, unique=True, index=True)
    fullname = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)



class DossierPerdu(Base):
    __tablename__ = "dossier_perdu"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    title_number = Column(String, nullable=False, unique=True, index=True)
    fullname = Column(String, nullable=False, index=True)
    category = Column(String, nullable=False, index=True)
    folder = Column(String, nullable=False, index=True)


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    action = Column(String, nullable=False)
    details = Column(String, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    user = relationship("User", back_populates="activity_logs")



class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
    name = Column(String, nullable=False, unique=True, index=True)
    






# class AgentNoControle(Base):
#     __tablename__ = "agents_no_controle"
#     id = Column(Integer, primary_key=True, index=True, autoincrement=True, unique=True)
#     nni = Column(Integer, unique=True, index=True, nullable=True, default=9999999999)
#     title_number = Column(String, nullable=False, unique=True, index=True)
#     fullname = Column(String, nullable=False, index=True)
#     date_of_birth = Column(Date, nullable=False)
#     birth_place = Column(String, nullable=False)
#     category = Column(String,nullable=False, index=True)
#     address = Column(String, default="")
#     document_path = Column(String, nullable=False)  
#     profile_path= Column(String, default="profiles/profile_default.png", nullable=True)
#     telephone = Column(String, default="0000000000", nullable=True)
#     created_at = Column(TIMESTAMP(timezone=True), server_default=text('now()'))









