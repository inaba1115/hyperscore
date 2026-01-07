"""
rhythm_dsl.py

Demonstrates hyperscore's rhythm DSL and its expansion into concrete
TimeSpan sequences.

This example focuses on:
- structural rhythm description
- normalization and proportional expansion
- conversion into concrete time spans
"""

from itertools import cycle
from pathlib import Path

from hyperscore import Score, parse_rhythm
from hyperscore.core import NoteEvent, bpm_to_ms
from hyperscore.io import MidiExporter
from hyperscore.rhythm import rhythm_ast_to_timespans

# --------------------------------------------------
# configuration
# --------------------------------------------------

BPM = 120
BARS = 2
OUTPUT = Path("rhythm_dsl.mid")

# Change this string to explore the DSL
RHYTHM = "1 [1 2] * 2"

# --------------------------------------------------
# rhythm DSL
# --------------------------------------------------

ast = parse_rhythm(RHYTHM)

bar_ms = int(bpm_to_ms(BPM, 4))
total = bar_ms * BARS

spans = rhythm_ast_to_timespans(
    ast,
    total=total,
)

# --------------------------------------------------
# pitch (intentionally trivial)
# --------------------------------------------------

pitch_cycle = cycle([60, 62, 64, 67])

# --------------------------------------------------
# score
# --------------------------------------------------

score = Score()

score.add_timespans(
    spans,
    factory=lambda span: NoteEvent(
        pitch=next(pitch_cycle),
        velocity=100,
        span=span,
        channel=0,
    ),
)

# --------------------------------------------------
# output
# --------------------------------------------------

MidiExporter().export(score, OUTPUT)

print(f"Wrote {OUTPUT}")
