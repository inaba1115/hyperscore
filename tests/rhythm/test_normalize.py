from __future__ import annotations

from fractions import Fraction

import pytest

from hyperscore.rhythm.rhythm_tree import (
    Atom,
    Group,
    Repeat,
    Sequence,
    Split,
    normalize,
    parse_rhythm,
)

# ============================================================
# helpers
# ============================================================


def norm(text: str):
    """
    Parse → normalize helper.
    """
    ast = parse_rhythm(text)
    return normalize(ast)


def assert_no_repeat_or_split(node):
    """
    Recursively assert that no Repeat or Split nodes exist.
    """
    if isinstance(node, (Repeat, Split)):
        pytest.fail(f"Repeat/Split node found after normalize: {node}")

    if isinstance(node, Sequence):
        for n in node.items:
            assert_no_repeat_or_split(n)

    if isinstance(node, Group):
        assert_no_repeat_or_split(node.body)


# ============================================================
# basic behavior
# ============================================================


def test_normalize_atom():
    n = norm("1")
    assert isinstance(n, Sequence)
    assert n.items == [Atom(Fraction(1, 1))]


def test_normalize_sequence_flat():
    n = norm("1 2 3")
    assert isinstance(n, Sequence)
    assert n.items == [
        Atom(Fraction(1, 1)),
        Atom(Fraction(2, 1)),
        Atom(Fraction(3, 1)),
    ]


# ============================================================
# repeat
# ============================================================


def test_normalize_repeat():
    n = norm("1*3")
    assert isinstance(n, Sequence)
    assert n.items == [
        Atom(Fraction(1, 1)),
        Atom(Fraction(1, 1)),
        Atom(Fraction(1, 1)),
    ]
    assert_no_repeat_or_split(n)


def test_normalize_nested_repeat():
    n = norm("(1 2)*2")
    assert isinstance(n, Sequence)
    assert n.items == [
        Atom(Fraction(1, 1)),
        Atom(Fraction(2, 1)),
        Atom(Fraction(1, 1)),
        Atom(Fraction(2, 1)),
    ]
    assert_no_repeat_or_split(n)


# ============================================================
# split
# ============================================================


def test_normalize_split():
    n = norm("1%4")
    assert isinstance(n, Sequence)
    assert len(n.items) == 1
    g = n.items[0]
    assert isinstance(g, Group)

    # group weight
    assert g.weight == Atom(Fraction(1, 1))

    # body should be sequence of ones
    assert isinstance(g.body, Sequence)
    assert g.body.items == [
        Atom(Fraction(1, 1)),
        Atom(Fraction(1, 1)),
        Atom(Fraction(1, 1)),
        Atom(Fraction(1, 1)),
    ]
    assert_no_repeat_or_split(n)


def test_normalize_split_requires_atom():
    """
    Split base must normalize to Atom.
    """
    ast = parse_rhythm("(1 2)%3")
    with pytest.raises(TypeError):
        normalize(ast)


# ============================================================
# grouping
# ============================================================


def test_normalize_group_preserved():
    n = norm("2[1 3]")
    assert isinstance(n, Sequence)
    assert len(n.items) == 1

    g = n.items[0]
    assert isinstance(g, Group)
    assert g.weight == Atom(Fraction(2, 1))
    assert g.body.items == [
        Atom(Fraction(1, 1)),
        Atom(Fraction(3, 1)),
    ]


def test_normalize_nested_group():
    n = norm("1[2[3 4]]")
    assert isinstance(n, Sequence)

    g1 = n.items[0]
    assert isinstance(g1, Group)
    assert g1.weight == Atom(Fraction(1, 1))

    inner = g1.body.items[0]
    assert isinstance(inner, Group)
    assert inner.weight == Atom(Fraction(2, 1))
    assert inner.body.items == [
        Atom(Fraction(3, 1)),
        Atom(Fraction(4, 1)),
    ]


# ============================================================
# flattening behavior
# ============================================================


def test_normalize_flattens_sequences():
    n = norm("(1 (2 3))")
    assert isinstance(n, Sequence)
    assert n.items == [
        Atom(Fraction(1, 1)),
        Atom(Fraction(2, 1)),
        Atom(Fraction(3, 1)),
    ]


def test_normalize_repeat_inside_group():
    n = norm("1[(2*2)]")
    g = n.items[0]
    assert isinstance(g, Group)
    assert g.body.items == [
        Atom(Fraction(2, 1)),
        Atom(Fraction(2, 1)),
    ]
    assert_no_repeat_or_split(n)


# ============================================================
# determinism
# ============================================================


def test_normalize_is_deterministic():
    a = norm("1[1 2]*2")
    b = norm("1[1 2]*2")
    assert a == b
