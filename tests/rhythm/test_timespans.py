import pytest

from hyperscore.core.time import TimeSpan
from hyperscore.rhythm.rhythm_tree import (
    parse_rhythm,
    rhythm_ast_to_timespans,
)

# ============================================================
# helpers
# ============================================================


def spans(expr: str, *, total: int, start: int = 0) -> list[TimeSpan]:
    ast = parse_rhythm(expr)
    return rhythm_ast_to_timespans(ast, total=total, start=start)


# ============================================================
# basic behavior
# ============================================================


def test_single_atom_timespan():
    s = spans("1", total=100)
    assert s == [TimeSpan(start=0, duration=100)]


def test_simple_sequence_timespans():
    s = spans("1 1", total=100)
    assert s == [
        TimeSpan(start=0, duration=50),
        TimeSpan(start=50, duration=50),
    ]


def test_weighted_sequence_timespans():
    s = spans("1 2", total=90)
    assert s == [
        TimeSpan(start=0, duration=30),
        TimeSpan(start=30, duration=60),
    ]


# ============================================================
# group
# ============================================================


def test_simple_group_timespans():
    s = spans("2[1 1]", total=100)
    assert s == [
        TimeSpan(start=0, duration=50),
        TimeSpan(start=50, duration=50),
    ]


def test_nested_group_timespans():
    s = spans("2[1 1[1 1]]", total=100)
    assert s == [
        TimeSpan(start=0, duration=50),
        TimeSpan(start=50, duration=25),
        TimeSpan(start=75, duration=25),
    ]


def test_group_with_weighted_body_timespans():
    s = spans("3[1 2]", total=120)
    assert s == [
        TimeSpan(start=0, duration=40),
        TimeSpan(start=40, duration=80),
    ]


# ============================================================
# repeat
# ============================================================


def test_repeat_atom_timespans():
    s = spans("1*4", total=100)
    assert s == [
        TimeSpan(start=0, duration=25),
        TimeSpan(start=25, duration=25),
        TimeSpan(start=50, duration=25),
        TimeSpan(start=75, duration=25),
    ]


def test_repeat_sequence_timespans():
    s = spans("(1 2)*2", total=120)
    assert s == [
        TimeSpan(start=0, duration=20),
        TimeSpan(start=20, duration=40),
        TimeSpan(start=60, duration=20),
        TimeSpan(start=80, duration=40),
    ]


# ============================================================
# split
# ============================================================


def test_split_atom_timespans():
    s = spans("1%4", total=100)
    assert s == [
        TimeSpan(start=0, duration=25),
        TimeSpan(start=25, duration=25),
        TimeSpan(start=50, duration=25),
        TimeSpan(start=75, duration=25),
    ]


def test_split_inside_group_timespans():
    s = spans("2[1%2 1]", total=100)
    assert s == [
        TimeSpan(start=0, duration=25),
        TimeSpan(start=25, duration=25),
        TimeSpan(start=50, duration=50),
    ]


def test_split_on_sequence_is_invalid():
    with pytest.raises(TypeError):
        spans("(1 1)%2", total=100)


# ============================================================
# zero weight handling
# ============================================================


def test_zero_weight_timespan():
    s = spans("0 1", total=100)
    assert s == [
        TimeSpan(start=0, duration=0),
        TimeSpan(start=0, duration=100),
    ]


def test_all_zero_weight_raises():
    with pytest.raises(ValueError):
        spans("0 0", total=100)


# ============================================================
# start offset
# ============================================================


def test_start_offset_applied():
    s = spans("1 1", total=100, start=200)
    assert s == [
        TimeSpan(start=200, duration=50),
        TimeSpan(start=250, duration=50),
    ]


# ============================================================
# determinism
# ============================================================


def test_timespans_are_deterministic():
    a = spans("1[1 2]*2", total=180)
    b = spans("1[1 2]*2", total=180)
    assert a == b
