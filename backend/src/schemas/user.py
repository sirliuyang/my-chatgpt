# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserDto(BaseModel):
    id: Optional[int] = Field(None, description="用户ID")
    email: EmailStr = Field(..., description="邮箱地址")
    name: str = Field(..., min_length=1, max_length=100, description="用户名")


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="邮箱地址")
    name: str = Field(..., min_length=1, max_length=100, description="用户名")


class UserCreate(UserBase):
    email: EmailStr
    password: str = Field(..., min_length=6, description="明文密码")


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    password: Optional[str] = Field(None, min_length=6)


class UserInDB(UserBase):
    id: int
    hashed_password: str
    created_at: datetime

    class Config:
        from_attributes = True
