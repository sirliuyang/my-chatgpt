# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from fastapi import FastAPI
from src.api.v1.api import router as api_v1_router
from src.core.config import settings
from src.db.session import engine
from src.models import Base  # Import Base to create tables if needed

app = FastAPI(title="Gen AI Backend", version="1.0")

# Include API routers
app.include_router(api_v1_router, prefix="/api/v1")

# Optional: Create tables on startup (for development; use Alembic in production)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.create_all)  # Uncomment for auto-create (not recommended for prod)
        pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)