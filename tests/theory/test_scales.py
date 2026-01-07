from __future__ import annotations

from hyperscore.theory.pcset import PitchClassSet
from hyperscore.theory.scales import (
    CHORDS,
    SCALES,
    Chord,
    Scale,
    ScaleOrdered,
    ordered_from_scale,
)

# ============================================================
# Scale
# ============================================================


def test_scale_basic_properties():
    s = SCALES["major"]
    assert isinstance(s, Scale)
    assert s.name == "major"
    assert isinstance(s.pcs, PitchClassSet)
    assert s.pcs.pcs == (0, 2, 4, 5, 7, 9, 11)


def test_scale_transpose():
    s = SCALES["major"]
    t = s.transpose(2)

    assert isinstance(t, Scale)
    assert t.name == "major_+2"
    assert t.pcs.pcs == (2, 4, 6, 7, 9, 11, 1) or t.pcs.pcs == (
        1,
        2,
        4,
        6,
        7,
        9,
        11,
    )


def test_scale_transpose_custom_name():
    s = SCALES["minor"]
    t = s.transpose(3, name="minor_up_m3")

    assert t.name == "minor_up_m3"


# ============================================================
# Ordered scale
# ============================================================


def test_ordered_from_scale():
    s = SCALES["dorian"]
    o = ordered_from_scale(s)

    assert isinstance(o, ScaleOrdered)
    assert o.name == "dorian"
    assert o.pcs == s.pcs.pcs


def test_ordered_transpose():
    o = ordered_from_scale(SCALES["major"])
    t = o.transpose(5)

    assert isinstance(t, ScaleOrdered)
    assert t.pcs == tuple((pc + 5) % 12 for pc in o.pcs)


def test_ordered_rotate_mode():
    o = ordered_from_scale(SCALES["major"])
    m = o.rotate_mode(1)

    assert isinstance(m, ScaleOrdered)
    assert m.pcs == o.pcs[1:] + o.pcs[:1]
    assert m.name.endswith("_mode2")


def test_ordered_normalize_to_zero():
    o = ScaleOrdered("test", (2, 4, 7))
    n = o.normalize_to_zero()

    assert n.pcs == (0, 2, 5)


def test_ordered_as_set():
    o = ordered_from_scale(SCALES["phrygian"])
    s = o.as_set()

    assert isinstance(s, PitchClassSet)
    assert set(s.pcs) == set(o.pcs)


# ============================================================
# Chords
# ============================================================


def test_chord_basic():
    c = CHORDS["major"]
    assert isinstance(c, Chord)
    assert c.name == "major"
    assert isinstance(c.intervals, PitchClassSet)
    assert c.intervals.pcs == (0, 4, 7)


def test_chord_intervals_mod12():
    c = CHORDS["six_nine"]
    # 14 == 2 mod 12
    assert set(c.intervals.pcs) == {0, 2, 4, 7, 9}


# ============================================================
# Dictionaries integrity
# ============================================================


def test_scales_dict_non_empty():
    assert len(SCALES) > 0
    for name, scale in SCALES.items():
        assert isinstance(name, str)
        assert isinstance(scale, Scale)


def test_chords_dict_non_empty():
    assert len(CHORDS) > 0
    for name, chord in CHORDS.items():
        assert isinstance(name, str)
        assert isinstance(chord, Chord)


# ============================================================
# Determinism
# ============================================================


def test_scale_transpose_deterministic():
    s = SCALES["lydian"]
    a = s.transpose(7)
    b = s.transpose(7)
    assert a == b


def test_ordered_rotate_deterministic():
    o = ordered_from_scale(SCALES["mixolydian"])
    a = o.rotate_mode(3)
    b = o.rotate_mode(3)
    assert a == b
