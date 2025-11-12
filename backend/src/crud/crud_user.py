# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging

from sqlalchemy.orm import Session
from sqlalchemy import select
from src.crud.base import CRUDBase
from src.models.user import User
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)


class CRUDUser(CRUDBase[User]):
    def get_by_email(self, db: Session, *, email: str) -> Optional[Dict[str, Any]]:
        try:
            query = select(self.model).where(self.model.email == email)
            result = db.execute(query)
            user = result.scalar_one_or_none()
            return self._to_dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by email {email}: {str(e)}")
            return None

    def email_exists(self, db: Session, email: str, exclude_user_id: Optional[int] = None) -> bool:
        try:
            query = select(self.model).where(self.model.email == email)
            if exclude_user_id:
                query = query.where(self.model.id != exclude_user_id)
            result = db.execute(query)
            return result.scalar_one_or_none() is not None
        except Exception as e:
            logger.error(f"Error checking if email {email} exists: {str(e)}")
            return False

    def get_by_id(self, db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        try:
            query = select(self.model).where(self.model.id == user_id)
            result = db.execute(query)
            user = result.scalar_one_or_none()
            return self._to_dict(user) if user else None
        except Exception as e:
            logger.error(f"Error getting user by id {user_id}: {str(e)}")
            return None

    def list_all(self, db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        try:
            query = select(self.model).offset(skip).limit(limit)
            result = db.execute(query)
            return [self._to_dict(row) for row in result.scalars().all()]
        except Exception as e:
            logger.error(f"Error listing users with skip {skip} and limit {limit}: {str(e)}")
            return []

    def create(self, db: Session, obj_in: Dict[str, Any]) -> int:
        try:
            obj = self.model(**obj_in)
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj.id
        except Exception as e:
            logger.error(f"Error creating user with data {obj_in}: {str(e)}")
            db.rollback()
            return 0

    def update(self, db: Session, user_id: int, update_data: Dict[str, Any]) -> bool:
        try:
            query = select(self.model).where(self.model.id == user_id)
            result = db.execute(query)
            user = result.scalar_one_or_none()
            if not user:
                return False
            for key, value in update_data.items():
                setattr(user, key, value)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error updating user {user_id} with data {update_data}: {str(e)}")
            db.rollback()
            return False

    def delete(self, db: Session, user_id: int) -> bool:
        try:
            query = select(self.model).where(self.model.id == user_id)
            result = db.execute(query)
            user = result.scalar_one_or_none()
            if not user:
                return False
            db.delete(user)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            db.rollback()
            return False

    @staticmethod
    def _to_dict(user: User) -> Dict[str, Any]:
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "hashed_password": user.hashed_password,
            "created_at": user.created_at
        }


# 全局实例
user_crud = CRUDUser(User)
