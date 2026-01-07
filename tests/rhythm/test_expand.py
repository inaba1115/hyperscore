from fractions import Fraction

import pytest

from hyperscore.rhythm.rhythm_tree import (
    Sequence,
    expand_to_fractions,
    normalize,
    parse_rhythm,
)

# ============================================================
# helpers
# ============================================================


def expand(expr: str) -> list[Fraction]:
    ast = parse_rhythm(expr)
    norm = normalize(ast)
    assert isinstance(norm, Sequence)
    return expand_to_fractions(norm)


# ============================================================
# basic expansion
# ============================================================


def test_single_atom():
    assert expand("1") == [Fraction(1, 1)]


def test_simple_sequence():
    assert expand("1 1") == [
        Fraction(1, 2),
        Fraction(1, 2),
    ]


def test_weighted_sequence():
    assert expand("1 2") == [
        Fraction(1, 3),
        Fraction(2, 3),
    ]


# ============================================================
# group expansion
# ============================================================


def test_simple_group():
    d = expand("2[1 1]")
    assert d == [
        Fraction(1, 2),
        Fraction(1, 2),
    ]


def test_nested_group():
    d = expand("2[1 1[1 1]]")
    # outer group distributes its share equally
    # inner group splits its own share evenly
    assert d == [
        Fraction(1, 2),
        Fraction(1, 4),
        Fraction(1, 4),
    ]


def test_group_with_weighted_body():
    d = expand("3[1 2]")
    assert d == [
        Fraction(1, 3),
        Fraction(2, 3),
    ]


# ============================================================
# repeat
# ============================================================


def test_repeat_atom():
    d = expand("1*4")
    assert d == [
        Fraction(1, 4),
        Fraction(1, 4),
        Fraction(1, 4),
        Fraction(1, 4),
    ]


def test_repeat_sequence_is_flattened():
    d = expand("(1 2)*2")
    assert d == [
        Fraction(1, 6),
        Fraction(2, 6),
        Fraction(1, 6),
        Fraction(2, 6),
    ]


# ============================================================
# split (Atom only)
# ============================================================


def test_split_atom():
    d = expand("1%4")
    assert d == [
        Fraction(1, 4),
        Fraction(1, 4),
        Fraction(1, 4),
        Fraction(1, 4),
    ]


def test_split_inside_group():
    d = expand("2[1%2 1]")
    assert d == [
        Fraction(1, 4),
        Fraction(1, 4),
        Fraction(1, 2),
    ]


def test_split_on_sequence_is_invalid():
    with pytest.raises(TypeError):
        expand("(1 1)*2 %4")


# ============================================================
# zero weight handling
# ============================================================


def test_zero_weight_is_allowed():
    d = expand("0 1")
    assert d == [
        Fraction(0, 1),
        Fraction(1, 1),
    ]


def test_all_zero_weight_raises():
    with pytest.raises(ValueError):
        expand("0 0")


# ============================================================
# structure assumptions
# ============================================================


def test_normalized_sequence_is_flat():
    ast = parse_rhythm("(1 2)*2")
    norm = normalize(ast)
    assert isinstance(norm, Sequence)

    # no nested Sequence remains
    for item in norm.items:
        assert not isinstance(item, Sequence)
