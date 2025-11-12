# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
from typing import Optional, List
import bcrypt
from src.crud.crud_user import CRUDUser
from src.schemas.user import UserBase, UserCreate, UserUpdate, UserDto
from sqlalchemy.orm import Session


class UserService:
    """用户业务逻辑层 - Service模式"""

    def __init__(self, repository: CRUDUser):
        self.repo = repository

    @staticmethod
    def _hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    @staticmethod
    def _verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    def create_user(self, db: Session, user_data: UserCreate) -> Optional[UserBase]:
        if self.repo.email_exists(db, str(user_data.email)):
            raise ValueError("Email already registered")

        user_dict = user_data.model_dump()
        user_dict["hashed_password"] = self._hash_password(user_dict.pop("password"))

        user_id = self.repo.create(db, user_dict)
        if not user_id:
            raise RuntimeError("Failed to create user")

        return self.get_user(db, user_id)

    def authenticate_user(self, db: Session, email: str, password: str) -> Optional[UserDto]:
        user_data = self.repo.get_by_email(db, email=email)
        if not user_data or not self._verify_password(password, user_data["hashed_password"]):
            return None
        return UserDto(**user_data)

    def get_user(self, db: Session, user_id: int) -> Optional[UserBase]:
        user_data = self.repo.get_by_id(db, user_id)
        return UserBase(**user_data) if user_data else None

    def get_user_by_email(self, db: Session, email: str) -> Optional[UserBase]:
        user_data = self.repo.get_by_email(db, email=email)
        return UserBase(**user_data) if user_data else None

    def list_users(self, db: Session, skip: int = 0, limit: int = 100) -> List[UserBase]:
        users_data = self.repo.list_all(db, skip, limit)
        return [UserBase(**data) for data in users_data]

    def update_user(self, db: Session, user_id: int, user_data: UserUpdate) -> Optional[UserBase]:
        existing_user = self.repo.get_by_id(db, user_id)
        if not existing_user:
            raise ValueError("User not found")

        update_dict = user_data.model_dump(exclude_unset=True)
        if "email" in update_dict and update_dict["email"] != existing_user["email"]:
            if self.repo.email_exists(db, update_dict["email"], exclude_user_id=user_id):
                raise ValueError("Email already registered")

        if "password" in update_dict and update_dict["password"]:
            update_dict["hashed_password"] = self._hash_password(update_dict.pop("password"))

        if not update_dict:
            return UserBase(**existing_user)

        success = self.repo.update(db, user_id, update_dict)
        if not success:
            raise RuntimeError("Failed to update user")

        return self.get_user(db, user_id)

    def delete_user(self, db: Session, user_id: int) -> bool:
        if not self.repo.get_by_id(db, user_id):
            raise ValueError("User not found")
        return self.repo.delete(db, user_id)
