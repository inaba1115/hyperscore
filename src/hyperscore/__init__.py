"""
hyperscore: structural music composition library
"""

from hyperscore.core import Score, ZippedNotes
from hyperscore.rhythm import parse_rhythm
from hyperscore.theory import CHORDS, SCALES

__all__ = [
    "CHORDS",
    "SCALES",
    "Score",
    "ZippedNotes",
    "parse_rhythm",
]
