from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import ServiceItem
from app.schemas.services import ServicesResponse, ServiceItemOut

router = APIRouter(prefix="/api/services", tags=["services"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/", response_model=ServicesResponse)
async def get_services(db: AsyncSession = Depends(get_db)):
    q = (
        select(ServiceItem)
        .where(ServiceItem.is_active == True)  # noqa: E712
        .order_by(ServiceItem.type, ServiceItem.sort_order, ServiceItem.id)
    )
    res = await db.execute(q)
    items = res.scalars().all()

    def pack(t: str) -> list[ServiceItemOut]:
        return [ServiceItemOut.model_validate(x) for x in items if x.type == t]

    return {
        "massage": pack("massage"),
        "training": pack("training"),
        "herbs": pack("herbs"),
    }
