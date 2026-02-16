from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.database import AsyncSessionLocal
from app.models import Review
from app.schemas.reviews import ReviewCreate, ReviewOut, ReviewPatch

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Публичный список (как было)
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

# Все отзывы (для админки/отладки) — без limit и без фильтра
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

@router.post("/", response_model=ReviewOut)
async def create_review(data: ReviewCreate, db: AsyncSession = Depends(get_db)):
    r = Review(
        author_name=data.author_name,
        text=data.text,
        rating=data.rating,
        status="pending",
        is_featured=False,
        created_at=datetime.utcnow(),
    )
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return ReviewOut.model_validate(r)

@router.patch("/{review_id}", response_model=ReviewOut)
async def admin_patch_review(review_id: int, patch: ReviewPatch, db: AsyncSession = Depends(get_db)):
    r = await db.get(Review, review_id)
    if not r:
        raise HTTPException(404, "Review not found")

    data = patch.model_dump(exclude_unset=True)
    for k, v in data.items():
        setattr(r, k, v)

    await db.commit()
    await db.refresh(r)
    return ReviewOut.model_validate(r)

# Удаление
@router.delete("/{review_id}")
async def delete_review(review_id: int, db: AsyncSession = Depends(get_db)):
    r = await db.get(Review, review_id)
    if not r:
        raise HTTPException(404, "Review not found")
    await db.delete(r)
    await db.commit()
    return {"ok": True, "deleted_id": review_id}

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


@router.post("/", response_model=ReviewOut)
async def create_review(data: ReviewCreate, db: AsyncSession = Depends(get_db)):
    r = Review(
        author_name=data.author_name,
        text=data.text,
        rating=data.rating,
        status="pending",     # модерация
        is_featured=False,
        created_at=datetime.utcnow(),
    )
    db.add(r)
    await db.commit()
    await db.refresh(r)
    return ReviewOut.model_validate(r)



