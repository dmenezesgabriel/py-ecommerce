from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from src.config import Config

DATABASE_URL = "postgresql://"
DATABASE_URL += f"{Config.DATABASE_USER}:{Config.DATABASE_PASSWORD}"
DATABASE_URL += f"@{Config.DATABASE_HOST}:{Config.DATABASE_PORT}/"
DATABASE_URL += f"{Config.DATABASE_NAME}"

# SQLAlchemy setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
