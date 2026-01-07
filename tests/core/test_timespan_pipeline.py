from __future__ import annotations

from hyperscore.core import TimeSpan, TimeSpanPipeline
from hyperscore.core.time_transforms import gate, shift, stretch

# ============================================================
# basic apply
# ============================================================


def test_pipeline_identity():
    """
    Empty pipeline must return the original TimeSpan.
    """
    span = TimeSpan(10, 5)
    pipe = TimeSpanPipeline()

    out = pipe.apply(span)
    assert out == span


def test_pipeline_single_transform():
    """
    Single transform must be applied.
    """
    span = TimeSpan(10, 10)
    pipe = TimeSpanPipeline().then(gate(0.5))

    out = pipe.apply(span)
    assert out is not None
    assert out.start == 10
    assert out.duration == 5


# ============================================================
# drop semantics
# ============================================================


def test_pipeline_drop():
    """
    Transform returning None must drop the TimeSpan.
    """

    def drop(_: TimeSpan) -> TimeSpan | None:
        return None

    span = TimeSpan(0, 10)
    pipe = TimeSpanPipeline().then(drop)

    out = pipe.apply(span)
    assert out is None


def test_pipeline_drop_short_circuit():
    """
    Once dropped, remaining transforms must not be applied.
    """
    called = False

    def drop(_: TimeSpan) -> TimeSpan | None:
        return None

    def marker(span: TimeSpan) -> TimeSpan:
        nonlocal called
        called = True
        return span

    span = TimeSpan(0, 10)
    pipe = TimeSpanPipeline().then(drop, marker)

    out = pipe.apply(span)
    assert out is None
    assert called is False


# ============================================================
# apply_all
# ============================================================


def test_apply_all_filters_none():
    """
    apply_all must filter out None results.
    """
    spans = [
        TimeSpan(0, 10),
        TimeSpan(10, 10),
    ]

    def drop_second(span: TimeSpan) -> TimeSpan | None:
        return None if span.start == 10 else span

    pipe = TimeSpanPipeline().then(drop_second)

    out = pipe.apply_all(spans)
    assert len(out) == 1
    assert out[0].start == 0


# ============================================================
# composition
# ============================================================


def test_then_composition_order():
    """
    then() must apply transforms in order.
    """
    span = TimeSpan(10, 10)

    pipe = TimeSpanPipeline().then(
        shift(5),
        stretch(0.5),
    )

    out = pipe.apply(span)
    assert out is not None
    assert out.start == 15
    assert out.duration == 5


def test_pipeline_or_operator():
    """
    pipe1 | pipe2 must concatenate transforms.
    """
    span = TimeSpan(0, 20)

    p1 = TimeSpanPipeline().then(shift(10))
    p2 = TimeSpanPipeline().then(stretch(0.5))

    pipe = p1 | p2
    out = pipe.apply(span)

    assert out is not None
    assert out.start == 10
    assert out.duration == 10


# ============================================================
# immutability
# ============================================================


def test_pipeline_is_immutable():
    """
    then() must return a new pipeline, not mutate the original.
    """
    p1 = TimeSpanPipeline()
    p2 = p1.then(shift(5))

    span = TimeSpan(0, 10)

    assert p1.apply(span) == span
    assert p2.apply(span) != span


# ============================================================
# safety
# ============================================================


def test_pipeline_does_not_modify_original_span():
    """
    Pipeline must not mutate original TimeSpan.
    """
    span = TimeSpan(0, 10)
    pipe = TimeSpanPipeline().then(stretch(0.5))

    out = pipe.apply(span)

    assert out is not None
    assert span.start == 0
    assert span.duration == 10
