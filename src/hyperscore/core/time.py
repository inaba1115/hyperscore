from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TimeSpan:
    """
    Immutable time span in milliseconds (or ticks).

    start: inclusive
    duration: non-negative
    """

    start: int
    duration: int

    @property
    def end(self) -> int:
        return self.start + self.duration

    def shift(self, delta: int) -> TimeSpan:
        """Move the span in time."""
        return TimeSpan(self.start + delta, self.duration)

    def stretch(self, factor: float) -> TimeSpan:
        """Scale duration (start unchanged)."""
        return TimeSpan(self.start, round(self.duration * factor))

    def overlaps(self, other: TimeSpan) -> bool:
        return not (self.end <= other.start or other.end <= self.start)

    def contains(self, t: int) -> bool:
        return self.start <= t < self.end


def bpm_to_ms(bpm: float, note_division: float = 1.0) -> float:
    """
    BPM -> milliseconds for a note length

    note_division:
        1.0 = quarter note
        0.5 = eighth note
        0.25 = sixteenth note
        2.0 = half note
    """
    return 60_000.0 / bpm * note_division
