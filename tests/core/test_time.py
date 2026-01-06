import unittest

from hyperscore.core import bpm_to_ms


class TestTime(unittest.TestCase):
    def test_bpm_to_ms(self):
        self.assertEqual(bpm_to_ms(120, note_division=1.0), 500.0)
        self.assertEqual(bpm_to_ms(120, note_division=0.5), 250.0)
        self.assertEqual(bpm_to_ms(120, note_division=0.25), 125.0)
        self.assertEqual(bpm_to_ms(120, note_division=0.125), 62.5)
        self.assertEqual(bpm_to_ms(120, note_division=2.0), 1000.0)

        self.assertEqual(int(bpm_to_ms(120)), 500)
        self.assertEqual(int(bpm_to_ms(130)), 461)
        self.assertEqual(int(bpm_to_ms(140)), 428)
        self.assertEqual(int(bpm_to_ms(150)), 400)
        self.assertEqual(int(bpm_to_ms(160)), 375)
