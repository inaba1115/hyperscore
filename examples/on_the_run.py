import mido

from hyperscore import Score, parse_rhythm
from hyperscore.core import NoteEvent, bpm_to_ms
from hyperscore.io import MidiExporter, MidiPlayer
from hyperscore.rhythm import rhythm_ast_to_ticks

score = Score()

arp = [52, 55, 57, 55, 62, 60, 62, 64]

ast = parse_rhythm("1*16")
duration = rhythm_ast_to_ticks(ast, total_ticks=int(bpm_to_ms(165, 4)))

for _ in range(8):
    score.add(pitch=arp, duration=duration, event_factory=NoteEvent)

# exporter = MidiExporter()
# exporter.export(score, "foo.mid")

player = MidiPlayer(output=mido.get_output_names()[0])  # type: ignore
player.play(score)
