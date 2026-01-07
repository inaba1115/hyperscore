from __future__ import annotations

from hyperscore.core import NoteEvent, Score, TimeSpan

# ============================================================
# helpers
# ============================================================


def make_event(span: TimeSpan, *, pitch: int = 60) -> NoteEvent:
    """
    Minimal NoteEvent factory for tests.
    """
    return NoteEvent(
        pitch=pitch,
        velocity=100,
        span=span,
        channel=0,
    )


# ============================================================
# basic behavior
# ============================================================


def test_score_empty_iter():
    """
    Iterating over an empty score yields no events.
    """
    score: Score[NoteEvent] = Score()
    assert list(score) == []


def test_score_iteration_is_sorted_by_start():
    """
    Events must be iterated in ascending TimeSpan.start order,
    regardless of insertion order.
    """
    score: Score[NoteEvent] = Score()

    spans = [
        TimeSpan(start=20, duration=5),
        TimeSpan(start=0, duration=5),
        TimeSpan(start=10, duration=5),
    ]

    score.add_timespans(spans, factory=make_event)

    starts = [e.span.start for e in score]
    assert starts == [0, 10, 20]


def test_score_add_timespans_does_not_modify_spans():
    """
    Score must not modify TimeSpan objects passed to add_timespans.
    """
    score: Score[NoteEvent] = Score()

    span = TimeSpan(start=0, duration=10)
    score.add_timespans([span], factory=make_event)

    ev = next(iter(score))
    assert ev.span is span


# ============================================================
# cursor-based add (ZippedNotes path)
# ============================================================


def test_score_add_updates_cursor():
    """
    Score.add() must advance internal cursor by total duration.
    """
    score: Score[NoteEvent] = Score()

    score.add(
        pitch=[60, 62, 64],
        duration=[10, 20, 30],
        channel=[0],
        event_factory=lambda **kw: NoteEvent(**kw),
    )

    assert score.get_cursor() == 60


def test_score_add_respects_start_argument():
    """
    start argument should override the current cursor position.
    """
    score: Score[NoteEvent] = Score()

    score.add(
        pitch=[60],
        duration=[10],
        channel=[0],
        start=100,
        event_factory=lambda **kw: NoteEvent(**kw),
    )

    ev = next(iter(score))
    assert ev.span.start == 100
    assert score.get_cursor() == 110


# ============================================================
# events_between
# ============================================================


def test_events_between_start_only():
    """
    events_between(start, None) returns events whose start >= start.
    """
    score: Score[NoteEvent] = Score()

    spans = [
        TimeSpan(0, 5),
        TimeSpan(10, 5),
        TimeSpan(20, 5),
    ]
    score.add_timespans(spans, factory=make_event)

    events = score.events_between(start_ms=10)
    starts = [e.span.start for e in events]

    assert starts == [10, 20]


def test_events_between_start_and_end():
    """
    events_between(start, end) must return overlapping events only.
    """
    score: Score[NoteEvent] = Score()

    spans = [
        TimeSpan(0, 10),
        TimeSpan(10, 10),
        TimeSpan(20, 10),
    ]
    score.add_timespans(spans, factory=make_event)

    events = score.events_between(start_ms=5, end_ms=15)
    starts = [e.span.start for e in events]

    assert starts == [0, 10]
