# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging

from pydantic import BaseModel, EmailStr, Field
from typing import Any, Dict

logger = logging.getLogger(__name__)


class LoginRequest(BaseModel):
    """登录请求模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=8, description="用户密码")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123"
            }
        }


class LoginResponse(BaseModel):
    """登录响应模型"""
    access_token: str = Field(..., description="访问token")
    refresh_token: str = Field(..., description="刷新token")
    token_type: str = Field(default="bearer", description="Token类型")
    expires_in: int = Field(..., description="过期时间(秒)")
    user: Dict[str, Any] = Field(..., description="用户信息")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800,
                "user": {
                    "id": 1,
                    "email": "user@example.com",
                    "name": "John Doe"
                }
            }
        }


class RefreshTokenRequest(BaseModel):
    """刷新token请求模型"""
    refresh_token: str = Field(..., description="刷新token")


class TokenResponse(BaseModel):
    """Token响应模型"""
    access_token: str
    token_type: str = "bearer"
