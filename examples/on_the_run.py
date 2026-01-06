import random
from itertools import cycle

import mido

from hyperscore import Score, parse_rhythm
from hyperscore.core import NoteEvent, bpm_to_ms
from hyperscore.io import MidiExporter, MidiPlayer
from hyperscore.rhythm import rhythm_ast_to_timespans

score = Score()

# --------------------------------------------------
# pitch stream
# --------------------------------------------------

arp = cycle([52, 55, 57, 55, 62, 60, 62, 64])

# --------------------------------------------------
# rhythm (one bar)
# --------------------------------------------------

ast = parse_rhythm("1*16")
bar_ms = int(bpm_to_ms(165, 4))

base_spans = rhythm_ast_to_timespans(ast, total=bar_ms)

# --------------------------------------------------
# repeat structure
# --------------------------------------------------

spans = [span.shift(i * bar_ms) for i in range(8) for span in base_spans]

# --------------------------------------------------
# factory
# --------------------------------------------------


def on_the_run_factory(span):
    pitch = next(arp)

    probability = random.choice([1.0, 1.0, 0.8, 0.6, 0.0])

    gate = random.choice([0.15, 0.25, 0.4, 0.7])

    return NoteEvent(
        pitch=pitch,
        velocity=100,
        span=span,
        gate=gate,
        probability=probability,
        channel=0,
    )


# --------------------------------------------------
# score injection
# --------------------------------------------------

score.add_timespans(spans, factory=on_the_run_factory)

# --------------------------------------------------
# output
# --------------------------------------------------

exporter = MidiExporter()
exporter.export(score, "foo.mid")

player = MidiPlayer(output=mido.get_output_names()[0])  # type: ignore
player.play(score)
