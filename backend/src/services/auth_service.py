# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging
from typing import Optional, Tuple, Dict, Any

from src.common.auth_handler import JWTHandler
from src.services.user_service import UserService
from sqlalchemy.orm import Session


class AuthService:
    """认证服务类"""

    def __init__(self, user_service: UserService):
        """
        初始化认证服务

        Args:
            user_service: 用户服务实例
        """
        self.user_service = user_service
        self.jwt_handler = JWTHandler()

    def login(self, db: Session, email: str, password: str) -> Optional[Tuple[str, str, Dict[str, Any]]]:
        """
        用户登录

        Args:
            db: 数据库会话
            email: 邮箱
            password: 密码

        Returns:
            (access_token, refresh_token, user_info) 或 None
        """
        # 使用UserService的authenticate_user方法验证用户
        user = self.user_service.authenticate_user(db, email, password)

        if not user:
            logging.warning(f"Login failed for email: {email}")
            return None

        # 准备token数据
        token_data = {
            "user_id": user.id,
            "email": user.email
        }

        # 生成tokens
        access_token = self.jwt_handler.create_access_token(token_data)
        refresh_token = self.jwt_handler.create_refresh_token(token_data)

        # 准备用户信息(不包含密码)
        user_info = {
            "id": user.id,
            "email": user.email,
            "name": user.name
        }

        logging.info(f"User {email} logged in successfully")
        return access_token, refresh_token, user_info

    def refresh_access_token(self, db: Session, refresh_token: str) -> Optional[str]:
        """
        使用refresh token获取新的access token

        Args:
            db: 数据库会话
            refresh_token: 刷新token

        Returns:
            新的access token或None
        """
        # 验证refresh token
        payload = self.jwt_handler.verify_token(refresh_token, token_type="refresh")

        if not payload:
            logging.warning("Invalid refresh token")
            return None

        # 验证用户是否仍然存在
        user_id = payload.get("user_id")
        user = self.user_service.get_user(db, user_id)

        if not user:
            logging.warning(f"User {user_id} not found during token refresh")
            return None

        # 生成新的access token
        token_data = {
            "user_id": user.id,
            "email": user.email
        }

        new_access_token = self.jwt_handler.create_access_token(token_data)
        logging.info(f"Access token refreshed for user: {user.email}")

        return new_access_token
