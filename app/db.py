from sqlmodel import SQLModel, create_engine, Session
import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./barsight.db")
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})
def init_db():
    SQLModel.metadata.create_all(engine)
def get_session():
    return Session(engine)