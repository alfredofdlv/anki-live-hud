import pytest

from addon.feedback import feedback_details, impact_frame
from addon.settings import validated


def snapshot(reviews, goal=100, day=1):
    return {
        "reviews": reviews,
        "goal": goal,
        "day": day,
        "progress": min(100, reviews / goal * 100),
    }


def test_feedback_uses_real_daily_progress():
    result = feedback_details(snapshot(43, 60), snapshot(42, 60))
    assert result["summary"] == "43 / 60 daily reviews"
    assert result["progress_from"] == 70
    assert result["progress"] == pytest.approx(71.666666)
    assert not result["special"]


def test_goal_crossing_earns_medal_without_replaying_for_refresh():
    assert feedback_details(snapshot(100), snapshot(99))["headline"] == "DAILY GOAL COMPLETE"
    assert feedback_details(snapshot(101), snapshot(100))["headline"] == "REVIEW RECORDED"


def test_milestone_is_an_actual_review_count():
    assert feedback_details(snapshot(25), snapshot(24))["headline"] == "25 REVIEWS TODAY"


def test_goal_change_and_new_day_do_not_invent_a_goal_crossing():
    assert feedback_details(snapshot(51, 50), snapshot(50, 100))["headline"] == "REVIEW RECORDED"
    assert feedback_details(snapshot(1, 1, 2), snapshot(99))["headline"] == "REVIEW RECORDED"
    assert feedback_details(snapshot(1), None)["progress_from"] == 0


def test_impact_has_pop_hold_and_fade():
    assert impact_frame(0, 2400, True) == pytest.approx((0, 0.78))
    assert impact_frame(220, 2400, True)[1] > 1
    assert impact_frame(1000, 2400, True) == (1, 1)
    assert impact_frame(2250, 2400, True)[0] == 0.5
    assert impact_frame(2400, 2400, True)[0] == 0


def test_reduced_motion_is_static_without_hiding_feedback():
    assert impact_frame(0, 2400, False) == (1, 1)
    assert impact_frame(2399, 2400, False) == (1, 1)


def test_feedback_settings_migrate_existing_configs_and_validate():
    assert validated({"daily_goal": 60})["answer_feedback"] is True
    assert validated({"feedback_duration": -10})["feedback_duration"] == 1200
    assert validated({"feedback_duration": 99999})["feedback_duration"] == 5000
    assert validated({"feedback_duration": "forever"})["feedback_duration"] == 2400
    assert validated({"answer_feedback": False})["answer_feedback"] is False
