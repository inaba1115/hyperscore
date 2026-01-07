from __future__ import annotations

from hyperscore.core import NoteEvent, Score, TimeSpan

# ============================================================
# helpers
# ============================================================


def make_event(span: TimeSpan, *, pitch: int = 60) -> NoteEvent:
    return NoteEvent(
        pitch=pitch,
        velocity=100,
        span=span,
        channel=0,
    )


# ============================================================
# events_between_span
# ============================================================


def test_events_between_span_exact_overlap():
    """
    An event whose TimeSpan exactly overlaps the query span
    must be included.
    """
    score: Score[NoteEvent] = Score()

    span = TimeSpan(10, 10)
    score.add_timespans([span], factory=make_event)

    result = score.events_between_span(TimeSpan(10, 10))
    assert len(result) == 1
    assert result[0].span is span


def test_events_between_span_partial_overlap():
    """
    Partial overlap should include the event.
    """
    score: Score[NoteEvent] = Score()

    spans = [
        TimeSpan(0, 10),
        TimeSpan(20, 10),
    ]
    score.add_timespans(spans, factory=make_event)

    result = score.events_between_span(TimeSpan(5, 20))
    starts = [e.span.start for e in result]

    assert starts == [0, 20]


def test_events_between_span_no_overlap():
    """
    Non-overlapping events must not be included.
    """
    score: Score[NoteEvent] = Score()

    spans = [
        TimeSpan(0, 10),
        TimeSpan(20, 10),
    ]
    score.add_timespans(spans, factory=make_event)

    result = score.events_between_span(TimeSpan(10, 10))
    assert result == []


def test_events_between_span_sorted_and_early_exit():
    """
    events_between_span must rely on sorted order
    and stop scanning after span.end.
    (behavioral guarantee, not performance measurement)
    """
    score: Score[NoteEvent] = Score()

    spans = [
        TimeSpan(0, 5),
        TimeSpan(10, 5),
        TimeSpan(20, 5),
        TimeSpan(30, 5),
    ]
    score.add_timespans(spans, factory=make_event)

    result = score.events_between_span(TimeSpan(12, 3))
    starts = [e.span.start for e in result]

    assert starts == [10]


# ============================================================
# events_between (int-based API)
# ============================================================


def test_events_between_equivalent_to_span():
    """
    events_between(start, end) must behave equivalently
    to events_between_span(TimeSpan(start, end-start)).
    """
    score: Score[NoteEvent] = Score()

    spans = [
        TimeSpan(0, 10),
        TimeSpan(15, 10),
        TimeSpan(30, 10),
    ]
    score.add_timespans(spans, factory=make_event)

    a = score.events_between(start=5, end=20)
    b = score.events_between_span(TimeSpan(5, 15))

    assert [e.span.start for e in a] == [e.span.start for e in b]


def test_events_between_open_ended():
    """
    events_between(start, None) must return all events
    starting at or after start.
    """
    score: Score[NoteEvent] = Score()

    spans = [
        TimeSpan(0, 10),
        TimeSpan(10, 10),
        TimeSpan(20, 10),
    ]
    score.add_timespans(spans, factory=make_event)

    result = score.events_between(start=10)
    starts = [e.span.start for e in result]

    assert starts == [10, 20]


# ============================================================
# immutability & safety
# ============================================================


def test_events_between_does_not_modify_score():
    """
    Querying events must not mutate internal score state.
    """
    score: Score[NoteEvent] = Score()

    spans = [
        TimeSpan(0, 10),
        TimeSpan(20, 10),
    ]
    score.add_timespans(spans, factory=make_event)

    _ = score.events_between_span(TimeSpan(0, 30))

    # Second iteration should be identical
    starts = [e.span.start for e in score]
    assert starts == [0, 20]
