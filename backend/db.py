# backend/db.py
from sqlmodel import SQLModel, create_engine, Session
from backend.config import DATABASE_URL
from backend.model import Customer, Company, Flight, Booking, Payment

# DATABASE ENGINE
engine = create_engine(DATABASE_URL, echo=True, pool_pre_ping=True)

# CREATE TABLES
def create_db_and_tables():
    print("Creating tables in the database...")
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")

# SESSION GENERATOR
def get_session():
    with Session(engine) as session:
        yield session

# RUN SCRIPT DIRECTLY
if __name__ == "__main__":
    create_db_and_tables()
