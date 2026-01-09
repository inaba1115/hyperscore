from __future__ import annotations

from hyperscore.core import NoteEvent, TimeSpan
from hyperscore.io.midi import MidiTimebase, note_events_to_midi_messages


def make_event(start: int, duration: int) -> NoteEvent:
    return NoteEvent(
        pitch=60,
        velocity=100,
        span=TimeSpan(start, duration),
        channel=0,
    )


def make_timebase() -> MidiTimebase:
    return MidiTimebase(
        ticks_per_beat=480,
        tempo_us_per_beat=500_000,
    )


def test_note_on_precedes_note_off_for_single_event():
    """
    For a single NoteEvent, note_on must not occur after note_off.
    """
    event = make_event(start=100, duration=50)
    timebase = make_timebase()

    msgs = note_events_to_midi_messages(
        [event],
        timebase=timebase,
    )

    assert len(msgs) == 2

    (tick_on, msg_on), (tick_off, msg_off) = msgs

    assert msg_on.type == "note_on"  # type: ignore[unresolved-attribute]
    assert msg_off.type == "note_off"  # type: ignore[unresolved-attribute]
    assert tick_on <= tick_off


def test_note_off_sorted_before_note_on_at_same_tick():
    """
    If note_on and note_off fall on the same tick,
    note_off must be ordered before note_on.
    """
    # duration small enough that both quantize to same tick
    event = make_event(start=100, duration=1)
    timebase = make_timebase()

    msgs = note_events_to_midi_messages(
        [event],
        timebase=timebase,
    )

    assert len(msgs) == 2

    (tick0, msg0), (tick1, msg1) = msgs

    assert tick0 == tick1
    assert msg0.type == "note_off"  # type: ignore[unresolved-attribute]
    assert msg1.type == "note_on"  # type: ignore[unresolved-attribute]


def test_multiple_events_independent_ordering():
    """
    note_on/off ordering must be preserved independently
    for each NoteEvent.
    """
    events = [
        make_event(start=0, duration=10),
        make_event(start=5, duration=10),
    ]
    timebase = make_timebase()

    msgs = note_events_to_midi_messages(
        events,
        timebase=timebase,
    )

    # Group messages by pitch (only one pitch here, so use ordering)
    ons = [(t, m) for t, m in msgs if m.type == "note_on"]  # type: ignore[unresolved-attribute]
    offs = [(t, m) for t, m in msgs if m.type == "note_off"]  # type: ignore[unresolved-attribute]

    # For each on/off pair, ordering must hold
    for (t_on, _), (t_off, _) in zip(ons, offs):
        assert t_on <= t_off
