# GenAI Backend

FastAPI + PostgreSQL + Alembic + DeepSeek (OpenAI Compatible) Chat Backend

## 启动

1. Install dependencies: `pip install -r requirements.txt`
2. Config file: .env
3. Init db: `alembic upgrade head`
4. Start service: `uvicorn src.main:app --reload`

## API

- POST /api/v1/chat (流式聊天)
- GET /api/v1/conversations (对话列表)
- POST /api/v1/conversations (新建对话)
- GET /api/v1/conversations/{id} (获取对话详情)
