# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : 88978827@qq.com
# src/crud/base.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Generic, TypeVar, Type, List, Any

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> ModelType | None:
        """
        Get a single record by primary key (id).
        Uses filter_by for type safety.
        """
        query = select(self.model).filter_by(id=id)
        result = await db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(self, db: AsyncSession) -> List[ModelType]:
        """Get all records as list[ModelType]."""
        query = select(self.model)
        result = await db.execute(query)
        return list(result.scalars().all())  # 强制转为 List[ModelType]

    async def create(self, db: AsyncSession, obj_in: dict) -> ModelType:
        """Create a new record."""
        obj = self.model(**obj_in)
        db.add(obj)
        await db.commit()
        await db.refresh(obj)
        return obj
