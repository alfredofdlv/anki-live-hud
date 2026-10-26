"""Integration with actual Anki scheduler/review log; no GUI or personal collection."""

import pytest

pytest.importorskip("anki.collection")
from anki.cards import Card  # noqa: E402
from anki.collection import Collection  # noqa: E402
from anki.scheduler.v3 import CardAnswer  # noqa: E402

from addon.statistics import collection_snapshot  # noqa: E402

pytestmark = pytest.mark.anki


@pytest.fixture
def col(tmp_path):
    col = Collection(str(tmp_path / "collection.anki2"))
    for i in range(12):
        note = col.new_note(col.models.by_name("Basic"))
        note["Front"], note["Back"] = f"Question {i}", f"Answer {i}"
        col.add_note(note, 1)
    yield col
    col.close()


def answer(col, ease):
    queued = col.sched.get_queued_cards().cards[0]
    card = Card(col)
    card._load_from_backend_card(queued.card)
    card.start_timer()
    response = col.sched.build_answer(
        card=card,
        states=queued.states,
        rating=[CardAnswer.AGAIN, CardAnswer.HARD, CardAnswer.GOOD, CardAnswer.EASY][ease - 1],
    )
    col.sched.answer_card(response)


def test_all_ratings_and_actual_undo_redo(col):
    before = collection_snapshot(col, 4)
    assert before["reviews"] == 0
    assert before["remaining"] == sum(col.sched.counts())
    for count, ease in enumerate([1, 2, 3, 4], 1):
        answer(col, ease)
        stats = collection_snapshot(col, 4)
        assert stats["reviews"] == count
        assert stats["last_rating"] == ease
        assert stats["remaining"] == sum(col.sched.counts())
    assert stats["accuracy"] == 75
    assert stats["correct"] == 3
    assert stats["progress"] == 100
    col.undo()
    undone = collection_snapshot(col, 4)
    assert undone["reviews"] == 3
    assert undone["easy"] == 0
    assert undone["last_rating"] == 3
    col.redo()
    assert collection_snapshot(col, 4) == stats


def test_deck_switching_preserves_collection_day_totals(col):
    answer(col, 3)
    initial = collection_snapshot(col, 10)
    did = col.decks.id("Separate deck")
    col.decks.set_current(did)
    switched = collection_snapshot(col, 10)
    assert switched["reviews"] == initial["reviews"]
    assert switched["remaining"] == 0
    assert switched["deck"] == "Separate deck"
    col.decks.set_current(1)
    assert collection_snapshot(col, 10)["remaining"] == initial["remaining"]


def test_snapshot_is_read_only_and_survives_reopen(col):
    answer(col, 4)
    before = col.db.all("select * from revlog")
    cards = col.db.all("select * from cards order by id")
    snapshot = collection_snapshot(col, 10)
    assert col.db.all("select * from revlog") == before
    assert col.db.all("select * from cards order by id") == cards
    path = col.path
    col.close()
    col.reopen()
    assert col.path == path
    assert collection_snapshot(col, 10) == snapshot


def test_real_undo_redo_restores_streaks_and_chart(col):
    for rating in [3, 3, 2, 4, 1, 3, 3]:
        answer(col, rating)
    insight = collection_snapshot(col, 100)["insights"]
    assert (insight["streak"], insight["best_streak"], insight["good_streak"]) == (2, 4, 2)
    assert insight["recent"] == [3, 3, 2, 4, 1, 3, 3]
    col.undo()
    assert collection_snapshot(col, 100)["insights"]["good_streak"] == 1
    col.undo()
    assert collection_snapshot(col, 100)["insights"]["streak"] == 0
    col.undo()
    restored = collection_snapshot(col, 100)["insights"]
    assert restored["streak"] == restored["best_streak"] == 4
    assert restored["recent"] == [3, 3, 2, 4]
    col.redo()
    assert collection_snapshot(col, 100)["insights"]["streak"] == 0
