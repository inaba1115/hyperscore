from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

# ============================================================
# Basic type
# ============================================================

PitchClass = int  # 0-11


def _mod12(x: int) -> int:
    return x % 12


# ============================================================
# Pitch-class set
# ============================================================


@dataclass(frozen=True)
class PitchClassSet:
    """
    Immutable pitch-class set.

    - Orderless (set semantics)
    - Unique
    - Sorted
    """

    pcs: tuple[PitchClass, ...]

    # ---------- special methods ----------

    def __contains__(self, pc: int) -> bool:
        return _mod12(pc) in self.pcs

    def __len__(self) -> int:
        return len(self.pcs)

    # ---------- constructors ----------

    @staticmethod
    def from_seq(seq: Sequence[int]) -> PitchClassSet:
        return PitchClassSet(tuple(sorted({_mod12(x) for x in seq})))

    # ---------- set operations ----------

    def union(self, other: PitchClassSet) -> PitchClassSet:
        return PitchClassSet.from_seq(tuple(set(self.pcs) | set(other.pcs)))

    def intersection(self, other: PitchClassSet) -> PitchClassSet:
        return PitchClassSet.from_seq(tuple(set(self.pcs) & set(other.pcs)))

    def difference(self, other: PitchClassSet) -> PitchClassSet:
        # symmetric difference
        return PitchClassSet.from_seq(tuple(set(self.pcs) ^ set(other.pcs)))

    # ---------- transformation ----------

    def transpose(self, n: int) -> PitchClassSet:
        """
        Transpose all pitch classes by n semitones (mod 12).
        """
        return PitchClassSet.from_seq(tuple(pc + n for pc in self.pcs))

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
