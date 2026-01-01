from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class NoteEvent:
    pitch: int
    velocity: int
    start_ms: int
    duration_ms: int
    gate: float
    probability: float
    chan: int


@dataclass
class ScoreContext:
    cursor_ms: int


class ScoreInput(Protocol):
    def iter_events(self, ctx: ScoreContext) -> Iterable[NoteEvent]: ...


@dataclass(frozen=True)
class ZippedNotes:
    pitch: Sequence[int] = field(default_factory=lambda: [60])
    velocity: Sequence[int] = field(default_factory=lambda: [100])
    duration: Sequence[int] = field(default_factory=lambda: [1000])
    gate: Sequence[float] = field(default_factory=lambda: [1.0])
    probability: Sequence[float] = field(default_factory=lambda: [1.0])
    chan: Sequence[int] = field(default_factory=lambda: [0])

    def iter_events(self, ctx: ScoreContext) -> Iterable[NoteEvent]:
        for i in range(len(self.duration)):
            p = self.pitch[i % len(self.pitch)]
            v = self.velocity[i % len(self.velocity)]
            d = self.duration[i % len(self.duration)]
            g = self.gate[i % len(self.gate)]
            r = self.probability[i % len(self.probability)]
            c = self.chan[i % len(self.chan)]
            yield NoteEvent(pitch=p, velocity=v, start_ms=ctx.cursor_ms, duration_ms=d, gate=g, probability=r, chan=c)
            ctx.cursor_ms += d


class Score:
    def __init__(self):
        self._context: ScoreContext = ScoreContext(cursor_ms=0)
        self._events: list[NoteEvent] = []
        self._sorted_by_start: list[NoteEvent] = []
        self._dirty: bool = False

    def get_cursor(self) -> int:
        return self._context.cursor_ms

    def set_cursor(self, cursor_ms: int) -> None:
        self._context.cursor_ms = cursor_ms

    def add(
        self,
        source: ScoreInput | None = None,
        *,
        pitch: Sequence[int] | None = None,
        velocity: Sequence[int] | None = None,
        duration: Sequence[int] | None = None,
        gate: Sequence[float] | None = None,
        probability: Sequence[float] | None = None,
        chan: Sequence[int] | None = None,
    ) -> None:
        if source:
            self._events.extend(source.iter_events(self._context))
            self._dirty = True
        else:
            kwargs = {
                "pitch": pitch,
                "velocity": velocity,
                "duration": duration,
                "gate": gate,
                "probability": probability,
                "chan": chan,
            }
            source = ZippedNotes(**{k: v for k, v in kwargs.items() if v is not None})  # type: ignore
            self._events.extend(source.iter_events(self._context))
            self._dirty = True

    def _ensure_sorted(self):
        if self._dirty:
            self._sorted_by_start = sorted(self._events, key=lambda e: e.start_ms)
            self._dirty = False

    def events_between(self, start_ms: int, end_ms: int) -> list[NoteEvent]:
        self._ensure_sorted()

        result = []
        for e in self._sorted_by_start:
            if start_ms <= e.start_ms <= end_ms:
                result.append(e)

        return result
