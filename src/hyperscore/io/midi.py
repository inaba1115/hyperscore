import time
from collections.abc import Iterable

import mido
import numpy as np
from mido import Message, MetaMessage, MidiFile, MidiTrack

from hyperscore.core import NoteEvent, Score


def convert_to_midi_events(
    events: Iterable[NoteEvent],
    start_ms: int,
    rng: np.random.Generator | None = None,
) -> list[tuple[int, Message]]:
    rng = rng if rng else np.random.default_rng()

    prob_events = [e for e in events if e.probability > rng.uniform()]

    midi_events = []
    for e in prob_events:
        midi_events.append(
            (e.start_ms, Message("note_on", note=e.pitch, velocity=e.velocity, time=0, channel=e.channel))
        )
        midi_events.append(
            (
                e.start_ms + int(e.duration_ms * e.gate),
                Message("note_off", note=e.pitch, velocity=0, time=0, channel=e.channel),
            )
        )

    midi_events.sort(key=lambda x: x[0])

    last_tick = start_ms
    for tick, msg in midi_events:
        msg.time = tick - last_tick
        last_tick = tick

    return midi_events


class MidiExporter:
    def __init__(
        self,
        *,
        ticks_per_beat: int = 500,  # TODO: Score側を1ms基準とするため500としているが、ここは480として変換するのが設計的に良い
        tempo: int = 500_000,
        rng: np.random.Generator | None = None,
    ):
        self.ticks_per_beat = ticks_per_beat
        self.tempo = tempo
        self.rng = rng if rng else np.random.default_rng()

    def export(
        self,
        score: Score,
        path: str,
        start_ms: int = 0,
        end_ms: int | None = None,
        channel: int | None = None,  # AbletonLiveはchannel毎にファイルを分ける必要があるので
    ) -> None:
        midi = MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = MidiTrack()
        midi.tracks.append(track)

        track.append(MetaMessage("set_tempo", tempo=self.tempo, time=0))

        events = score.events_between(start_ms, end_ms)
        if channel is not None:
            events = [e for e in events if e.channel == channel]

        midi_events = convert_to_midi_events(events, start_ms, self.rng)
        for _, msg in midi_events:
            track.append(msg)

        midi.save(path)


class MidiPlayer:
    def __init__(self, *, output: mido.ports.BaseOutput, rng: np.random.Generator | None = None):
        self.output = output
        self.rng = rng if rng else np.random.default_rng()

    def play(self, score: Score, start_ms: int = 0, end_ms: int | None = None) -> None:
        events = score.events_between(start_ms, end_ms)
        midi_events = convert_to_midi_events(events, start_ms, self.rng)

        with mido.open_output(self.output, autoreset=True) as outport:  # type: ignore
            logical_time = time.time()
            for _, msg in midi_events:
                logical_time += msg.time * 0.001  # type: ignore

                delta_time = logical_time - time.time()
                if delta_time > 0:
                    time.sleep(delta_time)

                outport.send(msg)
