import random

from hyperscore.core.time import TimeSpan


def gate(ratio: float):
    """
    Truncate a TimeSpan by a fixed ratio.

    This transform shortens the duration of a TimeSpan
    while preserving its start position.

    Parameters
    ----------
    ratio : float
        Duration multiplier (e.g. 0.5 halves the duration).

    Returns
    -------
    callable
        A TimeSpan transform.
    """

    def f(span: TimeSpan) -> TimeSpan:
        return TimeSpan(
            start=span.start,
            duration=int(span.duration * ratio),
        )

    return f


def probability(p: float):
    """
    Probabilistically drop TimeSpans.

    With probability ``p``, the input TimeSpan is kept.
    Otherwise, it is dropped (returns None).

    Notes
    -----
    - Uses Python's global random generator.
    - Call ``random.seed(...)`` for reproducible results.
    - Intended for stochastic filtering, not deterministic logic.

    Parameters
    ----------
    p : float
        Probability of keeping the TimeSpan (0.0-1.0).

    Returns
    -------
    callable
        A TimeSpan transform.
    """

    def f(span: TimeSpan) -> TimeSpan | None:
        return span if random.random() < p else None

    return f


def shift(delta: int):
    """
    Shift a TimeSpan along the time axis.

    Parameters
    ----------
    delta : int
        Time shift in milliseconds.
        Positive values move the span forward in time,
        negative values move it backward.

    Returns
    -------
    callable
        A TimeSpan transform.
    """

    def f(span: TimeSpan) -> TimeSpan:
        return span.shift(delta)

    return f


def stretch(factor: float):
    """
    Stretch or compress a TimeSpan duration.

    The start position is preserved.
    Only the duration is scaled.

    Parameters
    ----------
    factor : float
        Duration scaling factor.
        Values > 1.0 stretch the span,
        values < 1.0 compress it.

    Returns
    -------
    callable
        A TimeSpan transform.
    """

    def f(span: TimeSpan) -> TimeSpan:
        return span.stretch(factor)

    return f
