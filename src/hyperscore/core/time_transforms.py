from __future__ import annotations

import random
from collections.abc import Callable, Iterable
from itertools import cycle

from hyperscore.core.time import TimeSpan
from hyperscore.core.time_pipeline import TimeSpanTransform

# ============================================================
# Compatibility / lifting
# ============================================================


def lift_map(f: Callable[[TimeSpan], TimeSpan | None]) -> TimeSpanTransform:
    """
    Lift a legacy TimeSpan -> TimeSpan | None function
    into a v0.2-style TimeSpanTransform.

    This is provided for backward compatibility with
    pre-v0.2.0 transforms.

    Notes
    -----
    - Returning None is interpreted as dropping the span.
    - Returning a TimeSpan is wrapped as a singleton list.
    """

    def wrapped(span: TimeSpan) -> list[TimeSpan]:
        out = f(span)
        if out is None:
            return []
        return [out]

    return wrapped


# ============================================================
# Identity / filtering
# ============================================================


def identity() -> TimeSpanTransform:
    """
    Identity transform.

    Returns the input TimeSpan unchanged.
    This is the neutral element of TimeSpanPipeline composition.
    """

    def f(span: TimeSpan) -> list[TimeSpan]:
        return [span]

    return f


def drop_if(pred: Callable[[TimeSpan], bool]) -> TimeSpanTransform:
    """
    Drop a TimeSpan if the predicate is satisfied.
    """

    def f(span: TimeSpan) -> list[TimeSpan]:
        return [] if pred(span) else [span]

    return f


def keep_if(pred: Callable[[TimeSpan], bool]) -> TimeSpanTransform:
    """
    Keep a TimeSpan only if the predicate is satisfied.
    """

    def f(span: TimeSpan) -> list[TimeSpan]:
        return [span] if pred(span) else []

    return f


def probability(p: float) -> TimeSpanTransform:
    """
    Probabilistically keep or drop TimeSpans.

    With probability ``p``, the input TimeSpan is kept.
    Otherwise, it is dropped.

    Notes
    -----
    - Uses Python's global random generator.
    - Call ``random.seed(...)`` for reproducible results.
    - Intended for stochastic structure variation.
    """

    if not (0.0 <= p <= 1.0):
        raise ValueError("p must be in the range [0.0, 1.0]")

    def f(span: TimeSpan) -> list[TimeSpan]:
        return [span] if random.random() < p else []

    return f


# ============================================================
# Time-domain transforms
# ============================================================


def shift(delta: int) -> TimeSpanTransform:
    """
    Shift a TimeSpan along the time axis.

    Parameters
    ----------
    delta : int
        Time shift in milliseconds.
        Positive values move the span forward,
        negative values move it backward.
    """

    def f(span: TimeSpan) -> list[TimeSpan]:
        return [span.shift(delta)]

    return f


def stretch(factor: float) -> TimeSpanTransform:
    """
    Scale the duration of a TimeSpan.

    The start position is preserved.
    Duration is scaled and rounded to an integer.

    Notes
    -----
    - Duration scaling always uses ``round()`` to
      avoid systematic shortening bias.
    """

    if factor < 0:
        raise ValueError("factor must be non-negative")

    def f(span: TimeSpan) -> list[TimeSpan]:
        return [span.stretch(factor)]

    return f


# ============================================================
# Structural / generative transforms
# ============================================================


def duplicate(n: int) -> TimeSpanTransform:
    """
    Duplicate a TimeSpan ``n`` times.

    This produces multiple identical TimeSpans
    sharing the same time interval.

    Typical use cases include:
    - chords / unison structures
    - layered events
    """

    if n < 0:
        raise ValueError("n must be >= 0")

    def f(span: TimeSpan) -> list[TimeSpan]:
        return [span] * n

    return f


def _validate_counts(counts: Iterable[int], *, name: str = "counts") -> tuple[int, ...]:
    values = tuple(counts)

    if not values:
        raise ValueError(f"{name} must be non-empty")

    invalid = [n for n in values if not isinstance(n, int) or isinstance(n, bool) or n < 0]
    if invalid:
        raise ValueError(f"{name} must contain non-negative integers: {invalid!r}")

    return values


def _validate_binary_pattern(
    pattern: Iterable[int | bool],
    *,
    name: str = "pattern",
) -> tuple[bool, ...]:
    values = tuple(pattern)

    if not values:
        raise ValueError(f"{name} must be non-empty")

    invalid = [x for x in values if not isinstance(x, (int, bool)) or x not in (0, 1, False, True)]
    if invalid:
        raise ValueError(f"{name} must contain only 0/1 or bool values: {invalid!r}")

    return tuple(bool(x) for x in values)


def duplicate_by(counts: Iterable[int]) -> TimeSpanTransform:
    """
    Duplicate each TimeSpan according to a cyclic count pattern.

    Parameters
    ----------
    counts : iterable of int
        Non-negative duplication counts.

    Notes
    -----
    - ``0`` drops the span.
    - ``1`` keeps the span unchanged.
    - ``n >= 2`` emits ``n`` identical spans.
    - The count pattern is cycled across incoming spans.

    Typical use cases include:
    - aligning spans with chord tones
    - layered events with varying multiplicity
    - periodic thinning / expansion patterns
    """

    counts = _validate_counts(counts)
    counts_cycle = cycle(counts)

    def f(span: TimeSpan) -> list[TimeSpan]:
        return [span] * next(counts_cycle)

    return f


def gate_by(pattern: Iterable[int | bool]) -> TimeSpanTransform:
    """
    Keep or drop TimeSpans according to a cyclic gate pattern.

    Parameters
    ----------
    pattern : iterable of int | bool
        Binary gate pattern.
        ``1`` / ``True`` keeps the span.
        ``0`` / ``False`` drops the span.

    Notes
    -----
    - This is a 0/1 specialization of ``duplicate_by``.
    - The gate pattern is cycled across incoming spans.

    Typical use cases include:
    - rests
    - rhythmic thinning
    - periodic omissions
    """

    gates = _validate_binary_pattern(pattern)
    return duplicate_by(1 if gate else 0 for gate in gates)


def split_even(n: int) -> TimeSpanTransform:
    """
    Split a TimeSpan into ``n`` contiguous sub-spans
    of (as) equal (as possible) duration.

    The total duration is preserved exactly.
    Any remainder is distributed to earlier sub-spans.

    Typical use cases include:
    - stutter / ratchet effects
    - rhythmic subdivision
    """

    if n <= 0:
        raise ValueError("n must be > 0")

    def f(span: TimeSpan) -> list[TimeSpan]:
        base = span.duration // n
        rem = span.duration % n

        out: list[TimeSpan] = []
        cur = span.start

        for i in range(n):
            d = base + (1 if i < rem else 0)
            out.append(TimeSpan(cur, d))
            cur += d

        return out

    return f


def split_by(ratios: Iterable[float]) -> TimeSpanTransform:
    """
    Split a TimeSpan according to relative ratios.

    Parameters
    ----------
    ratios : iterable of float
        Relative weights of each sub-span.

    Notes
    -----
    - The total duration is preserved.
    - Durations are rounded and adjusted to ensure
      exact conservation.
    """

    ratios = list(ratios)
    if not ratios:
        raise ValueError("ratios must be non-empty")

    total = sum(ratios)
    if total <= 0:
        raise ValueError("sum of ratios must be > 0")

    def f(span: TimeSpan) -> list[TimeSpan]:
        raw = [span.duration * (r / total) for r in ratios]
        rounded = [round(x) for x in raw]

        diff = span.duration - sum(rounded)
        if diff != 0:
            rounded[0] += diff

        out: list[TimeSpan] = []
        cur = span.start
        for d in rounded:
            out.append(TimeSpan(cur, d))
            cur += d

        return out

    return f
