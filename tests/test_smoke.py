from __future__ import annotations

from pathlib import Path

from hyperscore import CHORDS, Score, parse_rhythm
from hyperscore.core import NoteEvent, TimeSpan, bpm_to_ms
from hyperscore.io import MidiExporter
from hyperscore.rhythm import rhythm_ast_to_timespans
from hyperscore.theory import PitchClassSet


def test_smoke_basic_pipeline(tmp_path: Path) -> None:
    """
    Smoke test for the basic hyperscore pipeline.

    This test verifies that:
    - theory / rhythm / core / io modules work together
    - no unexpected exceptions are raised
    - a MIDI file can be successfully written to disk

    This test does NOT validate musical correctness.
    """

    # ----------------
    # theory
    # ----------------
    chord = CHORDS["major7"]

    pcs = PitchClassSet.from_seq([0, 4, 7, 11])
    assert pcs.jaccard(chord.intervals) == 1.0

    pitches = [n for n in range(60, 72) if n % 12 in chord.intervals]
    assert pitches, "no pitches selected from chord"

    pitch_iter = iter(pitches)

    # ----------------
    # rhythm
    # ----------------
    ast = parse_rhythm("1*4")
    total = int(bpm_to_ms(120, 1))
    spans = rhythm_ast_to_timespans(ast, total=total)

    assert sum(span.duration for span in spans) == total

    # ----------------
    # core / score
    # ----------------
    score: Score[NoteEvent] = Score()

    score.add_timespans(
        spans,
        factory=lambda span: NoteEvent(
            pitch=next(pitch_iter),
            velocity=100,
            span=span,
            channel=0,
        ),
    )

    events = list(score)
    assert len(events) == 4
    assert all(isinstance(event.span, TimeSpan) for event in events)

    # ----------------
    # io / midi export
    # ----------------
    out = tmp_path / "smoke.mid"

    exporter = MidiExporter()
    exporter.export(score, out)

    assert out.exists()
    assert out.stat().st_size > 0


def test_smoke_zipped_notes() -> None:
    """
    Smoke test for the zipped-parameter note creation API.

    This test ensures that:
    - list-like parameters are zipped correctly
    - the Score can generate multiple NoteEvent objects
      without raising errors
    """

    score: Score[NoteEvent] = Score()

    score.add(
        pitch=[60, 64, 67, 71],  # C major 7 chord tones
        velocity=[100],
        duration=[125],
        channel=[0],
        event_factory=lambda **kw: NoteEvent(
            pitch=kw["pitch"],
            velocity=kw["velocity"],
            span=kw["span"],
            channel=kw["channel"],
        ),
    )

    events = list(score)
    assert len(events) == 4
