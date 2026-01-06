from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from hyperscore.core.time import TimeSpan

TimeSpanTransform = Callable[[TimeSpan], TimeSpan | None]


@dataclass(frozen=True)
class TimeSpanPipeline:
    """
    Immutable pipeline of TimeSpan transforms.

    Each transform may:
      - return a modified TimeSpan
      - return None (drop the span)
    """

    transforms: tuple[TimeSpanTransform, ...] = ()

    # ---------------- core ----------------

    def apply(self, span: TimeSpan) -> TimeSpan | None:
        cur: TimeSpan | None = span
        for t in self.transforms:
            if cur is None:
                return None
            cur = t(cur)
        return cur

    def apply_all(self, spans: Iterable[TimeSpan]) -> list[TimeSpan]:
        out: list[TimeSpan] = []
        for s in spans:
            s2 = self.apply(s)
            if s2 is not None:
                out.append(s2)
        return out

    # ---------------- composition ----------------

    def then(self, *more: TimeSpanTransform) -> TimeSpanPipeline:
        return TimeSpanPipeline(self.transforms + more)

    def __or__(self, other: TimeSpanPipeline) -> TimeSpanPipeline:
        return TimeSpanPipeline(self.transforms + other.transforms)
