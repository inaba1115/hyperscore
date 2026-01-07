from __future__ import annotations

import time
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from os import PathLike
from pathlib import Path

import mido
from mido import Message, MetaMessage, MidiFile, MidiTrack

from hyperscore.core import NoteEvent

# ============================================================
# Time conversion utilities
# ============================================================


@dataclass(frozen=True)
class MidiTimebase:
    """
    MIDI timebase configuration.

    This class defines the mapping between real time
    (milliseconds) and MIDI ticks.

    Attributes
    ----------
    ticks_per_beat : int
        MIDI resolution.
    tempo_us_per_beat : int
        Tempo expressed as microseconds per beat.
    """

    ticks_per_beat: int = 480
    tempo_us_per_beat: int = 500_000  # 120 BPM

    @property
    def ticks_per_second(self) -> float:
        """
        Return the number of MIDI ticks per second.
        """
        return self.ticks_per_beat * 1_000_000 / self.tempo_us_per_beat

    def ms_to_ticks_float(self, ms: int) -> float:
        """
        Convert milliseconds to fractional MIDI ticks.
        """
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
    Quantize absolute times (milliseconds) into MIDI ticks
    using the Largest Remainder Method (LRM).

    This method ensures that the total tick sum matches
    the rounded ideal value, avoiding cumulative timing drift.

    Parameters
    ----------
    times_ms : sequence of int
        Absolute times in milliseconds.
    timebase : MidiTimebase
        MIDI timebase configuration.

    Returns
    -------
    list of int
        Quantized absolute times in MIDI ticks.
    """
    floats = [timebase.ms_to_ticks_float(t) for t in times_ms]
    floors = [int(x) for x in floats]
    remainders = [x - f for x, f in zip(floats, floors)]

    target_sum = round(sum(floats))
    current_sum = sum(floors)
    diff = target_sum - current_sum

    if diff > 0:
        # distribute +1 to largest remainders
        indices = sorted(
            range(len(remainders)),
            key=lambda i: remainders[i],
            reverse=True,
        )
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
) -> list[tuple[int, Message]]:
    """
    Convert NoteEvents into absolute-time MIDI messages.

    Each NoteEvent is expanded into:
    - a note_on message at span.start
    - a note_off message at span.end

    Absolute times are quantized globally to MIDI ticks.

    Parameters
    ----------
    events : iterable of NoteEvent
        Input note events.
    timebase : MidiTimebase
        MIDI timebase configuration.

    Returns
    -------
    list of (int, Message)
        Pairs of (absolute_tick, MIDI message).
    """
    # ---- build absolute ms times ----
    times_ms: list[int] = []
    msg_specs: list[tuple[str, NoteEvent]] = []

    for e in events:
        times_ms.append(e.span.start)
        msg_specs.append(("on", e))

        times_ms.append(e.span.end)
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
    messages.sort(key=lambda x: (x[0], 0 if x[1].type == "note_off" else 1))
    return messages


def absolute_to_delta(messages: list[tuple[int, Message]]) -> list[Message]:
    """
    Convert absolute-tick MIDI messages into delta-time messages.

    Parameters
    ----------
    messages : list of (int, Message)
        Absolute-tick MIDI messages.

    Returns
    -------
    list of Message
        MIDI messages with delta-time populated.
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
    """
    MIDI file exporter for TimeSpan-based NoteEvents.

    This exporter converts hyperscore NoteEvents into
    a standard MIDI file, performing global time quantization.
    """

    def __init__(
        self,
        *,
        ticks_per_beat: int = 480,
        tempo_us_per_beat: int = 500_000,
    ):
        """
        Initialize the exporter with a given MIDI timebase.
        """
        self.timebase = MidiTimebase(
            ticks_per_beat=ticks_per_beat,
            tempo_us_per_beat=tempo_us_per_beat,
        )

    def export(
        self,
        events: Iterable[NoteEvent],
        path: str | PathLike[str],
        *,
        channel: int | None = None,
    ) -> None:
        """
        Export NoteEvents to a MIDI file.

        Parameters
        ----------
        events : iterable of NoteEvent
            Input note events.
        path : str or PathLike
            Output MIDI file path.
        channel : int or None, optional
            If specified, only events on this channel
            are exported.

        Notes
        -----
        - Event ordering is derived from TimeSpan start times.
        - MIDI is treated as a lossy output format.
        """
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
        )

        for msg in absolute_to_delta(abs_msgs):
            track.append(msg)

        midi.save(Path(path))


# ============================================================
# MIDI Player (TimeSpan-based, lightweight)
# ============================================================


class MidiPlayer:
    """
    Lightweight real-time MIDI player for NoteEvents.

    This player schedules MIDI messages based on TimeSpan
    timing and sends them to a MIDI output port.
    """

    def __init__(
        self,
        *,
        output: mido.ports.BaseOutput,
        timebase: MidiTimebase | None = None,
    ):
        """
        Initialize the MIDI player.

        Parameters
        ----------
        output : mido output port
            MIDI output destination.
        timebase : MidiTimebase or None
            Optional timebase configuration.
        """
        self.output = output
        self.timebase = timebase or MidiTimebase()

    def play(
        self,
        events: Iterable[NoteEvent],
        *,
        channel: int | None = None,
    ) -> None:
        """
        Play NoteEvents in real time via a MIDI output port.

        Parameters
        ----------
        events : iterable of NoteEvent
            Input note events.
        channel : int or None, optional
            If specified, only events on this channel
            are played.

        Notes
        -----
        - Scheduling uses wall-clock time and is not
          sample-accurate.
        - Intended for preview and testing, not
          high-precision performance.
        """
        if channel is not None:
            events = [e for e in events if e.channel == channel]

        abs_msgs = note_events_to_midi_messages(
            events,
            timebase=self.timebase,
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
