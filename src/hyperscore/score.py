from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field, fields
from typing import Generic, Protocol, TypeVar

# ============================================================
# Event model (default)
# ============================================================


@dataclass(frozen=True)
class NoteEvent:
    pitch: int
    velocity: int
    start_ms: int
    duration_ms: int
    gate: float
    probability: float
    channel: int


EventT = TypeVar("EventT")


# ============================================================
# Score context
# ============================================================


@dataclass(frozen=True)
class ScoreContext:
    cursor_ms: int

    def advance(self, delta_ms: int) -> ScoreContext:
        return ScoreContext(cursor_ms=self.cursor_ms + delta_ms)


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
    # ---- core zipped parameters ----
    pitch: Sequence[int] = field(default_factory=lambda: [60])
    velocity: Sequence[int] = field(default_factory=lambda: [100])
    duration: Sequence[int] = field(default_factory=lambda: [1000])
    gate: Sequence[float] = field(default_factory=lambda: [1.0])
    probability: Sequence[float] = field(default_factory=lambda: [1.0])
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

            kwargs = {
                "pitch": self.pitch[i % len(self.pitch)],
                "velocity": self.velocity[i % len(self.velocity)],
                "start_ms": cur.cursor_ms,
                "duration_ms": d,
                "gate": self.gate[i % len(self.gate)],
                "probability": self.probability[i % len(self.probability)],
                "channel": self.channel[i % len(self.channel)],
            }

            ev = self.event_factory(**kwargs)
            events.append(ev)

            cur = cur.advance(d)

        return events, cur


# ============================================================
# Score
# ============================================================


class Score(Generic[EventT]):
    def __init__(self):
        self._context: ScoreContext = ScoreContext(cursor_ms=0)
        self._events: list[EventT] = []
        self._sorted_by_start: list[EventT] = []
        self._dirty: bool = False

    # ---------------- cursor ----------------

    def get_cursor_ms(self) -> int:
        return self._context.cursor_ms

    def set_cursor_ms(self, cursor_ms: int) -> None:
        self._context = ScoreContext(cursor_ms=cursor_ms)

    # ---------------- add ----------------

    def add(
        self,
        source: ScoreInput[EventT] | None = None,
        *,
        pitch: Sequence[int] | None = None,
        velocity: Sequence[int] | None = None,
        duration: Sequence[int] | None = None,
        gate: Sequence[float] | None = None,
        probability: Sequence[float] | None = None,
        channel: Sequence[int] | None = None,
        start_ms: int | None = None,
        event_factory: EventFactory[EventT] | None = None,
    ) -> None:
        ctx = self._context

        if start_ms is not None:
            ctx = ScoreContext(cursor_ms=start_ms)

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
            "gate": gate,
            "probability": probability,
            "channel": channel,
        }

        source = ZippedNotes(
            **{k: v for k, v in kwargs.items() if v is not None},  # type: ignore[arg-type]
            event_factory=event_factory,
        )

        events, ctx = source.iter_events(ctx)
        self._events.extend(events)
        self._context = ctx
        self._dirty = True

    # ---------------- query ----------------

    def _ensure_sorted(self) -> None:
        if self._dirty:
            self._sorted_by_start = sorted(
                self._events,
                key=lambda e: getattr(e, "start_ms"),
            )
            self._dirty = False

    def events_between(
        self,
        start_ms: int = 0,
        end_ms: int | None = None,
    ) -> list[EventT]:
        self._ensure_sorted()

        if not self._sorted_by_start:
            return []

        if end_ms is None:
            end_ms = max(getattr(e, "start_ms") for e in self._sorted_by_start)

        return [e for e in self._sorted_by_start if start_ms <= getattr(e, "start_ms") <= end_ms]
