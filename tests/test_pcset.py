import unittest

from hyperscore.pcset import PitchClassSet


class TestPitchClassSet(unittest.TestCase):
    def test_union(self):
        a = PitchClassSet.from_seq([1, 2])
        b = PitchClassSet.from_seq([2, 3])
        self.assertEqual(a.union(b), PitchClassSet.from_seq([1, 2, 3]))

    def test_intersection(self):
        a = PitchClassSet.from_seq([1, 2])
        b = PitchClassSet.from_seq([2, 3])
        self.assertEqual(a.intersection(b), PitchClassSet.from_seq([2]))

    def test_difference(self):
        a = PitchClassSet.from_seq([1, 2])
        b = PitchClassSet.from_seq([2, 3])
        self.assertEqual(a.difference(b), PitchClassSet.from_seq([1, 3]))

    def test_jaccard_similarity(self):
        a = PitchClassSet.from_seq([0, 1, 2, 3, 4, 5])
        b = PitchClassSet.from_seq([3, 4, 5, 6])
        self.assertAlmostEqual(a.jaccard(b), 0.42857142857142855)

    def test_dice_similarity(self):
        a = PitchClassSet.from_seq([0, 1, 2, 3, 4, 5])
        b = PitchClassSet.from_seq([3, 4, 5, 6])
        self.assertAlmostEqual(a.dice(b), 0.6)

    def test_overlap_similarity(self):
        a = PitchClassSet.from_seq([0, 1, 2, 3, 4, 5])
        b = PitchClassSet.from_seq([3, 4, 5, 6])
        self.assertAlmostEqual(a.overlap(b), 0.75)
