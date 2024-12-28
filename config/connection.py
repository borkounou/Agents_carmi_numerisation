import sys
sys.path.append('./')
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models.models import Base
import os

DB_USER= os.getenv("DB_USER")
PASSWORD= os.getenv("DB_PASSWORD")
DATABASE= os.getenv("DB_DATABASE")
uri = f"postgresql+psycopg2://{DB_USER}:{PASSWORD}@localhost:5432/{DATABASE}"


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
    print("connection closed")

except Exception as e:
    print("Error connecting to database")