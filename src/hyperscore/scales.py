import collections

SCALES = collections.OrderedDict(
    [
        # Five notes scales
        ("min_pent", [0, 3, 5, 7, 10]),
        ("maj_pent", [0, 2, 4, 7, 9]),
        # Another mode of major pentatonic
        ("ritusen", [0, 2, 5, 7, 9]),
        # Another mode of major pentatonic
        ("egyptian", [0, 2, 5, 7, 10]),
        # Other scales
        ("kumai", [0, 2, 3, 7, 9]),
        ("hirajoshi", [0, 2, 3, 7, 8]),
        ("iwato", [0, 1, 5, 6, 10]),
        ("chinese", [0, 4, 6, 7, 11]),
        ("indian", [0, 4, 5, 7, 10]),
        ("pelog", [0, 1, 3, 7, 8]),
        # More scales
        ("prometheus", [0, 2, 4, 6, 11]),
        ("scriabin", [0, 1, 4, 7, 9]),
        # Han Chinese pentatonic scales
        ("gong", [0, 2, 4, 7, 9]),
        ("shang", [0, 2, 5, 7, 10]),
        ("jiao", [0, 3, 5, 8, 10]),
        ("zhi", [0, 2, 5, 7, 9]),
        ("yu", [0, 3, 5, 7, 10]),
        # 6 note scales
        ("whole", [0, 2, 4, 6, 8, 10]),
        ("augmented", [0, 3, 4, 7, 8, 11]),
        ("augmented2", [0, 1, 4, 5, 8, 9]),
        # Hexatonic modes with no tritone
        ("hex_major7", [0, 2, 4, 7, 9, 11]),
        ("hex_dorian", [0, 2, 3, 5, 7, 10]),
        ("hex_phrygian", [0, 1, 3, 5, 8, 10]),
        ("hex_sus", [0, 2, 5, 7, 9, 10]),
        ("hex_major6", [0, 2, 4, 5, 7, 9]),
        ("hex_aeolian", [0, 3, 5, 7, 8, 10]),
        # 7 note scales
        ("major", [0, 2, 4, 5, 7, 9, 11]),
        ("ionian", [0, 2, 4, 5, 7, 9, 11]),
        ("dorian", [0, 2, 3, 5, 7, 9, 10]),
        ("phrygian", [0, 1, 3, 5, 7, 8, 10]),
        ("lydian", [0, 2, 4, 6, 7, 9, 11]),
        ("mixolydian", [0, 2, 4, 5, 7, 9, 10]),
        ("aeolian", [0, 2, 3, 5, 7, 8, 10]),
        ("minor", [0, 2, 3, 5, 7, 8, 10]),
        ("locrian", [0, 1, 3, 5, 6, 8, 10]),
        ("harmonic_minor", [0, 2, 3, 5, 7, 8, 11]),
        ("harmonic_major", [0, 2, 4, 5, 7, 8, 11]),
        ("melodic_minor", [0, 2, 3, 5, 7, 9, 11]),
        ("melodic_minor_desc", [0, 2, 3, 5, 7, 8, 10]),
        ("melodic_major", [0, 2, 4, 5, 7, 8, 10]),
        # Raga modes
        ("todi", [0, 1, 3, 6, 7, 8, 11]),
        ("purvi", [0, 1, 4, 6, 7, 8, 11]),
        ("marva", [0, 1, 4, 6, 7, 9, 11]),
        ("bhairav", [0, 1, 4, 5, 7, 8, 11]),
        ("ahirbhairav", [0, 1, 4, 5, 7, 9, 10]),
        # More modes
        ("super_locrian", [0, 1, 3, 4, 6, 8, 10]),
        ("romanian_minor", [0, 2, 3, 6, 7, 9, 10]),
        ("hungarian_minor", [0, 2, 3, 6, 7, 8, 11]),
        ("neapolitan_minor", [0, 1, 3, 5, 7, 8, 11]),
        ("enigmatic", [0, 1, 4, 6, 8, 10, 11]),
        ("spanish", [0, 1, 4, 5, 7, 8, 10]),
        # Modes of whole tones with added note
        ("leading_whole", [0, 2, 4, 6, 8, 10, 11]),
        ("lydian_minor", [0, 2, 4, 6, 7, 8, 10]),
        ("neapolitan_major", [0, 1, 3, 5, 7, 9, 11]),
        ("locrian_major", [0, 2, 4, 5, 6, 8, 10]),
        # 8 note scales
        ("diminished", [0, 1, 3, 4, 6, 7, 9, 10]),
        ("diminished2", [0, 2, 3, 5, 6, 8, 9, 11]),
        # Modes of limited transposition
        ("messiaen3", [0, 2, 3, 4, 6, 7, 8, 10, 11]),
        ("messiaen4", [0, 1, 2, 5, 6, 7, 8, 11]),
        ("messiaen5", [0, 1, 5, 6, 7, 11]),
        ("messiaen6", [0, 2, 4, 5, 6, 8, 10, 11]),
        ("messiaen7", [0, 1, 2, 3, 5, 6, 7, 8, 9, 11]),
        # 12 note scales
        ("chromatic", [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]),
    ],
)

CHORDS = collections.OrderedDict(
    [
        # Major chords
        ("major", [0, 4, 7]),
        ("aug", [0, 4, 8]),
        ("six", [0, 4, 7, 9]),
        ("six_nine", [0, 4, 7, 9, 14]),
        ("major7", [0, 4, 7, 11]),
        ("major9", [0, 4, 7, 11, 14]),
        ("add9", [0, 4, 7, 14]),
        ("major11", [0, 4, 7, 11, 14, 17]),
        ("add11", [0, 4, 7, 17]),
        ("major13", [0, 4, 7, 11, 14, 21]),
        ("add13", [0, 4, 7, 21]),
        # Dominant chords
        ("dom7", [0, 4, 7, 10]),
        ("dom9", [0, 4, 7, 14]),
        ("dom11", [0, 4, 7, 17]),
        ("dom13", [0, 4, 7, 21]),
        ("seven_flat5", [0, 4, 6, 10]),
        ("seven_sharp5", [0, 4, 8, 10]),
        ("seven_flat9", [0, 4, 7, 10, 13]),
        ("nine", [0, 4, 7, 10, 14]),
        ("eleven", [0, 4, 7, 10, 14, 17]),
        ("thirteen", [0, 4, 7, 10, 14, 17, 21]),
        # Minor chords
        ("minor", [0, 3, 7]),
        ("diminished", [0, 3, 6]),
        ("minor_sharp5", [0, 3, 8]),
        ("minor6", [0, 3, 7, 9]),
        ("minor_six_nine", [0, 3, 9, 7, 14]),
        ("minor7flat5", [0, 3, 6, 10]),
        ("minor7", [0, 3, 7, 10]),
        ("minor7sharp5", [0, 3, 8, 10]),
        ("minor7flat9", [0, 3, 7, 10, 13]),
        ("minor7sharp9", [0, 3, 7, 10, 15]),
        ("diminished7", [0, 3, 6, 9]),
        ("minor9", [0, 3, 7, 10, 14]),
        ("minor11", [0, 3, 7, 10, 14, 17]),
        ("minor13", [0, 3, 7, 10, 14, 17, 21]),
        ("minor_major7", [0, 3, 7, 11]),
        # Other chords
        ("one", [0]),
        ("five", [0, 7]),
        ("sus2", [0, 2, 7]),
        ("sus4", [0, 5, 7]),
        ("seven_sus2", [0, 2, 7, 10]),
        ("seven_sus4", [0, 5, 7, 10]),
        ("nine_sus4", [0, 5, 7, 10, 14]),
        # Questionable chords
        ("seven_flat10", [0, 4, 7, 10, 15]),
        ("nine_sharp5", [0, 1, 13]),
        ("minor9sharp5", [0, 1, 14]),
        ("seven_sharp5flat9", [0, 4, 8, 10, 13]),
        ("minor7sharp5flat9", [0, 3, 8, 10, 13]),
        ("eleven_sharp", [0, 4, 7, 10, 14, 18]),
        ("minor11sharp", [0, 3, 7, 10, 14, 18]),
    ],
)


def union(xs: list[int], ys: list[int]) -> list[int]:
    return sorted(set(xs) | set(ys))


def intersection(xs: list[int], ys: list[int]) -> list[int]:
    return sorted(set(xs) & set(ys))


def difference(xs: list[int], ys: list[int]) -> list[int]:
    return sorted(set(xs) ^ set(ys))


def unique(xs: list[int]) -> list[int]:
    return sorted(set(xs))


def jaccard_similarity(xs: list[int], ys: list[int]) -> float:
    return len(intersection(xs, ys)) / len(union(xs, ys))


def dice_similarity(xs: list[int], ys: list[int]) -> float:
    return 2 * len(intersection(xs, ys)) / (len(xs) + len(ys))


def overlap_similarity(xs: list[int], ys: list[int]) -> float:
    return len(intersection(xs, ys)) / min(len(xs), len(ys))
