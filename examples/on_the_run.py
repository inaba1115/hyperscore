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
# score injection
# --------------------------------------------------

score.add_timespans(
    spans,
    factory=lambda span: NoteEvent(
        pitch=next(arp),
        velocity=100,
        span=span,
        gate=1.0,
        probability=1.0,
        channel=0,
    ),
)

# --------------------------------------------------
# output
# --------------------------------------------------

exporter = MidiExporter()
exporter.export(score, "foo.mid")

player = MidiPlayer(output=mido.get_output_names()[0])  # type: ignore
player.play(score)
