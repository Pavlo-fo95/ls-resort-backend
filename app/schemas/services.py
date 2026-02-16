from pydantic import BaseModel
from typing import Literal


ServiceType = Literal["massage", "training", "herbs"]


class ServiceItemOut(BaseModel):
    id: int
    type: ServiceType
    title: str
    description: str | None = None
    duration_min: int | None = None
    price_uah: int | None = None
    is_active: bool
    sort_order: int

    model_config = {"from_attributes": True}


class ServicesResponse(BaseModel):
    massage: list[ServiceItemOut]
    training: list[ServiceItemOut]
    herbs: list[ServiceItemOut]

