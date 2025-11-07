# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from fastapi import APIRouter
from src.api.v1.endpoints import chat, conversations

router = APIRouter()

router.include_router(chat.router, tags=["chat"])
router.include_router(conversations.router, tags=["conversations"])
