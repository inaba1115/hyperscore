import unittest

from hyperscore.scales import (
    dice_similarity,
    difference,
    intersection,
    jaccard_similarity,
    overlap_similarity,
    union,
    unique,
)


class TestScales(unittest.TestCase):
    def test_union(self):
        self.assertEqual(union([1, 2], [2, 3]), [1, 2, 3])

    def test_intersection(self):
        self.assertEqual(intersection([1, 2], [2, 3]), [2])

    def test_difference(self):
        self.assertEqual(difference([1, 2], [2, 3]), [1, 3])

    def test_unique(self):
        self.assertEqual(unique([3, 2, 1, 1, 2, 3]), [1, 2, 3])

    def test_jaccard_similarity(self):
        xs = [0, 1, 2, 3, 4, 5]
        ys = [3, 4, 5, 6]
        self.assertAlmostEqual(jaccard_similarity(xs, ys), 0.42857142857142855)

    def test_dice_similarity(self):
        xs = [0, 1, 2, 3, 4, 5]
        ys = [3, 4, 5, 6]
        self.assertAlmostEqual(dice_similarity(xs, ys), 0.6)

    def test_overlap_similarity(self):
        xs = [0, 1, 2, 3, 4, 5]
        ys = [3, 4, 5, 6]
        self.assertAlmostEqual(overlap_similarity(xs, ys), 0.75)
