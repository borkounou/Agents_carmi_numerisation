import sys
sys.path.append('./')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base
import os

DB_USER= os.getenv("POSTGRES_USER")
DB_PASSWORD= os.getenv("POSTGRES_PASSWORD")
DB_BASE= os.getenv("POSTGRES_DB")
DB_HOST= os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

uri = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_BASE}"
uri = "postgresql+psycopg2://postgres:Borkounou%40123@localhost:5432/mahrasoft"
engine = create_engine(uri)
Base.metadata.create_all(bind=engine)

session = sessionmaker(bind=engine, autoflush=True)

def get_db():
    db_session = session()
    try:
        yield db_session
    finally:
        db_session.close()


try: 
    connection = engine.connect()
    connection.close()
    print("connection successfully established")
 
except Exception as e:
    print("Error connecting to database")