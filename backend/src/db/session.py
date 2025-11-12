# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.common.config import settings

logger = logging.getLogger(__name__)
# 同步引擎
engine = create_engine(settings.DATABASE_URL, echo=True)

# 同步 Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# 依赖注入
def get_db():
    db = SessionLocal()
    try:
        try:
            yield db
        except Exception as e:
            logger.error(f"数据库操作出错: {str(e)}")
            db.rollback()
            raise
    finally:
        db.close()
