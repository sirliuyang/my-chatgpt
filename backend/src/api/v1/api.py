# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from fastapi import APIRouter
from src.api.v1.endpoints import chat, conversations

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/api/v1", tags=["chat"])
api_router.include_router(conversations.router, prefix="/api/v1", tags=["conversations"])
