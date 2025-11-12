# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
import logging
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.db.session import get_db
from src.schemas.user import UserCreate, UserBase
from src.common.auth_entity import LoginRequest, LoginResponse, RefreshTokenRequest, TokenResponse
from src.services import user_service
from src.services.auth_service import AuthService
from src.common.auth_bearer import get_current_user  # 添加当前用户依赖，如果需要保护某些路由

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/users", tags=["users"])

auth_service = AuthService(user_service)


@router.post("/register", response_model=UserBase, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate, db: Session = Depends(get_db)):
    """用户注册"""
    try:
        return user_service.create_user(db, user_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/login", response_model=LoginResponse)
def login_user(login_data: LoginRequest, db: Session = Depends(get_db)):
    """用户登录"""
    result = auth_service.login(db, str(login_data.email), login_data.password)
    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    access_token, gen_refresh_token, user_info = result

    expires_in = 7 * 24 * 60 * 60  # 转换为秒

    return LoginResponse(
        access_token=access_token,
        refresh_token=gen_refresh_token,
        token_type="bearer",
        expires_in=expires_in,
        user=user_info
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """刷新 access token"""
    new_access_token = auth_service.refresh_access_token(db, refresh_data.refresh_token)
    if not new_access_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer"
    )


@router.get("/me", response_model=UserBase)
def get_current_user_info(current_user: Dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户信息"""
    user = user_service.get_user(db, current_user["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout_user(current_user: Dict = Depends(get_current_user)):
    """用户登出（客户端需删除 token，此处可选实现黑名单）"""
    if current_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {"message": "Logged out successfully"}
