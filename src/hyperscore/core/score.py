from __future__ import annotations

from collections.abc import Callable, Iterable, Iterator, Sequence
from dataclasses import dataclass, field, fields
from typing import Generic, Protocol, TypeVar

from .time import TimeSpan

# ============================================================
# Event model (default)
# ============================================================


class HasTimeSpan(Protocol):
    span: TimeSpan


@dataclass(frozen=True)
class NoteEvent:
    pitch: int
    velocity: int
    span: TimeSpan
    channel: int


EventT = TypeVar("EventT", bound=HasTimeSpan)


# ============================================================
# Score context
# ============================================================


@dataclass(frozen=True)
class ScoreContext:
    cursor: int

    def advance(self, delta: int) -> ScoreContext:
        return ScoreContext(cursor=self.cursor + delta)


# ============================================================
# ScoreInput protocol (event generator)
# ============================================================


class ScoreInput(Protocol[EventT]):
    def iter_events(
        self,
        ctx: ScoreContext,
    ) -> tuple[list[EventT], ScoreContext]: ...


# ============================================================
# EventFactory protocol
# ============================================================


EventFactory = Callable[..., EventT]


# ============================================================
# ZippedNotes (generic, factory-based)
# ============================================================


@dataclass(frozen=True)
class ZippedNotes(Generic[EventT]):
    """
    Convenience builder for simple sequential note generation.

    For advanced temporal control, prefer:
        - rhythm_tree
        - TimeSpanPipeline
        - Score.add_timespans()
    """

    # ---- core zipped parameters ----
    pitch: Sequence[int] = field(default_factory=lambda: [60])
    velocity: Sequence[int] = field(default_factory=lambda: [100])
    duration: Sequence[int] = field(default_factory=lambda: [1000])
    channel: Sequence[int] = field(default_factory=lambda: [0])

    # ---- extensibility ----
    event_factory: EventFactory[EventT] | None = None

    # --------------------------------

    def _max_len(self) -> int:
        return max(len(getattr(self, f.name)) for f in fields(self) if f.name != "event_factory")

    def iter_events(self, ctx: ScoreContext) -> tuple[list[EventT], ScoreContext]:
        if self.event_factory is None:
            raise ValueError("event_factory must be provided")

        events: list[EventT] = []
        cur = ctx

        for i in range(self._max_len()):
            d = self.duration[i % len(self.duration)]
            span = TimeSpan(start=cur.cursor, duration=d)

            kwargs = {
                "pitch": self.pitch[i % len(self.pitch)],
                "velocity": self.velocity[i % len(self.velocity)],
                "span": span,
                "channel": self.channel[i % len(self.channel)],
            }

            ev = self.event_factory(**kwargs)
            events.append(ev)

            cur = cur.advance(d)

        return events, cur


# ============================================================
# Score
# ============================================================


class Score(Generic[EventT], Iterable[EventT]):
    def __init__(self):
        self._context: ScoreContext = ScoreContext(cursor=0)
        self._events: list[EventT] = []
        self._sorted_by_start: list[EventT] = []
        self._dirty: bool = False

    def __iter__(self) -> Iterator[EventT]:
        """
        Iterate over all events in time order.
        """
        self._ensure_sorted()
        return iter(self._sorted_by_start)

    # ---------------- cursor ----------------

    def get_cursor(self) -> int:
        return self._context.cursor

    def set_cursor(self, cursor: int) -> None:
        self._context = ScoreContext(cursor=cursor)

    # ---------------- add ----------------

    def add(
        self,
        source: ScoreInput[EventT] | None = None,
        *,
        pitch: Sequence[int] | None = None,
        velocity: Sequence[int] | None = None,
        duration: Sequence[int] | None = None,
        channel: Sequence[int] | None = None,
        start: int | None = None,
        event_factory: EventFactory[EventT] | None = None,
    ) -> None:
        """
        Simple, convenience API for basic use cases.

        For advanced temporal control, prefer:
            - rhythm_tree
            - TimeSpanPipeline
            - add_timespans()
        """
        ctx = self._context

        if start is not None:
            ctx = ScoreContext(cursor=start)

        if source is not None:
            events, ctx = source.iter_events(ctx)
            self._events.extend(events)
            self._context = ctx
            self._dirty = True
            return

        if event_factory is None:
            raise ValueError("event_factory must be provided when using zipped parameters")

        kwargs = {
            "pitch": pitch,
            "velocity": velocity,
            "duration": duration,
            "channel": channel,
        }

        source_ = ZippedNotes[EventT](
            **{k: v for k, v in kwargs.items() if v is not None},  # type: ignore[arg-type]
            event_factory=event_factory,
        )

        events, ctx = source_.iter_events(ctx)
        self._events.extend(events)
        self._context = ctx
        self._dirty = True

    def add_timespans(
        self,
        spans: Iterable[TimeSpan],
        *,
        factory: Callable[[TimeSpan], EventT],
    ) -> None:
        """
        Add events generated from TimeSpans.

        Score does not interpret TimeSpan contents.
        """
        for span in spans:
            ev = factory(span)
            self._events.append(ev)

        self._dirty = True

    # ---------------- query ----------------

    def _ensure_sorted(self) -> None:
        if self._dirty:
            self._sorted_by_start = sorted(
                self._events,
                key=lambda e: e.span.start,
            )
            self._dirty = False

    def events_between_span(self, span: TimeSpan) -> list[EventT]:
        """
        Return events whose TimeSpan overlaps with the given span.
        """
        self._ensure_sorted()

        if not self._sorted_by_start:
            return []

        result: list[EventT] = []

        for e in self._sorted_by_start:
            if e.span.overlaps(span):
                result.append(e)

            # optimization: since sorted by start
            if e.span.start >= span.end:
                break

        return result

    def events_between(
        self,
        start_ms: int = 0,
        end_ms: int | None = None,
    ) -> list[EventT]:
        if end_ms is None:
            # 明示的に「start 以降すべて」
            self._ensure_sorted()
            return [e for e in self._sorted_by_start if e.span.start >= start_ms]

        span = TimeSpan(
            start=start_ms,
            duration=end_ms - start_ms,
        )
        return self.events_between_span(span)
