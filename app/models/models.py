from __future__ import annotations

from datetime import datetime

from sqlalchemy import String, Text, DateTime, Boolean, Integer, text
from sqlalchemy import text as sa_text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str | None] = mapped_column(String, nullable=True)
    topic: Mapped[str | None] = mapped_column(String, nullable=True)
    message: Mapped[str] = mapped_column(String, nullable=False)
    preferred_contact: Mapped[str] = mapped_column(String, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, server_default=text("CURRENT_TIMESTAMP")
    )

    status: Mapped[str] = mapped_column(
        String, nullable=False, default="new", server_default=text("'new'")
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("0")
    )

class ServiceItem(Base):
    """
    Контент для фронта: услуги/направления.
    type: massage | training | herbs
    """
    __tablename__ = "service_items"

    id: Mapped[int] = mapped_column(primary_key=True)

    type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    duration_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_uah: Mapped[int | None] = mapped_column(Integer, nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="1",
    )

    sort_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True)

    author_name: Mapped[str] = mapped_column(String(80), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    rating: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default=sa_text("5"),
    )

    sentiment: Mapped[str | None] = mapped_column(String(20), nullable=True)

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default=sa_text("'pending'"),
    )

    is_featured: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=sa_text("0"),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
    )


class SearchEvent(Base):
    __tablename__ = "search_events"

    id: Mapped[int] = mapped_column(primary_key=True)

    query: Mapped[str] = mapped_column(String(200), nullable=False)
    query_norm: Mapped[str] = mapped_column(String(200), nullable=False, index=True)

    lang: Mapped[str] = mapped_column(String(5), nullable=False, server_default="ua")
    session_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    chosen_route: Mapped[str | None] = mapped_column(String(200), nullable=True)
    chosen_item_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )