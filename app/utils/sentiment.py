from __future__ import annotations

def sentiment_from_rating(rating: int) -> str:
    try:
        r = int(rating)
    except Exception:
        return "neutral"

    if r >= 4: return "positive"
    if r == 3: return "neutral"
    return "negative"