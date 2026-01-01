import mido

import hyperscore

score = hyperscore.Score()

arp = [52, 55, 57, 55, 62, 60, 62, 64]

ast = hyperscore.parse_rhythm("1*16")
duration = hyperscore.rhythm_to_ticks(ast, total_ticks=hyperscore.bpm_to_ms(165) * 4)

for _ in range(8):
    score.add(pitch=arp, duration=duration)

# exporter = hyperscore.MidiExporter(ticks_per_beat=500)
# exporter.export(s, "foo.mid", channel=0)
# exporter.export(s, "bar.mid", channel=1)
# print(s.events_between(0, 10000))

player = hyperscore.MidiPlayer(output=mido.get_output_names()[0])  # type: ignore
player.play(score)
