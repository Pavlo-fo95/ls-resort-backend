import os
import secrets
import httpx

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models.user import User
from app.schemas.auth import RegisterIn, LoginIn, TokenOut, MeOut, GoogleVerifyIn
from app.auth.security import hash_password, verify_password, create_access_token
from app.auth.deps import get_current_user
from app.schemas.auth import MeOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

async def get_db():
    async with AsyncSessionLocal() as s:
        yield s

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()

# ---------- email/phone register ----------
@router.post("/register", response_model=TokenOut)
async def register(payload: RegisterIn, db: AsyncSession = Depends(get_db)):
    if not payload.email and not payload.phone:
        raise HTTPException(400, "Provide email or phone")
    if len(payload.password) < 6:
        raise HTTPException(400, "Password too short")

    if payload.email:
        exists = await db.scalar(select(User).where(User.email == payload.email))
        if exists:
            raise HTTPException(409, "Email already used")

    if payload.phone:
        exists = await db.scalar(select(User).where(User.phone == payload.phone))
        if exists:
            raise HTTPException(409, "Phone already used")

    u = User(email=payload.email, phone=payload.phone, password_hash=hash_password(payload.password))
    db.add(u)
    await db.commit()
    await db.refresh(u)

    token = create_access_token(str(u.id))
    return {"access_token": token, "token_type": "bearer"}


# ---------- email/phone login ----------
@router.post("/login", response_model=TokenOut)
async def login(payload: LoginIn, db: AsyncSession = Depends(get_db)):
    q = select(User).where(or_(User.email == payload.login, User.phone == payload.login))
    u = await db.scalar(q)

    if not u or not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token(str(u.id))
    return {"access_token": token, "token_type": "bearer"}


# ---------- Google verify (ScanText-style) ----------
@router.post("/google/verify", response_model=TokenOut)
async def google_verify(payload: GoogleVerifyIn, db: AsyncSession = Depends(get_db)):
    if not payload.credential:
        raise HTTPException(400, "Missing credential")

    # 🔎 Проверка ID-токена через Google
    url = "https://oauth2.googleapis.com/tokeninfo"

    async with httpx.AsyncClient(timeout=15) as client:
        resp = await client.get(url, params={"id_token": payload.credential})

    if resp.status_code != 200:
        raise HTTPException(401, detail=f"Google token invalid: {resp.text}")

    data = resp.json()

    # ✅ защита: токен должен быть выдан твоему приложению
    GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "").strip()
    aud = data.get("aud")
    if GOOGLE_CLIENT_ID and aud != GOOGLE_CLIENT_ID:
        raise HTTPException(401, "Google token has wrong audience")

    email = data.get("email")
    sub = data.get("sub")
    aud = data.get("aud")  # 👈 ВАЖНО

    if not email or not sub:
        raise HTTPException(401, "Google token invalid (no email/sub)")

    # 🔐 Проверяем, что токен выдан именно нашему приложению
    if GOOGLE_CLIENT_ID and aud != GOOGLE_CLIENT_ID:
        raise HTTPException(401, "Google token has wrong audience")

    # 🔍 Ищем пользователя
    u = await db.scalar(select(User).where(User.email == email))

    if not u:
        # 🎯 создаем нового пользователя с безопасным случайным паролем
        random_pass = secrets.token_urlsafe(16)

        u = User(
            email=email,
            phone=None,
            password_hash=hash_password(random_pass),
            role="user"
        )

        db.add(u)
        await db.commit()
        await db.refresh(u)

    token = create_access_token(str(u.id))

    return {
        "access_token": token,
        "token_type": "bearer"
    }

# ---------- Users: GET all / GET by id / DELETE by id ----------
@router.get("/users")
async def users_all(db: AsyncSession = Depends(get_db)):
    rows = (await db.execute(select(User))).scalars().all()
    return [{"id": u.id, "email": u.email, "phone": u.phone} for u in rows]

@router.get("/users/{user_id}")
async def user_by_id(user_id: int, db: AsyncSession = Depends(get_db)):
    u = await db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    return {"id": u.id, "email": u.email, "phone": u.phone}

@router.delete("/users/{user_id}")
async def user_delete(user_id: int, db: AsyncSession = Depends(get_db)):
    u = await db.get(User, user_id)
    if not u:
        raise HTTPException(404, "User not found")
    await db.delete(u)
    await db.commit()
    return {"ok": True, "deleted_id": user_id}

@router.get("/me", response_model=MeOut)
async def me(u: User = Depends(get_current_user)):
    return {"id": u.id, "email": u.email, "phone": u.phone, "role": u.role}