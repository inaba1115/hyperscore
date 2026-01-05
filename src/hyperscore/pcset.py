from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

# ============================================================
# Basic types
# ============================================================


PitchClass = int  # 0-11


# ============================================================
# Pitch-class set (immutable, with similarity metrics)
# ============================================================


@dataclass(frozen=True)
class PitchClassSet:
    pcs: tuple[PitchClass, ...]

    # ---------- constructors ----------

    @staticmethod
    def from_seq(seq: Sequence[int]) -> PitchClassSet:
        return PitchClassSet(tuple(sorted(set(seq))))

    # ---------- set operations ----------

    def union(self, other: PitchClassSet) -> PitchClassSet:
        return PitchClassSet(tuple(sorted(set(self.pcs) | set(other.pcs))))

    def intersection(self, other: PitchClassSet) -> PitchClassSet:
        return PitchClassSet(tuple(sorted(set(self.pcs) & set(other.pcs))))

    def difference(self, other: PitchClassSet) -> PitchClassSet:
        # symmetric difference
        return PitchClassSet(tuple(sorted(set(self.pcs) ^ set(other.pcs))))

    # ---------- similarity metrics ----------

    def jaccard(self, other: PitchClassSet) -> float:
        inter = len(set(self.pcs) & set(other.pcs))
        uni = len(set(self.pcs) | set(other.pcs))
        return inter / uni if uni else 0.0

    def dice(self, other: PitchClassSet) -> float:
        inter = len(set(self.pcs) & set(other.pcs))
        return 2 * inter / (len(self.pcs) + len(other.pcs))

    def overlap(self, other: PitchClassSet) -> float:
        inter = len(set(self.pcs) & set(other.pcs))
        return inter / min(len(self.pcs), len(other.pcs))
