import mido

import hyperscore as hs

score = hs.Score()

arp = [52, 55, 57, 55, 62, 60, 62, 64]

ast = hs.parse_rhythm("1*16")
duration = hs.rhythm_ast_to_ticks(ast, total_ticks=int(hs.bpm_to_ms(165, 4)))

for _ in range(8):
    score.add(pitch=arp, duration=duration, event_factory=hs.NoteEvent)

# exporter = hs.MidiExporter()
# exporter.export(score, "foo.mid")

player = hs.MidiPlayer(output=mido.get_output_names()[0])  # type: ignore
player.play(score)
