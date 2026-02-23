from __future__ import annotations
from datetime import datetime, timedelta
import re

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_db
from app.models.models import SearchEvent
from app.schemas.search import SuggestResponse, SuggestItem, SearchLogIn, SearchLogOut

router = APIRouter(prefix="/api/search", tags=["search"])

def normalize_q(q: str) -> str:
    q = (q or "").strip().lower()
    q = re.sub(r"\s+", " ", q)
    q = re.sub(r"[^\w\s\-’']", "", q)
    return q[:200]

INTENTS = [
    {
        "title_ua": "Масаж",
        "title_ru": "Массаж",
        "route": "/massage",
        "keywords": ["масаж", "массаж", "обличчя", "лица", "плече", "плечо", "шия", "шея", "спина", "головний", "головная"],
    },
    {
        "title_ua": "Тренування",
        "title_ru": "Тренировки",
        "route": "/training",
        "keywords": ["тренування", "тренировка", "вправи", "упражнения", "йога", "постава", "осанка", "розтяжка", "растяжка"],
    },
    {
        "title_ua": "Трави та збори",
        "title_ru": "Травы и сборы",
        "route": "/herbs",
        "keywords": ["трави", "травы", "збір", "сбор", "чай", "сон", "стрес", "стресс", "нерви", "нервы", "імун", "иммун"],
    },
    {
        "title_ua": "Рекомендації",
        "title_ru": "Рекомендации",
        "route": "/recommendations",
        "keywords": ["рекомендації", "рекомендации", "поради", "советы", "біль", "боль"],
    },
    {
        "title_ua": "Відгуки",
        "title_ru": "Отзывы",
        "route": "/reviews",
        "keywords": ["відгуки", "отзывы", "оцінка", "оценка"],
    },
]

def intent_suggestions(q_norm: str, lang: str) -> list[SuggestItem]:
    items: list[SuggestItem] = []
    if not q_norm:
        return items
    for it in INTENTS:
        hits = sum(1 for kw in it["keywords"] if kw in q_norm)
        if hits:
            title = it["title_ua"] if lang == "ua" else it["title_ru"]
            items.append(SuggestItem(title=title, route=it["route"], type="intent", score=float(hits) * 10))
    return sorted(items, key=lambda x: x.score, reverse=True)[:8]

@router.get("/suggest", response_model=SuggestResponse)
async def suggest(
    q: str = Query("", max_length=200),
    lang: str = Query("ua", pattern="^(ua|ru)$"),
    db: AsyncSession = Depends(get_db),
):
    q_norm = normalize_q(q)

    items = intent_suggestions(q_norm, lang)

    # trending 7 days
    since = datetime.utcnow() - timedelta(days=7)
    stmt = (
        select(SearchEvent.query_norm, func.count(SearchEvent.id).label("cnt"))
        .where(SearchEvent.created_at >= since)
        .where(SearchEvent.lang == lang)
        .group_by(SearchEvent.query_norm)
        .order_by(desc("cnt"))
        .limit(8)
    )
    rows = (await db.execute(stmt)).all()
    trending = [
        SuggestItem(title=r[0], route=f"/search?q={r[0]}", type="trending", score=float(r[1]))
        for r in rows if r[0]
    ]

    if not q_norm:
        base = [
            SuggestItem(
                title=(it["title_ua"] if lang == "ua" else it["title_ru"]),
                route=it["route"],
                type="page",
                score=1.0,
            )
            for it in INTENTS
        ]
        return SuggestResponse(q=q, lang=lang, items=base, trending=trending)

    return SuggestResponse(q=q, lang=lang, items=items, trending=trending)

@router.post("/log", response_model=SearchLogOut)
async def log_search(
    payload: SearchLogIn,
    db: AsyncSession = Depends(get_db),
):
    q_norm = normalize_q(payload.query)

    event = SearchEvent(
        query=payload.query.strip()[:200],
        query_norm=q_norm,
        lang=payload.lang,
        session_id=payload.session_id,
        chosen_route=payload.chosen_route,
        chosen_item_id=payload.chosen_item_id,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return SearchLogOut(ok=True, id=event.id, created_at=event.created_at)