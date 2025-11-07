# Gen AI Backend

## Overview

FastAPI backend for a ChatGPT-like Gen AI product.
Uses **PostgreSQL** for conversation persistence and **pydantic-ai**
with **DeepSeek LLM** for streaming chat.

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt

2. Config .env
3. Apply database migrations
   ```bash
   alembic init alembic # First time only
   alembic revision --autogenerate -m "your-change-comment"  # Run if you make changes to the models
   alembic upgrade head # Apply migrations
   ```
4. Run the server
