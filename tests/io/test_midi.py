import unittest

from mido import Message

from hyperscore.core import NoteEvent, ScoreContext, ZippedNotes
from hyperscore.io.midi import convert_to_midi_events


class TestMidi(unittest.TestCase):
    def test_convert_to_midi_events(self):
        context = ScoreContext(cursor_ms=0)
        events, _ = ZippedNotes(pitch=[1, 2], duration=[100, 200], event_factory=NoteEvent).iter_events(context)
        midi_events = convert_to_midi_events(events, 0)

        self.assertEqual(len(midi_events), 4)
        self.assertEqual(midi_events[0], (0, Message("note_on", channel=0, note=1, velocity=100, time=0)))
        self.assertEqual(midi_events[1], (100, Message("note_off", channel=0, note=1, velocity=0, time=100)))
        self.assertEqual(midi_events[2], (100, Message("note_on", channel=0, note=2, velocity=100, time=0)))
        self.assertEqual(midi_events[3], (300, Message("note_off", channel=0, note=2, velocity=0, time=200)))
