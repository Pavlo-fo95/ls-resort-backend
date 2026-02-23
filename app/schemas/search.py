from pydantic import BaseModel
from datetime import datetime

class SuggestItem(BaseModel):
    title: str
    route: str
    type: str  # intent | trending | recent | page
    score: float = 0.0

class SuggestResponse(BaseModel):
    q: str
    lang: str
    items: list[SuggestItem]
    trending: list[SuggestItem] = []

class SearchLogIn(BaseModel):
    query: str
    lang: str = "ua"
    session_id: str | None = None
    chosen_route: str | None = None
    chosen_item_id: int | None = None

class SearchLogOut(BaseModel):
    ok: bool
    id: int
    created_at: datetime

    model_config = {"from_attributes": True}