import os
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal
from app.models import Review
from app.schemas.reviews import ReviewCreate, ReviewCreateFull, ReviewOut, ReviewPatch
from app.utils.sentiment import sentiment_from_rating
print("SENTIMENT FUNC SOURCE:", __file__)
print("CHECK:", sentiment_from_rating(3))


router = APIRouter(prefix="/api/reviews", tags=["reviews"])

ADMIN_TOKEN = os.getenv("ADMIN_TOKEN", "dev-token")


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


def require_admin(x_admin_token: str | None):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=401, detail="Not authorized")


# Публичный список (published)
@router.get("/", response_model=list[ReviewOut])
async def list_reviews(
    limit: int = Query(6, ge=1, le=100),
    only_published: bool = True,
    db: AsyncSession = Depends(get_db),
):
    q = select(Review)
    if only_published:
        q = q.where(Review.status == "published")
    q = q.order_by(Review.is_featured.desc(), Review.created_at.desc()).limit(limit)

    res = await db.execute(q)
    return [ReviewOut.model_validate(x) for x in res.scalars().all()]


# Все отзывы (dev/админка) — без фильтра
@router.get("/all", response_model=list[ReviewOut])
async def list_reviews_all(db: AsyncSession = Depends(get_db)):
    q = select(Review).order_by(Review.created_at.desc())
    res = await db.execute(q)
    return [ReviewOut.model_validate(x) for x in res.scalars().all()]


# Один отзыв по id
@router.get("/{review_id}", response_model=ReviewOut)
async def get_review(review_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.get(Review, review_id)
    if not r:
        raise HTTPException(404, "Review not found")
    return ReviewOut.model_validate(r)


# Публичное создание отзыва с сайта (всегда pending + авто-sentiment)
@router.post("/", response_model=ReviewOut)
async def create_review(data: ReviewCreate, db: AsyncSession = Depends(get_db)):
    r = Review(
        author_name=data.author_name,
        text=data.text,
        rating=data.rating,
        sentiment=sentiment_from_rating(data.rating),  # ✅ авто
        status="pending",
        is_featured=False,
        created_at=datetime.utcnow(),
    )
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return ReviewOut.model_validate(r)


# Админское создание “полного” отзыва (published/pending + sentiment optional)
@router.post("/full", response_model=ReviewOut)
async def create_review_full(
    data: ReviewCreateFull,
    db: AsyncSession = Depends(get_db),
    x_admin_token: str | None = Header(default=None),
):
    require_admin(x_admin_token)

    sentiment = data.sentiment or sentiment_from_rating(data.rating)

    r = Review(
        author_name=data.author_name,
        text=data.text,
        rating=data.rating,
        sentiment=sentiment,
        status=data.status,
        is_featured=data.is_featured,
        created_at=data.created_at or datetime.utcnow(),
    )
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return ReviewOut.model_validate(r)


# PATCH (админ)
@router.patch("/{review_id}", response_model=ReviewOut)
async def admin_patch_review(
    review_id: int,
    patch: ReviewPatch,
    db: AsyncSession = Depends(get_db),
    x_admin_token: str | None = Header(default=None),
):
    require_admin(x_admin_token)

    r = await db.get(Review, review_id)
    if not r:
        raise HTTPException(404, "Review not found")

    data = patch.model_dump(exclude_unset=True)

    # если админ поменял rating, а sentiment не указал — можно авто-обновить
    if "rating" in data and "sentiment" not in data:
        data["sentiment"] = sentiment_from_rating(data["rating"])

    for k, v in data.items():
        setattr(r, k, v)

    await db.commit()
    await db.refresh(r)
    return ReviewOut.model_validate(r)


# DELETE (админ)
@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    db: AsyncSession = Depends(get_db),
    x_admin_token: str | None = Header(default=None),
):
    require_admin(x_admin_token)

    r = await db.get(Review, review_id)
    if not r:
        raise HTTPException(404, "Review not found")
    await db.delete(r)
    await db.commit()
    return {"ok": True, "deleted_id": review_id}
