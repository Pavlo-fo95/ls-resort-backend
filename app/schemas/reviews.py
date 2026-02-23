from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime

Sentiment = Literal["positive", "neutral", "negative", "other"]
Status = Literal["pending", "published", "hidden"]

class ReviewCreate(BaseModel):
    author_name: str = Field(..., max_length=80)
    text: str = Field(..., min_length=3)
    rating: int = Field(..., ge=1, le=5)

class ReviewCreateFull(ReviewCreate):
    sentiment: Optional[Sentiment] = None
    status: Status = "published"
    is_featured: bool = False
    created_at: Optional[datetime] = None

class ReviewOut(BaseModel):
    id: int
    author_name: str
    text: str
    rating: int
    sentiment: Optional[Sentiment] = None
    status: Status
    is_featured: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class ReviewPatch(BaseModel):
    status: Optional[str] = None
    is_featured: Optional[bool] = None
    sentiment: Optional[Sentiment] = None

    model_config = {"from_attributes": True}