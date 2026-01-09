from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass

from hyperscore.core.time import TimeSpan

TimeSpanTransform = Callable[[TimeSpan], Iterable[TimeSpan]]


@dataclass(frozen=True)
class TimeSpanPipeline:
    """
    Immutable pipeline for transforming TimeSpan objects.

    A pipeline is a pure, composable sequence of TimeSpan
    transformations. Each transform may either:

    - return a modified TimeSpan
    - return ``None`` to drop the span

    Notes
    -----
    - The pipeline itself holds no state.
    - No temporal ordering is enforced.
    - This class does not generate TimeSpans; it only
      transforms existing ones.

    Typical use cases include:
    - quantization
    - clipping
    - filtering by duration or position
    - time-warping in the TimeSpan domain
    """

    transforms: tuple[TimeSpanTransform, ...] = ()

    # ---------------- core ----------------

    def apply(self, span: TimeSpan) -> list[TimeSpan]:
        """
        Apply the pipeline to a single TimeSpan.

        Parameters
        ----------
        span : TimeSpan
            Input TimeSpan.

        Returns
        -------
        TimeSpan or None
            Transformed TimeSpan, or None if dropped
            by any transform.
        """
        cur: list[TimeSpan] = [span]
        for t in self.transforms:
            nxt: list[TimeSpan] = []
            for s in cur:
                nxt.extend(list(t(s)))
            cur = nxt
        return cur

    def apply_all(self, spans: Iterable[TimeSpan]) -> list[TimeSpan]:
        """
        Apply the pipeline to an iterable of TimeSpans.

        TimeSpans dropped by the pipeline are excluded
        from the result.

        Parameters
        ----------
        spans : iterable of TimeSpan
            Input TimeSpans.

        Returns
        -------
        list of TimeSpan
            Transformed TimeSpans.
        """
        out: list[TimeSpan] = []
        for s in spans:
            out.extend(self.apply(s))
        return out

    # ---------------- composition ----------------

    def then(self, *more: TimeSpanTransform) -> TimeSpanPipeline:
        """
        Return a new pipeline with additional transforms appended.

        This method does not modify the original pipeline.

        Parameters
        ----------
        *more : callable
            Additional TimeSpan transforms.

        Returns
        -------
        TimeSpanPipeline
            A new composed pipeline.
        """
        return TimeSpanPipeline(self.transforms + more)

    def __or__(self, other: TimeSpanPipeline) -> TimeSpanPipeline:
        """
        Compose two pipelines using the ``|`` operator.

        The resulting pipeline applies this pipeline first,
        then the other pipeline.

        Returns
        -------
        TimeSpanPipeline
            Composed pipeline.
        """
        return TimeSpanPipeline(self.transforms + other.transforms)
