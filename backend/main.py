# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .v1 import router as api_router
from app.db import init_models, get_engine
import os

app = FastAPI(title="ChatGPT-Style App (FastAPI + pydantic-ai)")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup():
    # ensure tables exist / create async engine; migrations expected via alembic
    await init_models()


app.include_router(api_router, prefix="/api/v1")
