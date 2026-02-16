from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Literal


class ContactMessageIn(BaseModel):
    name: str
    phone: str
    email: EmailStr | None = None
    topic: str | None = None
    message: str
    preferred_contact: str = "viber"


class ContactMessageOut(BaseModel):
    id: int
    name: str
    phone: str
    email: str | None
    topic: str | None
    message: str
    preferred_contact: str
    created_at: datetime
    status: str
    is_read: bool

    model_config = {"from_attributes": True}


class ContactMessageUpdate(BaseModel):
    is_read: bool | None = None
    status: Literal["new", "closed", "spam"] | None = None


class SendResponse(BaseModel):
    ok: bool
    id: int
    received_at: datetime
    note: str
