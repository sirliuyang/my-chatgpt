# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from fastapi import FastAPI
from src.db import init_models
from src.routes import chat, conversations

app = FastAPI(title="ChatGPT-Style FastAPI Backend")

@app.on_event("startup")
def on_startup():
    init_models()

app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat"])
app.include_router(conversations.router, prefix="/api/v1/conversations", tags=["Conversations"])
