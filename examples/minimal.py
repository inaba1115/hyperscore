"""
minimal.py

Minimal, end-to-end example of the hyperscore workflow.

This script mirrors the "Minimal example" section in the README and
demonstrates the complete pipeline:

- selecting pitch material using theory objects
- describing rhythm structurally
- generating time-based events
- exporting the result to MIDI

For focused demonstrations of individual concepts, see:
- rhythm_dsl.py          (structural rhythm description)
- timespan_pipeline.py  (time-domain transformations)
"""

from hyperscore import CHORDS, Score, parse_rhythm
from hyperscore.core import NoteEvent, bpm_to_ms
from hyperscore.io import MidiExporter
from hyperscore.rhythm import rhythm_ast_to_timespans

# ----------------
# theory
# ----------------
chord = CHORDS["major7"]

pitches = [n for n in range(60, 72) if n % 12 in chord.intervals]
pitch_iter = iter(pitches)

# ----------------
# rhythm
# ----------------
ast = parse_rhythm("1*4")
total = int(bpm_to_ms(120, 1))
spans = rhythm_ast_to_timespans(ast, total=total)

# ----------------
# score
# ----------------
score = Score()

score.add_timespans(
    spans,
    factory=lambda span: NoteEvent(
        pitch=next(pitch_iter),
        velocity=100,
        span=span,
        channel=0,
    ),
)

# ----------------
# output
# ----------------
MidiExporter().export(score, "minimal.mid")
