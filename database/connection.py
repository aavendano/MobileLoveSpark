import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager

# Get database URL from environment variable with a default
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///temp.db")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for declarative models
Base = declarative_base()

@contextmanager
def get_db():
    """Get a database session using context manager"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()