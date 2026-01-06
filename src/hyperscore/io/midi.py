from __future__ import annotations

import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

import mido
import numpy as np
from mido import Message, MetaMessage, MidiFile, MidiTrack

from hyperscore.core import NoteEvent

# ============================================================
# Time conversion utilities
# ============================================================


@dataclass(frozen=True)
class MidiTimebase:
    """
    MIDI timebase configuration.

    ticks_per_beat: MIDI resolution
    tempo_us_per_beat: microseconds per beat
    """

    ticks_per_beat: int = 480
    tempo_us_per_beat: int = 500_000  # 120 BPM

    @property
    def ticks_per_second(self) -> float:
        return self.ticks_per_beat * 1_000_000 / self.tempo_us_per_beat

    def ms_to_ticks_float(self, ms: int) -> float:
        return ms * self.ticks_per_second / 1000.0


# ============================================================
# Largest Remainder Method (global quantization)
# ============================================================


def quantize_times_lrm(
    times_ms: Sequence[int],
    *,
    timebase: MidiTimebase,
) -> list[int]:
    """
    Convert absolute times (ms) to MIDI ticks using
    Largest Remainder Method to avoid drift.
    """
    floats = [timebase.ms_to_ticks_float(t) for t in times_ms]
    floors = [int(x) for x in floats]
    remainders = [x - f for x, f in zip(floats, floors)]

    target_sum = round(sum(floats))
    current_sum = sum(floors)
    diff = target_sum - current_sum

    if diff > 0:
        # distribute +1 to largest remainders
        indices = sorted(range(len(remainders)), key=lambda i: remainders[i], reverse=True)
        for i in indices[:diff]:
            floors[i] += 1

    return floors


# ============================================================
# Event → MIDI message expansion (TimeSpan-based)
# ============================================================


def note_events_to_midi_messages(
    events: Iterable[NoteEvent],
    *,
    timebase: MidiTimebase,
    rng: np.random.Generator,
) -> list[tuple[int, Message]]:
    """
    Convert NoteEvents to absolute-time MIDI messages (ticks).
    """
    # ---- probability filter ----
    filtered = [e for e in events if e.probability > rng.uniform()]

    # ---- build absolute ms times ----
    times_ms: list[int] = []
    msg_specs: list[tuple[str, NoteEvent]] = []

    for e in filtered:
        span = e.span
        note_off_ms = span.start + int(span.duration * e.gate)

        times_ms.append(span.start)
        msg_specs.append(("on", e))

        times_ms.append(note_off_ms)
        msg_specs.append(("off", e))

    # ---- quantize ms -> ticks globally ----
    times_ticks = quantize_times_lrm(times_ms, timebase=timebase)

    # ---- build MIDI messages ----
    messages: list[tuple[int, Message]] = []

    for (kind, e), tick in zip(msg_specs, times_ticks):
        if kind == "on":
            msg = Message(
                "note_on",
                note=e.pitch,
                velocity=e.velocity,
                channel=e.channel,
                time=0,
            )
        else:
            msg = Message(
                "note_off",
                note=e.pitch,
                velocity=0,
                channel=e.channel,
                time=0,
            )

        messages.append((tick, msg))

    # ---- sort by absolute tick ----
    messages.sort(key=lambda x: x[0])
    return messages


def absolute_to_delta(messages: list[tuple[int, Message]]) -> list[Message]:
    """
    Convert absolute-tick messages to delta-time messages.
    """
    out: list[Message] = []
    last_tick = 0

    for tick, msg in messages:
        msg.time = tick - last_tick
        last_tick = tick
        out.append(msg)

    return out


# ============================================================
# MIDI Exporter
# ============================================================


class MidiExporter:
    def __init__(
        self,
        *,
        ticks_per_beat: int = 480,
        tempo_us_per_beat: int = 500_000,
        rng: np.random.Generator | None = None,
    ):
        self.timebase = MidiTimebase(
            ticks_per_beat=ticks_per_beat,
            tempo_us_per_beat=tempo_us_per_beat,
        )
        self.rng = rng if rng else np.random.default_rng()

    def export(
        self,
        events: Iterable[NoteEvent],
        path: str,
        *,
        channel: int | None = None,
    ) -> None:
        midi = MidiFile(ticks_per_beat=self.timebase.ticks_per_beat)
        track = MidiTrack()
        midi.tracks.append(track)

        track.append(
            MetaMessage(
                "set_tempo",
                tempo=self.timebase.tempo_us_per_beat,
                time=0,
            )
        )

        if channel is not None:
            events = [e for e in events if e.channel == channel]

        abs_msgs = note_events_to_midi_messages(
            events,
            timebase=self.timebase,
            rng=self.rng,
        )

        for msg in absolute_to_delta(abs_msgs):
            track.append(msg)

        midi.save(path)


# ============================================================
# MIDI Player (TimeSpan-based, lightweight)
# ============================================================


class MidiPlayer:
    def __init__(
        self,
        *,
        output: mido.ports.BaseOutput,
        timebase: MidiTimebase | None = None,
        rng: np.random.Generator | None = None,
    ):
        self.output = output
        self.timebase = timebase or MidiTimebase()
        self.rng = rng if rng else np.random.default_rng()

    def play(
        self,
        events: Iterable[NoteEvent],
        *,
        channel: int | None = None,
    ) -> None:
        if channel is not None:
            events = [e for e in events if e.channel == channel]

        abs_msgs = note_events_to_midi_messages(
            events,
            timebase=self.timebase,
            rng=self.rng,
        )
        delta_msgs = absolute_to_delta(abs_msgs)

        with mido.open_output(self.output, autoreset=True) as outport:  # type: ignore
            logical_time = time.time()

            for msg in delta_msgs:
                # MIDI delta time is in ticks → convert to seconds
                delta_sec = msg.time / self.timebase.ticks_per_second  # type: ignore
                logical_time += delta_sec

                sleep_time = logical_time - time.time()
                if sleep_time > 0:
                    time.sleep(sleep_time)

                outport.send(msg)
