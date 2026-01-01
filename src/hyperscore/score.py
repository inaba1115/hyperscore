from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class NoteEvent:
    pitch: int
    velocity: int
    start_tick: int
    duration_tick: int
    gate: float
    probability: float
    chan: int


@dataclass
class ScoreContext:
    tick_cursor: int


class ScoreInput(Protocol):
    def iter_events(self, ctx: ScoreContext) -> Iterable[NoteEvent]: ...


@dataclass(frozen=True)
class ZippedNotes:
    pitch: Sequence[int] = field(default_factory=lambda: [60])
    velocity: Sequence[int] = field(default_factory=lambda: [100])
    duration: Sequence[int] = field(default_factory=lambda: [1000])  # int(default_tick_rate * 1.0sec)
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
            yield NoteEvent(
                pitch=p, velocity=v, start_tick=ctx.tick_cursor, duration_tick=d, gate=g, probability=r, chan=c
            )
            ctx.tick_cursor += d


class Score:
    def __init__(self, tick_rate: int = 1000):
        self._tick_rate = tick_rate
        self._context: ScoreContext = ScoreContext(tick_cursor=0)
        self._events: list[NoteEvent] = []

    def get_cursor(self) -> int:
        return self._context.tick_cursor

    def set_cursor(self, tick_cursor: int) -> None:
        self._context.tick_cursor = tick_cursor

    def get_events(self) -> Iterable[NoteEvent]:
        return sorted(self._events, key=lambda e: e.start_tick)

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
