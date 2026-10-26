from types import SimpleNamespace

import pytest

pytest.importorskip("aqt")
from addon import hooks  # noqa: E402


def test_optional_feedback_failure_does_not_interrupt_answer_hook(monkeypatch):
    requests = []

    def broken_widget(parent):
        raise RuntimeError("simulated optional UI initialization failure")

    monkeypatch.setattr(hooks, "AnswerFeedback", broken_widget)
    controller = SimpleNamespace(
        active=lambda: True,
        config={"answer_feedback": True},
        feedback=None,
        mw=SimpleNamespace(web=None),
        request_refresh=requests.append,
    )
    hooks.HudController.on_answer(controller, None, None, 3)
    assert requests == ["answer"]
