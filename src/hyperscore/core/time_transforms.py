import random

from hyperscore.core.time import TimeSpan


def gate(ratio: float):
    def f(span: TimeSpan) -> TimeSpan:
        return TimeSpan(
            start=span.start,
            duration=int(span.duration * ratio),
        )

    return f


def probability(p: float, *, rng=random):
    def f(span: TimeSpan) -> TimeSpan | None:
        return span if rng.random() < p else None

    return f


def shift(delta: int):
    def f(span: TimeSpan) -> TimeSpan:
        return span.shift(delta)

    return f


def stretch(factor: float):
    def f(span: TimeSpan) -> TimeSpan:
        return span.stretch(factor)

    return f
