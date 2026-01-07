from __future__ import annotations

from fractions import Fraction

from hyperscore.rhythm.rhythm_tree import Sequence, expand_to_fractions, normalize, parse_rhythm

# ============================================================
# helpers
# ============================================================


def expand(text: str) -> list[Fraction]:
    """
    Parse → normalize → expand helper.
    """
    ast = parse_rhythm(text)

    norm = normalize(ast)
    assert isinstance(norm, Sequence)

    return expand_to_fractions(norm)


# ============================================================
# basic properties
# ============================================================


def test_expand_sum_is_one():
    """
    Expanded fractions must sum to exactly 1.
    """
    fracs = expand("1 1 1 1")
    assert sum(fracs) == Fraction(1, 1)


def test_expand_single_atom():
    """
    Single atom expands to [1].
    """
    fracs = expand("1")
    assert fracs == [Fraction(1, 1)]


# ============================================================
# grouping
# ============================================================


def test_expand_simple_group():
    """
    Group distributes weight to its body.
    1[1 1] -> two equal parts
    """
    fracs = expand("1[1 1]")
    assert fracs == [Fraction(1, 2), Fraction(1, 2)]


def test_expand_group_weight():
    """
    Group weight affects distribution.
    2[1 1] inside total 2 -> still equal internally.
    """
    fracs = expand("2[1 1]")
    assert fracs == [Fraction(1, 2), Fraction(1, 2)]


def test_expand_mixed_atoms_and_group():
    """
    Atoms and groups share outer weight.
    """
    fracs = expand("1 1[1 1]")
    # total outer weights: 1 + 1 = 2
    # first atom: 1/2
    # group: 1/2 split into two
    assert fracs == [
        Fraction(1, 2),
        Fraction(1, 4),
        Fraction(1, 4),
    ]


# ============================================================
# repeat / split sugar
# ============================================================


def test_expand_repeat():
    """
    Repeat sugar must expand to repeated atoms.
    """
    fracs = expand("1*3")
    assert fracs == [
        Fraction(1, 3),
        Fraction(1, 3),
        Fraction(1, 3),
    ]


def test_expand_split():
    """
    Split sugar must expand to equal parts.
    """
    fracs = expand("1%4")
    assert fracs == [
        Fraction(1, 4),
        Fraction(1, 4),
        Fraction(1, 4),
        Fraction(1, 4),
    ]


# ============================================================
# nesting
# ============================================================


def test_expand_nested_group():
    """
    Nested groups must multiply proportions correctly.
    """
    fracs = expand("1[1[1 1] 1]")
    # structure:
    # outer group -> total 2
    # first inner group weight 1 -> half
    #   inner splits into two -> each 1/4
    # second atom -> half
    assert fracs == [
        Fraction(1, 4),
        Fraction(1, 4),
        Fraction(1, 2),
    ]


def test_expand_complex_structure():
    """
    More complex nested + repeat structure.
    """
    fracs = expand("(1[1 2])*2")
    # inner: 1[1 2] -> [1/3, 2/3]
    # repeated twice, total 4 elements
    # each repetition gets half of total
    assert fracs == [
        Fraction(1, 6),
        Fraction(2, 6),
        Fraction(1, 6),
        Fraction(2, 6),
    ]


# ============================================================
# safety
# ============================================================


def test_expand_deterministic():
    """
    Expansion must be deterministic.
    """
    a = expand("1[1 2]")
    b = expand("1[1 2]")
    assert a == b
