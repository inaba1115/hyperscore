import mido


def bpm_to_ms(bpm: float) -> int:
    microseconds = mido.bpm2tempo(bpm)
    return int(microseconds / 1_000)
