from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, DateTime, func, Integer, Boolean
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    email: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True, index=True)
    phone: Mapped[str | None] = mapped_column(String(40), unique=True, nullable=True, index=True)

    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    role: Mapped[str] = mapped_column(String(20), nullable=False, server_default="user")

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
