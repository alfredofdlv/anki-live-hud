"""Read-only answer runs and categorical recent history for the current study day."""

from __future__ import annotations

from collections.abc import Iterable

RECENT_LIMIT = 24
ROLLING_WINDOW = 5
RATED_WHERE = "id >= ? and id < ? and ease between 1 and 4 and type between 0 and 3"


def summarize_answers(answers: Iterable[int]) -> dict:
    ratings = [rating for rating in answers if rating in (1, 2, 3, 4)]
    current = best = good = 0
    rolling = []
    for index, rating in enumerate(ratings):
        current = current + 1 if rating in (2, 3, 4) else 0
        best = max(best, current)
        good = good + 1 if rating == 3 else 0
        window = ratings[max(0, index - ROLLING_WINDOW + 1) : index + 1]
        rolling.append(sum(value in (2, 3, 4) for value in window) / len(window) * 100)
    return {
        "streak": current,
        "best_streak": best,
        "good_streak": good,
        "recent": ratings[-RECENT_LIMIT:],
        "rolling_accuracy": rolling[-RECENT_LIMIT:],
        "rolling_window": ROLLING_WINDOW,
    }


def read_insights(db, start_ms: int, end_ms: int) -> dict:
    # Only this study day's indexed revlog range is read. Keep full-day runs exact;
    # truncating to the last 24 answers would silently cap the streak/record.
    rows = db.all(f"select ease from revlog where {RATED_WHERE} order by id", start_ms, end_ms)
    return summarize_answers(row[0] for row in rows)
