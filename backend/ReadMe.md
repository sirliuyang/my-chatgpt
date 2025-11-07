# Gen AI Backend

## Overview

FastAPI backend for a ChatGPT-like Gen AI product. Uses PostgreSQL for conversation persistence and pydantic-ai
framework for agentic AI with DeepSeek LLM for streaming chat.

## Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set up .env with your keys and DB URL (including DEEPSEEK_API_KEY).
3. Init Alembic: `alembic init alembic`
4. Generate migration: `alembic revision --autogenerate -m "init"`
5. Apply migration: `alembic upgrade head`
6. Run: `python src/main.py`

## Endpoints

- POST /api/v1/chat: Streaming chat (powered by pydantic-ai Agent)
- GET /api/v1/conversations: List conversations
- GET /api/v1/conversations/{id}: Fetch history
- POST /api/v1/conversations: Create new

Use X-API-Key header for auth.