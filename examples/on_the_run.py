"""
on_the_run.py

A performance-oriented example inspired by repetitive, motoric motion.

This example demonstrates:
- using a fixed rhythmic structure as a repeating grid
- layering simple pitch streams over repeated time spans
- introducing small variations (register, velocity) over long repetition
- exporting to MIDI and playing back in real time

Compared to other examples, this script is intentionally more
"musical" and less minimal, while still relying only on core concepts.
"""

from itertools import cycle
from pathlib import Path

import mido

from hyperscore import Score, parse_rhythm
from hyperscore.core import NoteEvent, bpm_to_ms
from hyperscore.io import MidiExporter, MidiPlayer
from hyperscore.rhythm import rhythm_ast_to_timespans

# --------------------------------------------------
# configuration
# --------------------------------------------------

BPM = 165
BARS = 8
OUTPUT = Path("on_the_run.mid")

# --------------------------------------------------
# pitch stream (repeating, but not symmetric)
# --------------------------------------------------

arp = cycle([52, 55, 57, 55, 62, 60, 62, 64])

# simple long-scale variation
velocity_cycle = cycle([90, 100, 110, 100])
octave_cycle = cycle([0, 0, 12, 0])

# --------------------------------------------------
# rhythm (single bar structure)
# --------------------------------------------------

ast = parse_rhythm("1*16")
bar_ms = int(bpm_to_ms(BPM, 4))

base_spans = rhythm_ast_to_timespans(
    ast,
    total=bar_ms,
)

# --------------------------------------------------
# repeat structure (explicit time shifting)
# --------------------------------------------------

spans = [span.shift(i * bar_ms) for i in range(BARS) for span in base_spans]

# --------------------------------------------------
# event factory
# --------------------------------------------------


def on_the_run_factory(span):
    pitch = next(arp) + next(octave_cycle)
    velocity = next(velocity_cycle)

    return NoteEvent(
        pitch=pitch,
        velocity=velocity,
        span=span,
        channel=0,
    )


# --------------------------------------------------
# score
# --------------------------------------------------

score = Score()
score.add_timespans(spans, factory=on_the_run_factory)

# --------------------------------------------------
# output
# --------------------------------------------------

exporter = MidiExporter()
exporter.export(score, OUTPUT)

player = MidiPlayer(output=mido.get_output_names()[0])  # type: ignore
player.play(score)

print(f"Wrote {OUTPUT}")
