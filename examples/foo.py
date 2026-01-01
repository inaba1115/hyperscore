import hyperscore

s = hyperscore.Score()
s.add(pitch=[60, 62, 64, 65], duration=[1000, 1000, 1000, 1000], channel=[0, 1])
exporter = hyperscore.MidiExporter(ticks_per_beat=500)
exporter.export(s, "foo.mid", channel=0)
exporter.export(s, "bar.mid", channel=1)
# print(s.events_between(0, 10000))
