import unittest

from hyperscore.theory import SCALES, ordered_from_scale


class TestScales(unittest.TestCase):
    def test_ordered_from_scale(self):
        ionian = ordered_from_scale(SCALES["major"])
        dorian = ionian.rotate_mode(1).normalize_to_zero()
        self.assertEqual(ionian.pcs, (0, 2, 4, 5, 7, 9, 11))
        self.assertEqual(dorian.pcs, (0, 2, 3, 5, 7, 9, 10))

    def test_transpose(self):
        phry = SCALES["phrygian"].transpose(1)
        self.assertEqual(phry.pcs.pcs, (1, 2, 4, 6, 8, 9, 11))

    def test_as_set(self):
        ionian = ordered_from_scale(SCALES["major"])
        mode2_set = ionian.rotate_mode(1).as_set()
        self.assertEqual(mode2_set.pcs, (0, 2, 4, 5, 7, 9, 11))
