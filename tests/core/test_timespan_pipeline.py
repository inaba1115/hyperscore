from __future__ import annotations

from hyperscore.core import TimeSpan, TimeSpanPipeline
from hyperscore.core.time_transforms import (
    duplicate,
    gate,
    shift,
    split_even,
    stretch,
)

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
    assert len(out) == 1
    assert out[0] == span


def test_pipeline_single_transform():
    """
    Single transform must be applied.
    """
    span = TimeSpan(10, 10)
    pipe = TimeSpanPipeline().then(gate(0.5))

    out = pipe.apply(span)
    assert len(out) == 1
    assert out[0].start == 10
    assert out[0].duration == 5


# ============================================================
# drop semantics
# ============================================================


def test_pipeline_drop():
    """
    Transform returning an empty list must drop the TimeSpan.
    """

    def drop(_: TimeSpan) -> list[TimeSpan]:
        return []

    span = TimeSpan(0, 10)
    pipe = TimeSpanPipeline().then(drop)

    out = pipe.apply(span)
    assert out == []


def test_pipeline_drop_short_circuit():
    """
    Once dropped, remaining transforms must not be applied.
    """
    called = False

    def drop(_: TimeSpan) -> list[TimeSpan]:
        return []

    def marker(span: TimeSpan) -> list[TimeSpan]:
        nonlocal called
        called = True
        return [span]

    span = TimeSpan(0, 10)
    pipe = TimeSpanPipeline().then(drop, marker)

    out = pipe.apply(span)
    assert out == []
    assert called is False


# ============================================================
# apply_all
# ============================================================


def test_apply_all_excludes_dropped_spans():
    """
    apply_all must exclude spans dropped by transforms.
    """
    spans = [
        TimeSpan(0, 10),
        TimeSpan(10, 10),
    ]

    def drop_second(span: TimeSpan) -> list[TimeSpan]:
        return [] if span.start == 10 else [span]

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
    assert len(out) == 1
    assert out[0].start == 15
    assert out[0].duration == 5


def test_pipeline_or_operator():
    """
    pipe1 | pipe2 must concatenate transforms.
    """
    span = TimeSpan(0, 20)

    p1 = TimeSpanPipeline().then(shift(10))
    p2 = TimeSpanPipeline().then(stretch(0.5))

    pipe = p1 | p2
    out = pipe.apply(span)

    assert len(out) == 1
    assert out[0].start == 10
    assert out[0].duration == 10


# ============================================================
# generative semantics (v0.2.0)
# ============================================================


def test_pipeline_duplicate():
    """
    duplicate(n) must produce n identical TimeSpans.
    """
    span = TimeSpan(0, 10)
    pipe = TimeSpanPipeline().then(duplicate(3))

    out = pipe.apply(span)

    assert len(out) == 3
    assert all(s == span for s in out)


def test_pipeline_split_even_preserves_total_duration():
    """
    split_even(n) must preserve total duration exactly.
    """
    span = TimeSpan(0, 10)
    pipe = TimeSpanPipeline().then(split_even(3))

    out = pipe.apply(span)

    assert len(out) == 3
    assert sum(s.duration for s in out) == 10
    assert out[0].start == 0
    assert out[1].start == out[0].end
    assert out[2].start == out[1].end


def test_pipeline_generate_then_drop():
    """
    Dropping after expansion must drop all generated spans.
    """

    def drop_all(_: TimeSpan) -> list[TimeSpan]:
        return []

    span = TimeSpan(0, 10)
    pipe = TimeSpanPipeline().then(
        duplicate(3),
        drop_all,
    )

    out = pipe.apply(span)
    assert out == []


def test_pipeline_split_then_shift():
    """
    Transforms must be applied left-to-right.
    """
    span = TimeSpan(0, 10)
    pipe = TimeSpanPipeline().then(
        split_even(2),
        shift(5),
    )

    out = pipe.apply(span)

    assert [s.start for s in out] == [5, 10]
    assert [s.duration for s in out] == [5, 5]


# ============================================================
# immutability & safety
# ============================================================


def test_pipeline_is_immutable():
    """
    then() must return a new pipeline, not mutate the original.
    """
    p1 = TimeSpanPipeline()
    p2 = p1.then(shift(5))

    span = TimeSpan(0, 10)

    assert p1.apply(span)[0] == span
    assert p2.apply(span)[0] != span


def test_pipeline_does_not_mutate_input_span():
    """
    Pipeline must not mutate original TimeSpan.
    """
    span = TimeSpan(0, 10)
    pipe = TimeSpanPipeline().then(stretch(0.5))

    out = pipe.apply(span)

    assert len(out) == 1
    assert span.start == 0
    assert span.duration == 10
