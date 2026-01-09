"""
timespan_pipeline.py

Demonstrates hyperscore v0.2.0 TimeSpanPipeline.

This example highlights:
- TimeSpanPipeline as a generative structure (1 → N)
- Separation of rhythmic structure and temporal transformation
- TimeSpan as an explicit, immutable object
"""

from itertools import cycle
from pathlib import Path

from hyperscore import Score, parse_rhythm
from hyperscore.core import (
    NoteEvent,
    TimeSpanPipeline,
    bpm_to_ms,
    duplicate,
    probability,
    shift,
    split_even,
    stretch,
)
from hyperscore.io import MidiExporter
from hyperscore.rhythm import rhythm_ast_to_timespans

# --------------------------------------------------
# configuration
# --------------------------------------------------

BPM = 110
BARS = 4
OUTPUT = Path("timespan_pipeline.mid")

# Change this string to explore different base rhythms
RHYTHM = "1*4"

# --------------------------------------------------
# base rhythm (structure only)
# --------------------------------------------------

# Parse rhythm grammar into a structural AST
ast = parse_rhythm(RHYTHM)

bar_ms = int(bpm_to_ms(BPM, 4))
total = bar_ms * BARS

# Generate base TimeSpans (pure structure, no pitch)
base_spans = rhythm_ast_to_timespans(
    ast,
    total=total,
)

# --------------------------------------------------
# TimeSpan pipeline (generative transformation)
# --------------------------------------------------

# In v0.2.0, a pipeline can expand a single TimeSpan
# into multiple TimeSpans (1 → N).
pipeline = TimeSpanPipeline().then(
    stretch(0.7),  # shorten each base span
    duplicate(2),  # duplicate → chord / unison structure
    split_even(3),  # subdivide each into a small stutter
    shift(25),  # slight global delay
    probability(0.85),  # stochastic thinning
)

processed_spans = pipeline.apply_all(base_spans)

# --------------------------------------------------
# pitch (simple deterministic cycle)
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
