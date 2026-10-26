"""Read-only, bounded review-log aggregation, independent of the GUI."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, tzinfo
from typing import Protocol

from .insights import RATED_WHERE, read_insights

RATING_NAMES = {1: "Again", 2: "Hard", 3: "Good", 4: "Easy"}


class Database(Protocol):
    def all(self, sql: str, *args: object) -> list: ...


def is_correct(ease: int) -> bool:
    """MVP answer accuracy, deliberately distinct from True Retention."""
    return ease in (2, 3, 4)


def study_day_bounds(next_cutoff: int, zone: tzinfo | None = None) -> tuple[int, int]:
    """Return a half-open millisecond range from Anki's next study-day cutoff.

    Subtract a local calendar day, not 86400 seconds: DST days can be 23/25 hours.
    Anki provides the cutoff; we never assume the rollover is midnight.
    """
    end = datetime.fromtimestamp(next_cutoff, zone)
    start = end - timedelta(days=1)
    return int(start.timestamp() * 1000), next_cutoff * 1000


@dataclass(frozen=True)
class DailyStats:
    again: int = 0
    hard: int = 0
    good: int = 0
    easy: int = 0
    unique_cards: int = 0
    last_rating: int | None = None

    @property
    def reviews(self) -> int:
        return self.again + self.hard + self.good + self.easy

    @property
    def correct(self) -> int:
        return self.hard + self.good + self.easy

    @property
    def accuracy(self) -> float | None:
        return self.correct * 100 / self.reviews if self.reviews else None

    def goal_progress(self, goal: int) -> float:
        return min(100.0, self.reviews * 100 / goal) if goal > 0 else 0.0

    def payload(self, goal: int) -> dict:
        return {
            **asdict(self),
            "reviews": self.reviews,
            "correct": self.correct,
            "accuracy": self.accuracy,
            "goal": goal,
            "progress": self.goal_progress(goal),
        }


def read_daily(db: Database, start_ms: int, end_ms: int) -> DailyStats:
    # revlog.id is the millisecond primary key. Restrict every scan to this study day.
    # Types 0/1/2/3: learning/review/relearning/filtered. 4/5 are manual/rescheduled.
    predicate = RATED_WHERE
    rows = db.all(
        f"select ease, count(*) from revlog where {predicate} group by ease",
        start_ms,
        end_ms,
    )
    counts = {int(ease): int(count) for ease, count in rows}
    unique_rows = db.all(
        f"select count(distinct cid) from revlog where {predicate}", start_ms, end_ms
    )
    last = db.all(
        f"select ease from revlog where {predicate} order by id desc limit 1",
        start_ms,
        end_ms,
    )
    return DailyStats(
        again=counts.get(1, 0),
        hard=counts.get(2, 0),
        good=counts.get(3, 0),
        easy=counts.get(4, 0),
        unique_cards=int(unique_rows[0][0]) if unique_rows else 0,
        last_rating=int(last[0][0]) if last else None,
    )


def collection_snapshot(col, goal: int) -> dict:
    """Called only on Anki's serialized collection worker via QueryOp."""
    start, end = study_day_bounds(col.sched.day_cutoff)
    daily = read_daily(col.db, start, end)
    new, learning, review = col.sched.counts()
    return {
        **daily.payload(goal),
        "insights": read_insights(col.db, start, end),
        "day": start,
        "remaining": new + learning + review,
        "queue": {"new": new, "learning": learning, "review": review},
        "deck": col.decks.name(col.decks.get_current_id()),
    }
