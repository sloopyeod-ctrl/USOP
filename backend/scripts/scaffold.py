from pathlib import Path
import sys


BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"


def snake_case(name: str) -> str:
    result = ""
    for index, char in enumerate(name):
        if char.isupper() and index != 0:
            result += "_"
        result += char.lower()
    return result


def title_case(name: str) -> str:
    return name.replace("_", " ").title()


def write_file(path: Path, content: str) -> None:
    if path.exists():
        print(f"SKIP existing: {path}")
        return

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"CREATE: {path}")


def scaffold(entity_name: str) -> None:
    entity_snake = snake_case(entity_name)
    entity_title = title_case(entity_snake)
    entity_plural = f"{entity_snake}s"

    model_content = f'''from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class {entity_name}(BaseModel):
    __tablename__ = "{entity_plural}"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(100), nullable=False, default="Active")
'''
    schema_content = f'''from datetime import datetime

from pydantic import BaseModel


class {entity_name}Create(BaseModel):
    name: str
    status: str = "Active"


class {entity_name}Read({entity_name}Create):
    id: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

    class Config:
        from_attributes = True
'''
    repository_content = f'''from sqlalchemy.orm import Session

from app.models.{entity_snake} import {entity_name}
from app.schemas.{entity_snake} import {entity_name}Create


class {entity_name}Repository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: {entity_name}Create) -> {entity_name}:
        record = {entity_name}(**data.model_dump())
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def list_all(self) -> list[{entity_name}]:
        return self.db.query({entity_name}).filter({entity_name}.is_active == True).all()

    def get_by_id(self, record_id: str) -> {entity_name} | None:
        return self.db.query({entity_name}).filter({entity_name}.id == record_id).first()
'''
    service_content = f'''from sqlalchemy.orm import Session

from app.repositories.{entity_snake}_repository import {entity_name}Repository
from app.schemas.{entity_snake} import {entity_name}Create


class {entity_name}Service:
    def __init__(self, db: Session):
        self.repository = {entity_name}Repository(db)

    def create(self, data: {entity_name}Create):
        return self.repository.create(data)

    def list_all(self):
        return self.repository.list_all()

    def get_by_id(self, record_id: str):
        return self.repository.get_by_id(record_id)
'''
    api_content = f'''from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.{entity_snake} import {entity_name}Create, {entity_name}Read
from app.services.{entity_snake}_service import {entity_name}Service

router = APIRouter(
    prefix="/api/v1/{entity_plural.replace("_", "-")}",
    tags=["{entity_title}"],
)


@router.post("/", response_model={entity_name}Read)
def create_record(data: {entity_name}Create, db: Session = Depends(get_db)):
    service = {entity_name}Service(db)
    return service.create(data)


@router.get("/", response_model=list[{entity_name}Read])
def list_records(db: Session = Depends(get_db)):
    service = {entity_name}Service(db)
    return service.list_all()


@router.get("/{{record_id}}", response_model={entity_name}Read)
def get_record(record_id: str, db: Session = Depends(get_db)):
    service = {entity_name}Service(db)
    record = service.get_by_id(record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="{entity_title} not found")

    return record
'''

    write_file(APP_DIR / "models" / f"{entity_snake}.py", model_content)
    write_file(APP_DIR / "schemas" / f"{entity_snake}.py", schema_content)
    write_file(APP_DIR / "repositories" / f"{entity_snake}_repository.py", repository_content)
    write_file(APP_DIR / "services" / f"{entity_snake}_service.py", service_content)
    write_file(APP_DIR / "api" / "v1" / f"{entity_plural}.py", api_content)

    print()
    print("NEXT MANUAL STEPS:")
    print(f'1. Add import to migrations/env.py: from app.models.{entity_snake} import {entity_name}')
    print(f'2. Add router import to app/api/router.py: from app.api.v1.{entity_plural} import router as {entity_snake}_router')
    print(f'3. Add include_router to app/api/router.py: router.include_router({entity_snake}_router)')
    print(f'4. Run: alembic revision --autogenerate -m "Create {entity_plural} table"')
    print("5. Run: alembic upgrade head")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/scaffold.py EntityName")
        sys.exit(1)

    scaffold(sys.argv[1])