import mido

import hyperscore

s = hyperscore.Score()

ast = hyperscore.parse_rhythm("1/30")
print(ast)

duration = hyperscore.rhythm_to_ticks(ast, total_ticks=5000)
print(duration)

s.add(pitch=[60, 62, 64, 65], duration=duration)

# exporter = hyperscore.MidiExporter(ticks_per_beat=500)
# exporter.export(s, "foo.mid", channel=0)
# exporter.export(s, "bar.mid", channel=1)
# print(s.events_between(0, 10000))

player = hyperscore.MidiPlayer(output=mido.get_output_names()[0])  # type: ignore
player.play(s)
