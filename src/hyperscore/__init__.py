"""
hyperscore: structural music composition library
"""

from hyperscore.core.score import Score, ZippedNotes
from hyperscore.rhythm.rhythm_tree import parse_rhythm
from hyperscore.theory.scales import CHORDS, SCALES

__all__ = [
    "CHORDS",
    "SCALES",
    "Score",
    "ZippedNotes",
    "parse_rhythm",
]
