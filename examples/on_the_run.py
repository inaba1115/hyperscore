import mido

import hyperscore

score = hyperscore.Score()

arp = [52, 55, 57, 55, 62, 60, 62, 64]

ast = hyperscore.parse_rhythm("1/16")
duration = hyperscore.rhythm_to_ticks(ast, total_ticks=hyperscore.bpm_to_ms(165) * 4)

for _ in range(8):
    score.add(pitch=arp, duration=duration)

# exporter = hyperscore.MidiExporter()
# exporter.export(score, "foo.mid")

player = hyperscore.MidiPlayer(output=mido.get_output_names()[0])  # type: ignore
player.play(score)
