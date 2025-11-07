# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
