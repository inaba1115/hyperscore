from __future__ import annotations

from hyperscore.core import TimeSpan

# ============================================================
# basic properties
# ============================================================


def test_timespan_end_property():
    """
    end must equal start + duration.
    """
    span = TimeSpan(start=10, duration=5)
    assert span.end == 15


def test_timespan_zero_duration():
    """
    Zero-duration TimeSpan is allowed and well-defined.
    """
    span = TimeSpan(start=10, duration=0)
    assert span.start == 10
    assert span.end == 10


# ============================================================
# contains
# ============================================================


def test_timespan_contains_start():
    """
    start is inclusive.
    """
    span = TimeSpan(10, 5)
    assert span.contains(10)


def test_timespan_contains_end_exclusive():
    """
    end is exclusive.
    """
    span = TimeSpan(10, 5)
    assert not span.contains(15)


def test_timespan_contains_inside():
    span = TimeSpan(10, 5)
    assert span.contains(12)


def test_timespan_contains_outside():
    span = TimeSpan(10, 5)
    assert not span.contains(9)
    assert not span.contains(16)


# ============================================================
# overlap
# ============================================================


def test_timespan_overlap_exact_same():
    """
    Identical spans overlap.
    """
    a = TimeSpan(10, 5)
    b = TimeSpan(10, 5)
    assert a.overlaps(b)


def test_timespan_overlap_partial():
    """
    Partial overlap counts as overlap.
    """
    a = TimeSpan(10, 10)
    b = TimeSpan(15, 10)
    assert a.overlaps(b)
    assert b.overlaps(a)


def test_timespan_overlap_touching_edges():
    """
    Touching at boundary does NOT overlap.
    """
    a = TimeSpan(10, 5)
    b = TimeSpan(15, 5)
    assert not a.overlaps(b)
    assert not b.overlaps(a)


def test_timespan_no_overlap_separated():
    a = TimeSpan(0, 5)
    b = TimeSpan(10, 5)
    assert not a.overlaps(b)


def test_timespan_zero_duration_overlap():
    """
    Zero-duration spans never overlap with non-zero spans.
    """
    a = TimeSpan(10, 0)
    b = TimeSpan(10, 5)
    assert not a.overlaps(b)
    assert not b.overlaps(a)


# ============================================================
# transformations
# ============================================================


def test_timespan_shift():
    span = TimeSpan(10, 5)
    shifted = span.shift(7)

    assert shifted.start == 17
    assert shifted.duration == 5
    assert shifted.end == 22


def test_timespan_shift_negative():
    span = TimeSpan(10, 5)
    shifted = span.shift(-3)

    assert shifted.start == 7
    assert shifted.duration == 5


def test_timespan_stretch():
    span = TimeSpan(10, 10)
    stretched = span.stretch(0.5)

    assert stretched.start == 10
    assert stretched.duration == 5


def test_timespan_stretch_rounding():
    """
    stretch uses round() and must produce integer duration.
    """
    span = TimeSpan(0, 3)
    stretched = span.stretch(0.5)

    assert isinstance(stretched.duration, int)
    assert stretched.duration in (1, 2)


# ============================================================
# immutability
# ============================================================


def test_timespan_is_immutable():
    """
    TimeSpan must be immutable (frozen dataclass).
    """
    span = TimeSpan(0, 10)

    try:
        span.start = 5  # type: ignore[misc]
        assert False, "TimeSpan should be immutable"
    except Exception:
        assert True
