import unittest

import hyperscore


class TestTempo(unittest.TestCase):
    def test_bpm_to_ms(self):
        self.assertEqual(hyperscore.bpm_to_ms(120), 500)
        self.assertEqual(hyperscore.bpm_to_ms(130), 461)
        self.assertEqual(hyperscore.bpm_to_ms(140), 428)
        self.assertEqual(hyperscore.bpm_to_ms(150), 400)
        self.assertEqual(hyperscore.bpm_to_ms(160), 375)
