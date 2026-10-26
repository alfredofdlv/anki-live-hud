"""Presentation values derived from committed review data, never XP or scheduler state."""

from __future__ import annotations

MILESTONES = {10, 25, 50, 100, 250, 500, 1000}


def feedback_details(current: dict, previous: dict | None) -> dict:
    same_goal = bool(
        previous and previous["day"] == current["day"] and previous["goal"] == current["goal"]
    )
    start = previous["progress"] if same_goal else 0.0
    reached = bool(same_goal and previous["reviews"] < current["goal"] <= current["reviews"])
    milestone = current["reviews"] in MILESTONES
    run = current.get("insights", {}).get("streak", 0)
    previous_run = previous.get("insights", {}).get("streak", 0) if same_goal else 0
    streak_medal = bool(same_goal and run in {5, 10, 20, 50, 100} and run > previous_run)
    headline = "REVIEW RECORDED"
    if reached:
        headline = "DAILY GOAL COMPLETE"
    elif milestone:
        headline = f"{current['reviews']:,} REVIEWS TODAY"
    elif streak_medal:
        headline = f"{run} ANSWER STREAK"
    return {
        "headline": headline,
        "special": reached or milestone or streak_medal,
        "progress_from": start,
        "progress": current["progress"],
        "summary": f"{current['reviews']:,} / {current['goal']:,} daily reviews",
    }


def impact_frame(elapsed_ms: float, duration_ms: int, animated: bool) -> tuple[float, float]:
    """Opacity and pop scale for one interruptible presentation. No clock/state mutation."""
    if not animated:
        return 1.0, 1.0
    enter = min(1.0, max(0.0, elapsed_ms / 340))
    # Ease-out-back: a small overshoot makes a visible impact without screen shake.
    x = enter - 1
    scale = 0.78 + 0.22 * (1 + 2.70158 * x**3 + 1.70158 * x**2)
    opacity = min(1.0, max(0.0, elapsed_ms / 110), max(0.0, (duration_ms - elapsed_ms) / 300))
    return opacity, scale
