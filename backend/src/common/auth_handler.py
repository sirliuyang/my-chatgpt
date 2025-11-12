# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import os
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
import jwt
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
load_dotenv()


class AuthConfig:
    """认证配置类"""
    SECRET_KEY: str = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '43200'))  # 30天
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '365'))  # 1年


class JWTHandler:
    """JWT token处理类"""

    @staticmethod
    def create_access_token(
            data: Dict[str, Any],
            expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        创建访问token

        Args:
            data: 要编码的数据(通常包含user_id, email等)
            expires_delta: 过期时间增量

        Returns:
            JWT token字符串
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(
                minutes=AuthConfig.ACCESS_TOKEN_EXPIRE_MINUTES
            )

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "access"
        })

        try:
            encoded_jwt = jwt.encode(
                to_encode,
                AuthConfig.SECRET_KEY,
                algorithm=AuthConfig.ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating access token: {e}")
            raise

    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """
        创建刷新token

        Args:
            data: 要编码的数据

        Returns:
            JWT refresh token字符串
        """
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            days=AuthConfig.REFRESH_TOKEN_EXPIRE_DAYS
        )

        to_encode.update({
            "exp": expire,
            "iat": datetime.now(timezone.utc),
            "type": "refresh"
        })

        try:
            encoded_jwt = jwt.encode(
                to_encode,
                AuthConfig.SECRET_KEY,
                algorithm=AuthConfig.ALGORITHM
            )
            return encoded_jwt
        except Exception as e:
            logger.error(f"Error creating refresh token: {e}")
            raise

    @staticmethod
    def decode_token(token: str, verify_expiration: bool = True) -> Optional[Dict[str, Any]]:
        """
        解码并验证token

        Args:
            token: JWT token字符串
            verify_expiration: 是否验证过期时间，默认为True

        Returns:
            解码后的数据,如果token无效返回None
        """
        try:
            options = {"verify_exp": verify_expiration}
            payload = jwt.decode(
                token,
                AuthConfig.SECRET_KEY,
                algorithms=[AuthConfig.ALGORITHM],
                options=options
            )
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            if verify_expiration:
                raise
            return None
        except jwt.PyJWTError as e:
            logger.error(f"JWT decode error: {e}")
            return None

    @staticmethod
    def verify_token(token: str, token_type: str = "access") -> Optional[Dict[str, Any]]:
        """
        验证token并检查类型

        Args:
            token: JWT token字符串
            token_type: token类型(access或refresh)

        Returns:
            验证通过返回payload,否则返回None
        """
        payload = JWTHandler.decode_token(token)

        if not payload:
            return None

        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type. Expected {token_type}, got {payload.get('type')}")
            return None

        return payload
