import hyperscore

s = hyperscore.Score()
s.add(pitch=[1, 2, 3], duration=[1000, 2000, 3000])
print(s.get_events())
