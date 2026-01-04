import unittest

import hyperscore


class TestTempo(unittest.TestCase):
    def test_bpm_to_ms_note(self):
        self.assertEqual(hyperscore.bpm_to_ms_note(120, note_division=1.0), 500.0)
        self.assertEqual(hyperscore.bpm_to_ms_note(120, note_division=0.5), 250.0)
        self.assertEqual(hyperscore.bpm_to_ms_note(120, note_division=0.25), 125.0)
        self.assertEqual(hyperscore.bpm_to_ms_note(120, note_division=0.125), 62.5)
        self.assertEqual(hyperscore.bpm_to_ms_note(120, note_division=2.0), 1000.0)

        self.assertEqual(int(hyperscore.bpm_to_ms_note(120)), 500)
        self.assertEqual(int(hyperscore.bpm_to_ms_note(130)), 461)
        self.assertEqual(int(hyperscore.bpm_to_ms_note(140)), 428)
        self.assertEqual(int(hyperscore.bpm_to_ms_note(150)), 400)
        self.assertEqual(int(hyperscore.bpm_to_ms_note(160)), 375)
