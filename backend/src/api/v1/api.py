# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
from fastapi import APIRouter
from src.api.v1.endpoints import chat_api, conversations_api, user_api, agui_agent, test_api

api_router = APIRouter()
api_router.include_router(test_api.router, prefix="/api/v1", tags=["test"])
api_router.include_router(chat_api.router, prefix="/api/v1", tags=["chat"])
api_router.include_router(conversations_api.router, prefix="/api/v1", tags=["conversations"])
api_router.include_router(user_api.router, prefix="/api/v1", tags=["users"])
api_router.include_router(agui_agent.router, prefix="/api/v1", tags=["agui"])
