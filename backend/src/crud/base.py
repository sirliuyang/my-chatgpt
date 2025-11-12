# @Home    : www.pi-apple.com
# @Author  : Leon
# @Email   : pi.apple.lab@gmail.com
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import Generic, TypeVar, Type, List, Any

ModelType = TypeVar("ModelType")


class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model

    def get(self, db: Session, id: Any) -> ModelType | None:
        """
        Get a single record by primary key (id).
        Uses filter_by for type safety.
        """
        query = select(self.model).filter_by(id=id)
        result = db.execute(query)
        return result.scalar_one_or_none()

    def get_multi(self, db: Session) -> List[ModelType]:
        """Get all records as list[ModelType]."""
        query = select(self.model)
        result = db.execute(query)
        return list(result.scalars().all())  # 强制转为 List[ModelType]

    def create(self, db: Session, obj_in: dict) -> ModelType:
        """Create a new record."""
        obj = self.model(**obj_in)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj
