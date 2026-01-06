import unittest

from hyperscore.core import NoteEvent, Score, TimeSpan, ZippedNotes


class TestScore(unittest.TestCase):
    def test_add_source(self):
        source = ZippedNotes(
            pitch=[60, 62],
            velocity=[80, 100],
            duration=[100, 200],
            channel=[0, 1],
            event_factory=NoteEvent,
        )
        score = Score()
        score.add(source, start=500)
        events = score.events_between()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].pitch, 60)
        self.assertEqual(events[0].velocity, 80)
        self.assertEqual(events[0].span, TimeSpan(500, 100))
        self.assertEqual(events[0].channel, 0)
        self.assertEqual(events[1].pitch, 62)
        self.assertEqual(events[1].velocity, 100)
        self.assertEqual(events[1].span, TimeSpan(600, 200))
        self.assertEqual(events[1].channel, 1)

    def test_add_sugar(self):
        score = Score()
        score.add(
            pitch=[60, 62],
            velocity=[80, 100],
            duration=[100, 200],
            channel=[0, 1],
            start=500,
            event_factory=NoteEvent,
        )
        events = score.events_between()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].pitch, 60)
        self.assertEqual(events[0].velocity, 80)
        self.assertEqual(events[0].span, TimeSpan(500, 100))
        self.assertEqual(events[0].channel, 0)
        self.assertEqual(events[1].pitch, 62)
        self.assertEqual(events[1].velocity, 100)
        self.assertEqual(events[1].span, TimeSpan(600, 200))
        self.assertEqual(events[1].channel, 1)
