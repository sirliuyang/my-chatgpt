# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from src.core.config import settings

# 创建异步引擎
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# 使用 async_sessionmaker 替代 sessionmaker
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
