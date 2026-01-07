"""
timespan_pipeline.py

Demonstrates hyperscore's TimeSpanPipeline and time-domain transforms.

This example focuses on:
- composing multiple TimeSpan transforms
- separating rhythmic structure from temporal modification
- treating time as an explicit, transformable object
"""

from itertools import cycle
from pathlib import Path

from hyperscore import Score, parse_rhythm
from hyperscore.core import NoteEvent, bpm_to_ms
from hyperscore.core.time_pipeline import TimeSpanPipeline
from hyperscore.core.time_transforms import gate, probability, shift, stretch
from hyperscore.io import MidiExporter
from hyperscore.rhythm import rhythm_ast_to_timespans

# --------------------------------------------------
# configuration
# --------------------------------------------------

BPM = 110
BARS = 4
OUTPUT = Path("timespan_pipeline.mid")

# Change this string to explore different base rhythms
RHYTHM = "1*8"

# --------------------------------------------------
# base rhythm (structure only)
# --------------------------------------------------

ast = parse_rhythm(RHYTHM)

bar_ms = int(bpm_to_ms(BPM, 4))
total = bar_ms * BARS

base_spans = rhythm_ast_to_timespans(
    ast,
    total=total,
)

# --------------------------------------------------
# TimeSpan pipeline (temporal transformation)
# --------------------------------------------------

pipeline = TimeSpanPipeline().then(
    gate(0.6),  # shorten each span
    shift(30),  # delay slightly
    stretch(1.1),  # subtle time expansion
    probability(0.9),  # randomly drop some spans
)

processed_spans = pipeline.apply_all(base_spans)

# --------------------------------------------------
# pitch (simple, deterministic cycle)
# --------------------------------------------------

pitch_cycle = cycle([60, 62, 64, 67])

# --------------------------------------------------
# score
# --------------------------------------------------

score = Score()

score.add_timespans(
    processed_spans,
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
