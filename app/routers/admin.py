import os
print("ADMIN_BOOTSTRAP_SECRET =", repr(os.getenv("ADMIN_BOOTSTRAP_SECRET")))
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.user import User
from app.auth.security import hash_password
from app.schemas.admin import AdminBootstrapIn, UserOut

router = APIRouter(prefix="/api/admin", tags=["admin"])

ADMIN_BOOTSTRAP_SECRET = os.getenv("ADMIN_BOOTSTRAP_SECRET", "").strip()

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s


# -------------------------
# 1) Create admin (bootstrap)
# -------------------------
@router.post("/bootstrap", response_model=UserOut)
async def bootstrap_admin(payload: AdminBootstrapIn, db: AsyncSession = Depends(get_db)):
    if not ADMIN_BOOTSTRAP_SECRET:
        raise HTTPException(
            status_code=500,
            detail="ADMIN_BOOTSTRAP_SECRET is not set (check .env + load_dotenv + restart backend)"
        )

    if payload.secret.strip() != ADMIN_BOOTSTRAP_SECRET:
        raise HTTPException(403, "Bad secret")

    if not payload.email and not payload.phone:
        raise HTTPException(400, "Provide email or phone")

    if payload.email:
        exists = await db.scalar(select(User).where(User.email == payload.email))
        if exists:
            raise HTTPException(409, "Email already used")

    if payload.phone:
        exists = await db.scalar(select(User).where(User.phone == payload.phone))
        if exists:
            raise HTTPException(409, "Phone already used")

    u = User(
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
        role="admin",
    )
    db.add(u)
    await db.commit()
    await db.refresh(u)

    return u


# -------------------------
# 2) Get all users
# -------------------------
@router.get("/users", response_model=list[UserOut])
async def list_users(db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).order_by(User.id.desc()))
    return res.scalars().all()


# -------------------------
# 3) Get user by id
# -------------------------
@router.get("/users/{user_id}", response_model=UserOut)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    u = await db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return u


# -------------------------
# 4) Delete user by id
# -------------------------
@router.delete("/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    u = await db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")

    await db.delete(u)
    await db.commit()
    return {"ok": True, "deleted_id": user_id}
