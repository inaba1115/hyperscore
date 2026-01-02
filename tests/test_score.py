import unittest

import hyperscore


class TestZippedNotes(unittest.TestCase):
    def test_iter_events(self):
        source = hyperscore.ZippedNotes(
            pitch=[60, 62], velocity=[80, 100], duration=[100, 200], gate=[0.5], probability=[0.5], channel=[0, 1]
        )
        context = hyperscore.ScoreContext(cursor_ms=500)
        events = list(source.iter_events(context))
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].pitch, 60)
        self.assertEqual(events[0].velocity, 80)
        self.assertEqual(events[0].start_ms, 500)
        self.assertEqual(events[0].duration_ms, 100)
        self.assertEqual(events[0].gate, 0.5)
        self.assertEqual(events[0].probability, 0.5)
        self.assertEqual(events[0].channel, 0)
        self.assertEqual(events[1].pitch, 62)
        self.assertEqual(events[1].velocity, 100)
        self.assertEqual(events[1].start_ms, 600)
        self.assertEqual(events[1].duration_ms, 200)
        self.assertEqual(events[1].gate, 0.5)
        self.assertEqual(events[1].probability, 0.5)
        self.assertEqual(events[1].channel, 1)


class TestScore(unittest.TestCase):
    def test_add_source(self):
        source = hyperscore.ZippedNotes(
            pitch=[60, 62], velocity=[80, 100], duration=[100, 200], gate=[0.5], probability=[0.5], channel=[0, 1]
        )
        score = hyperscore.Score()
        score.add(source, start_ms=500)
        events = score.events_between()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].pitch, 60)
        self.assertEqual(events[0].velocity, 80)
        self.assertEqual(events[0].start_ms, 500)
        self.assertEqual(events[0].duration_ms, 100)
        self.assertEqual(events[0].gate, 0.5)
        self.assertEqual(events[0].probability, 0.5)
        self.assertEqual(events[0].channel, 0)
        self.assertEqual(events[1].pitch, 62)
        self.assertEqual(events[1].velocity, 100)
        self.assertEqual(events[1].start_ms, 600)
        self.assertEqual(events[1].duration_ms, 200)
        self.assertEqual(events[1].gate, 0.5)
        self.assertEqual(events[1].probability, 0.5)
        self.assertEqual(events[1].channel, 1)

    def test_add_sugar(self):
        score = hyperscore.Score()
        score.add(
            pitch=[60, 62],
            velocity=[80, 100],
            duration=[100, 200],
            gate=[0.5],
            probability=[0.5],
            channel=[0, 1],
            start_ms=500,
        )
        events = score.events_between()
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0].pitch, 60)
        self.assertEqual(events[0].velocity, 80)
        self.assertEqual(events[0].start_ms, 500)
        self.assertEqual(events[0].duration_ms, 100)
        self.assertEqual(events[0].gate, 0.5)
        self.assertEqual(events[0].probability, 0.5)
        self.assertEqual(events[0].channel, 0)
        self.assertEqual(events[1].pitch, 62)
        self.assertEqual(events[1].velocity, 100)
        self.assertEqual(events[1].start_ms, 600)
        self.assertEqual(events[1].duration_ms, 200)
        self.assertEqual(events[1].gate, 0.5)
        self.assertEqual(events[1].probability, 0.5)
        self.assertEqual(events[1].channel, 1)
