# Gen AI Backend

## Overview

FastAPI backend for a ChatGPT-like Gen AI product.
Uses **PostgreSQL** for conversation persistence and **pydantic-ai**
with **DeepSeek LLM** for streaming chat.

## Setup

Before setup, make sure you have a PostgreSQL database running and accessible.

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt

2. Config src/.env
   > Use the `config_template/.env.example` file as a template
3. Apply database migrations
   ```bash
   alembic init alembic # First time only, and config the env.py file
   alembic revision --autogenerate -m "your-change-comment"  # If not the first run, use this command
   alembic upgrade head # Apply migrations
   ```
4. Run the server
   ```shell
    uvicorn api_main:app --host 0.0.0.0 --port 7007 --workers 4
    ```

## Test

```shell
pytest -q
```