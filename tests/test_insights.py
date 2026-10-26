import sqlite3

import pytest

from addon.insights import read_insights, summarize_answers


@pytest.mark.parametrize(
    "ratings,streak,best,good",
    [
        ([], 0, 0, 0),
        ([1], 0, 0, 0),
        ([3, 3, 3], 3, 3, 3),
        ([3, 3, 2, 4], 4, 4, 0),
        ([3, 3, 1, 3], 1, 2, 1),
        ([3, 3, 3, 1], 0, 3, 0),
        ([0, 3, 5, None, 3], 2, 2, 2),
    ],
)
def test_answer_streak_definitions(ratings, streak, best, good):
    result = summarize_answers(ratings)
    assert (result["streak"], result["best_streak"], result["good_streak"]) == (streak, best, good)


def test_exact_full_day_runs_are_not_limited_by_chart_length():
    result = summarize_answers([3] * 80)
    assert result["streak"] == result["best_streak"] == result["good_streak"] == 80
    assert result["recent"] == [3] * 24
    assert result["rolling_accuracy"] == [100] * 24


def test_rolling_accuracy_uses_preceding_answers_beyond_visible_chart():
    result = summarize_answers([1] * 5 + [3] * 24)
    assert len(result["recent"]) == len(result["rolling_accuracy"]) == 24
    assert result["rolling_accuracy"][:5] == [20, 40, 60, 80, 100]


def test_recent_answers_are_categorical_and_chronological():
    result = summarize_answers([1, 2, 3, 4, 1, 3])
    assert result["recent"] == [1, 2, 3, 4, 1, 3]
    assert result["rolling_accuracy"] == pytest.approx([0, 50, 200 / 3, 75, 60, 80])


def test_read_history_filters_manual_rows_and_obeys_day_bounds():
    connection = sqlite3.connect(":memory:")
    connection.execute("create table revlog(id integer primary key, ease integer, type integer)")
    connection.executemany(
        "insert into revlog values (?,?,?)",
        [
            (99, 1, 1),
            (100, 3, 0),
            (101, 1, 4),
            (102, 1, 5),
            (103, 0, 1),
            (104, 2, 2),
            (105, 4, 3),
            (106, 3, 1),
            (200, 1, 1),
        ],
    )

    class DB:
        def all(self, sql, *args):
            return connection.execute(sql, args).fetchall()

    result = read_insights(DB(), 100, 200)
    assert result["recent"] == [3, 2, 4, 3]
    assert (result["streak"], result["best_streak"], result["good_streak"]) == (4, 4, 1)
    assert read_insights(DB(), 200, 300)["streak"] == 0
    assert read_insights(DB(), 201, 300)["recent"] == []
    connection.close()
