from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import AsyncSessionLocal
from app.models import ContactMessage
from app.schemas.contact import ContactMessageIn, ContactMessageOut, ContactMessageUpdate

router = APIRouter(prefix="/api/contact", tags=["contact"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


@router.get("/info")
async def contact_info():
    return {
        "viber": {
            "iryna": "https://viber.com",
            "serhii": "https://viber.com",
            "group": "https://viber.com",
        },
        "email": "hello@lsresort.studio",
        "phone": "+38 (000) 000-00-00",
    }


@router.post("/send")
async def send_message(data: ContactMessageIn, db: AsyncSession = Depends(get_db)):
    msg = ContactMessage(**data.model_dump(), created_at=datetime.utcnow())
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return {"ok": True, "id": msg.id, "received_at": msg.created_at, "note": "Повідомлення отримано. Ми відповімо найближчим часом."}


@router.get("/all", response_model=list[ContactMessageOut])
async def get_all_messages(
    status: str | None = None,
    unread_only: bool = False,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    q = select(ContactMessage)
    if status:
        q = q.where(ContactMessage.status == status)
    if unread_only:
        q = q.where(ContactMessage.is_read == False)  # noqa: E712
    q = q.order_by(ContactMessage.created_at.desc()).limit(limit)

    res = await db.execute(q)
    return [ContactMessageOut.model_validate(x) for x in res.scalars().all()]


@router.get("/{message_id}", response_model=ContactMessageOut)
async def get_message(message_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ContactMessage).where(ContactMessage.id == message_id))
    msg = res.scalar_one_or_none()
    if not msg:
        raise HTTPException(404, "Message not found")
    return ContactMessageOut.model_validate(msg)


@router.patch("/{message_id}", response_model=ContactMessageOut)
async def update_message(message_id: int, patch: ContactMessageUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ContactMessage).where(ContactMessage.id == message_id))
    msg = res.scalar_one_or_none()
    if not msg:
        raise HTTPException(404, "Message not found")

    data = patch.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(msg, k, v)

    await db.commit()
    await db.refresh(msg)
    return ContactMessageOut.model_validate(msg)


@router.delete("/{message_id}")
async def delete_message(message_id: int, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(ContactMessage).where(ContactMessage.id == message_id))
    msg = res.scalar_one_or_none()
    if not msg:
        raise HTTPException(404, "Message not found")

    await db.delete(msg)
    await db.commit()
    return {"ok": True, "deleted_id": message_id}

