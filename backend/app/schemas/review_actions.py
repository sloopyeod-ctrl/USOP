from pydantic import BaseModel


class ReviewAction(BaseModel):
    reviewer: str
    notes: str | None = None