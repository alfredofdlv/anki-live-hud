import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from addon.settings import DEFAULTS, validated
from addon.state import RevisionGate
from addon.statistics import DailyStats, is_correct, read_daily, study_day_bounds


class DB:
    def __init__(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.execute(
            "create table revlog (id integer primary key, cid integer, ease integer, type integer)"
        )

    def all(self, sql, *args):
        return self.connection.execute(sql, args).fetchall()

    def add(self, id, ease, cid=1, type=1):
        self.connection.execute("insert into revlog values (?, ?, ?, ?)", (id, cid, ease, type))


@pytest.mark.parametrize(
    "rating,expected", [(0, False), (1, False), (2, True), (3, True), (4, True), (5, False)]
)
def test_classification(rating, expected):
    assert is_correct(rating) is expected


def test_aggregation_and_repeated_card_events():
    db = DB()
    for id, ease in enumerate([1, 2, 3, 4, 3], 100):
        db.add(id, ease, cid=1 if id < 104 else 2)
    result = read_daily(db, 100, 200)
    assert (result.reviews, result.correct, result.again, result.unique_cards) == (5, 4, 1, 2)
    assert (result.hard, result.good, result.easy) == (1, 2, 1)
    assert result.accuracy == 80
    assert result.last_rating == 3


def test_half_open_day_and_non_answer_entries():
    db = DB()
    db.add(99, 1)
    db.add(100, 2, type=0)
    db.add(101, 3, type=2)
    db.add(102, 4, type=3)
    db.add(103, 0)
    db.add(104, 3, type=4)
    db.add(105, 4, type=5)
    db.add(200, 1)
    stats = read_daily(db, 100, 200)
    assert stats.reviews == stats.correct == 3
    assert stats.accuracy == 100


def test_empty_day():
    stats = read_daily(DB(), 0, 10)
    assert stats == DailyStats()
    assert stats.accuracy is None
    assert stats.goal_progress(100) == 0
    assert stats.payload(100)["last_rating"] is None


@pytest.mark.parametrize(
    "reviews,goal,progress", [(0, 100, 0), (5, 10, 50), (15, 10, 100), (3, 0, 0), (2, -1, 0)]
)
def test_goal(reviews, goal, progress):
    assert DailyStats(good=reviews).goal_progress(goal) == progress


def test_undo_resynchronizes_from_source():
    db = DB()
    db.add(100, 1)
    db.add(101, 4)
    assert read_daily(db, 0, 200).accuracy == 50
    db.connection.execute("delete from revlog where id = 101")
    undone = read_daily(db, 0, 200)
    assert (undone.reviews, undone.correct, undone.last_rating) == (1, 0, 1)
    db.add(101, 4)
    assert read_daily(db, 0, 200).accuracy == 50


@pytest.mark.parametrize(
    "cutoff,hours", [("2026-03-29T04:00", 23), ("2026-10-25T04:00", 25), ("2026-06-12T04:00", 24)]
)
def test_study_day_rollover_and_dst(cutoff, hours):
    zone = ZoneInfo("Europe/Madrid")
    end = datetime.fromisoformat(cutoff).replace(tzinfo=zone)
    start_ms, end_ms = study_day_bounds(int(end.timestamp()), zone)
    assert (end_ms - start_ms) / 3600000 == hours
    start = datetime.fromtimestamp(start_ms / 1000, zone)
    assert start.hour == 4


def test_revision_gate_rejects_rapid_and_previous_profile_results():
    gate = RevisionGate()
    first = gate.request()
    latest = gate.request()
    assert not gate.accepts(first)
    assert gate.accepts(latest)
    gate.invalidate()
    assert not gate.accepts(latest)
    assert gate.accepts(gate.request())


@pytest.mark.parametrize("raw", [None, {}, [], "bad"])
def test_settings_missing(raw):
    assert validated(raw) == DEFAULTS


def test_settings_malformed_and_clamped():
    settings = validated(
        {
            "enabled": "false",
            "width": 10000,
            "daily_goal": -3,
            "theme": "invalid",
            "compact": True,
            "animations": False,
        }
    )
    assert settings["enabled"] is True
    assert settings["width"] == 480
    assert settings["daily_goal"] == 1
    assert settings["theme"] == "auto"
    assert settings["compact"] is True
    assert settings["animations"] is False
    assert validated({"width": True})["width"] == DEFAULTS["width"]
