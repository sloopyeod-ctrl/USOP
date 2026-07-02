from typing import Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType]):
    def __init__(self, db: Session, model: type[ModelType]):
        self.db = db
        self.model = model

    def create(self, data: CreateSchemaType) -> ModelType:
        record = self.model(**data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_all(self) -> list[ModelType]:
        return self.db.query(self.model).filter(self.model.is_active == True).all()

    def get_by_id(self, record_id: str) -> ModelType | None:
        return self.db.query(self.model).filter(self.model.id == record_id).first()