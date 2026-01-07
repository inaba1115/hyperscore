from __future__ import annotations

import math

from hyperscore.theory.pcset import PitchClassSet

# ============================================================
# constructors
# ============================================================


def test_from_seq_removes_duplicates_and_sorts():
    pcs = PitchClassSet.from_seq([0, 7, 4, 7, 0])
    assert pcs.pcs == (0, 4, 7)


def test_from_seq_applies_mod12():
    pcs = PitchClassSet.from_seq([12, 13, -1])
    # 12 -> 0, 13 -> 1, -1 -> 11
    assert pcs.pcs == (0, 1, 11)


def test_empty_pcset():
    pcs = PitchClassSet.from_seq([])
    assert pcs.pcs == ()


# ============================================================
# set operations
# ============================================================


def test_union():
    a = PitchClassSet.from_seq([0, 4, 7])
    b = PitchClassSet.from_seq([7, 10])
    c = a.union(b)
    assert c.pcs == (0, 4, 7, 10)


def test_intersection():
    a = PitchClassSet.from_seq([0, 4, 7])
    b = PitchClassSet.from_seq([7, 10])
    c = a.intersection(b)
    assert c.pcs == (7,)


def test_difference_is_symmetric_difference():
    a = PitchClassSet.from_seq([0, 4, 7])
    b = PitchClassSet.from_seq([7, 10])
    c = a.difference(b)
    # symmetric difference: {0,4,10}
    assert c.pcs == (0, 4, 10)


# ============================================================
# transpose
# ============================================================


def test_transpose_positive():
    pcs = PitchClassSet.from_seq([0, 4, 7])
    t = pcs.transpose(2)
    assert t.pcs == (2, 6, 9)


def test_transpose_negative():
    pcs = PitchClassSet.from_seq([0, 4, 7])
    t = pcs.transpose(-1)
    assert t.pcs == (3, 6, 11)


def test_transpose_wraps_mod12():
    pcs = PitchClassSet.from_seq([11])
    t = pcs.transpose(2)
    assert t.pcs == (1,)


# ============================================================
# similarity metrics
# ============================================================


def test_jaccard_similarity():
    a = PitchClassSet.from_seq([0, 4, 7])
    b = PitchClassSet.from_seq([0, 7, 10])

    # intersection = {0,7} (2)
    # union = {0,4,7,10} (4)
    assert math.isclose(a.jaccard(b), 0.5)


def test_dice_similarity():
    a = PitchClassSet.from_seq([0, 4, 7])
    b = PitchClassSet.from_seq([0, 7, 10])

    # 2 * |intersection| / (|a| + |b|) = 4 / 6
    assert math.isclose(a.dice(b), 4 / 6)


def test_overlap_similarity():
    a = PitchClassSet.from_seq([0, 4, 7])
    b = PitchClassSet.from_seq([0, 7, 10])

    # |intersection| / min(|a|, |b|) = 2 / 3
    assert math.isclose(a.overlap(b), 2 / 3)


def test_similarity_with_empty_set():
    a = PitchClassSet.from_seq([])
    b = PitchClassSet.from_seq([0, 1, 2])

    assert a.jaccard(b) == 0.0
    assert a.dice(b) == 0.0
    assert a.overlap(b) == 0.0
