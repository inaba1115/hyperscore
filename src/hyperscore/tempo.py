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
