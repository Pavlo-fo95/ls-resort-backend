from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


ReviewStatus = Literal["pending", "published", "hidden"]


class ReviewCreate(BaseModel):
    author_name: str = Field(min_length=2, max_length=80)
    text: str = Field(min_length=10, max_length=3000)
    rating: int | None = Field(default=None, ge=1, le=5)


class ReviewOut(BaseModel):
    id: int
    author_name: str
    text: str
    rating: int | None
    sentiment: str | None
    status: ReviewStatus
    is_featured: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewPatch(BaseModel):
    status: ReviewStatus | None = None
    is_featured: bool | None = None
