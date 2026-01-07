from fractions import Fraction

import pytest

from hyperscore.rhythm.rhythm_tree import (
    Atom,
    Group,
    Repeat,
    Sequence,
    Split,
    parse_rhythm,
)

# ============================================================
# basic parsing
# ============================================================


def test_parse_single_atom():
    ast = parse_rhythm("1")
    assert isinstance(ast, Sequence)
    assert ast.items == [Atom(Fraction(1, 1))]


def test_parse_fraction_atom():
    ast = parse_rhythm("3/4")
    assert isinstance(ast, Sequence)
    assert ast.items == [Atom(Fraction(3, 4))]


def test_parse_sequence():
    ast = parse_rhythm("1 2 3")
    assert isinstance(ast, Sequence)
    assert ast.items == [
        Atom(Fraction(1, 1)),
        Atom(Fraction(2, 1)),
        Atom(Fraction(3, 1)),
    ]


# ============================================================
# group parsing
# ============================================================


def test_parse_simple_group():
    ast = parse_rhythm("2[1 1]")
    assert isinstance(ast, Sequence)
    g = ast.items[0]
    assert isinstance(g, Group)
    assert g.weight == Atom(Fraction(2, 1))
    assert g.body.items == [
        Atom(Fraction(1, 1)),
        Atom(Fraction(1, 1)),
    ]


def test_parse_nested_group():
    ast = parse_rhythm("2[1 1[1 1]]")
    g = ast.items[0]
    assert isinstance(g, Group)
    assert isinstance(g.body, Sequence)

    inner = g.body.items[1]
    assert isinstance(inner, Group)
    assert inner.weight == Atom(Fraction(1, 1))
    assert inner.body.items == [
        Atom(Fraction(1, 1)),
        Atom(Fraction(1, 1)),
    ]


# ============================================================
# repeat parsing
# ============================================================


def test_parse_repeat_atom():
    ast = parse_rhythm("1*4")
    node = ast.items[0]
    assert isinstance(node, Repeat)
    assert node.times == 4
    assert isinstance(node.node, Atom)


def test_parse_repeat_sequence():
    ast = parse_rhythm("(1 2)*2")
    node = ast.items[0]
    assert isinstance(node, Repeat)
    assert node.times == 2
    assert isinstance(node.node, Sequence)
    assert node.node.items == [
        Atom(Fraction(1, 1)),
        Atom(Fraction(2, 1)),
    ]


def test_parse_nested_repeat():
    ast = parse_rhythm("(1 2)*2*3")
    node = ast.items[0]
    assert isinstance(node, Repeat)
    assert node.times == 3
    assert isinstance(node.node, Repeat)
    assert node.node.times == 2


# ============================================================
# split parsing
# ============================================================


def test_parse_split_atom():
    ast = parse_rhythm("1%4")
    node = ast.items[0]
    assert isinstance(node, Split)
    assert node.parts == 4
    assert isinstance(node.node, Atom)


def test_parse_split_after_repeat():
    ast = parse_rhythm("1*2%3")
    node = ast.items[0]
    assert isinstance(node, Split)
    assert node.parts == 3
    assert isinstance(node.node, Repeat)


def test_parse_repeat_after_split():
    ast = parse_rhythm("1%2*3")
    node = ast.items[0]
    assert isinstance(node, Repeat)
    assert node.times == 3
    assert isinstance(node.node, Split)


# ============================================================
# precedence & postfix chaining
# ============================================================


def test_postfix_is_left_associative():
    ast = parse_rhythm("1*2%3")
    # equivalent to (1*2)%3
    node = ast.items[0]
    assert isinstance(node, Split)
    assert node.parts == 3
    assert isinstance(node.node, Repeat)
    assert node.node.times == 2


def test_parentheses_override_postfix_scope():
    ast = parse_rhythm("(1 2)%3")
    node = ast.items[0]
    assert isinstance(node, Split)
    assert node.parts == 3
    assert isinstance(node.node, Sequence)


# ============================================================
# multiple expressions
# ============================================================


def test_multiple_expressions():
    ast = parse_rhythm("1 2[1 1] 3*2")
    assert isinstance(ast, Sequence)
    assert len(ast.items) == 3
    assert isinstance(ast.items[0], Atom)
    assert isinstance(ast.items[1], Group)
    assert isinstance(ast.items[2], Repeat)


# ============================================================
# invalid syntax
# ============================================================


def test_invalid_syntax_raises():
    with pytest.raises(Exception):
        parse_rhythm("1[2")  # missing closing bracket
