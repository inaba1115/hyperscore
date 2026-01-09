from __future__ import annotations

from hyperscore.io.midi import MidiTimebase, ms_to_ticks_int


def make_timebase() -> MidiTimebase:
    return MidiTimebase(
        ticks_per_beat=480,
        tempo_us_per_beat=500_000,
    )


def test_ms_to_ticks_length_preserved():
    """
    Output length must equal input length.
    """
    timebase = make_timebase()
    times_ms = [0, 100, 200, 300]

    ticks = ms_to_ticks_int(times_ms, timebase=timebase)
    assert len(ticks) == len(times_ms)


def test_ms_to_ticks_monotonicity():
    """
    Monotonic input times must produce monotonic ticks.
    """
    timebase = make_timebase()
    times_ms = [0, 50, 100, 150, 200]

    ticks = ms_to_ticks_int(times_ms, timebase=timebase)
    assert ticks == sorted(ticks)


def test_ms_to_ticks_zero_time():
    """
    Zero time must map to zero tick.
    """
    timebase = make_timebase()
    ticks = ms_to_ticks_int([0], timebase=timebase)

    assert ticks == [0]


def test_ms_to_ticks_independent_quantization():
    """
    Each time value must be quantized independently.
    """
    timebase = make_timebase()
    times_ms = [0, 33, 67, 100]

    ticks = ms_to_ticks_int(times_ms, timebase=timebase)

    # No global adjustment: each value stands alone
    for t_ms, t_tick in zip(times_ms, ticks):
        assert t_tick == int(timebase.ms_to_ticks_float(t_ms))
