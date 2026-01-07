from __future__ import annotations

from hyperscore.io.midi import MidiTimebase, quantize_times_lrm

# ============================================================
# helpers
# ============================================================


def make_timebase() -> MidiTimebase:
    """
    Standard 120 BPM timebase for tests.
    """
    return MidiTimebase(
        ticks_per_beat=480,
        tempo_us_per_beat=500_000,
    )


# ============================================================
# basic properties
# ============================================================


def test_quantize_preserves_length():
    """
    Output length must equal input length.
    """
    timebase = make_timebase()
    times_ms = [0, 100, 200, 300]

    ticks = quantize_times_lrm(times_ms, timebase=timebase)
    assert len(ticks) == len(times_ms)


def test_quantize_monotonicity():
    """
    Monotonic input times must produce monotonic ticks.
    """
    timebase = make_timebase()
    times_ms = [0, 50, 100, 150, 200]

    ticks = quantize_times_lrm(times_ms, timebase=timebase)
    assert ticks == sorted(ticks)


# ============================================================
# drift prevention (core property)
# ============================================================


def test_quantize_preserves_total_duration():
    """
    Largest Remainder Method must preserve total duration
    (no cumulative drift).
    """
    timebase = make_timebase()

    # 4 equal divisions that are not integer in ticks
    times_ms = [0, 33, 67, 100]

    ticks = quantize_times_lrm(times_ms, timebase=timebase)

    ideal_end = round(timebase.ms_to_ticks_float(times_ms[-1]))
    assert ticks[-1] == ideal_end


def test_quantize_even_distribution():
    """
    Remainders should be distributed as evenly as possible.
    """
    timebase = make_timebase()

    times_ms = [0, 25, 50, 75, 100]
    ticks = quantize_times_lrm(times_ms, timebase=timebase)

    # Differences between successive ticks
    deltas = [b - a for a, b in zip(ticks, ticks[1:])]

    # All deltas should be very close
    assert max(deltas) - min(deltas) <= 1


# ============================================================
# edge cases
# ============================================================


def test_quantize_zero_time():
    """
    Zero time must quantize to zero tick.
    """
    timebase = make_timebase()
    ticks = quantize_times_lrm([0], timebase=timebase)

    assert ticks == [0]


def test_quantize_single_value():
    """
    Single timestamp should quantize correctly.
    """
    timebase = make_timebase()
    times_ms = [123]

    ticks = quantize_times_lrm(times_ms, timebase=timebase)
    assert ticks[0] == round(timebase.ms_to_ticks_float(123))


def test_quantize_large_values():
    """
    Large absolute times should not overflow or misbehave.
    """
    timebase = make_timebase()
    times_ms = [0, 10_000, 20_000, 30_000]

    ticks = quantize_times_lrm(times_ms, timebase=timebase)

    assert ticks[-1] == round(timebase.ms_to_ticks_float(30_000))
