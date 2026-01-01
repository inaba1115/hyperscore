import time

import mido
from mido import Message

from .score import Score


class MidiPlayer:
    def __init__(self, *, output: mido.ports.BaseOutput):
        self.output = output

    def play(
        self,
        score: Score,
        start_ms: int = 0,
        end_ms: int | None = None,
    ) -> None:
        events = score.events_between(start_ms, end_ms)

        midi_events = []
        for e in events:
            midi_events.append(
                (e.start_ms, Message("note_on", note=e.pitch, velocity=e.velocity, time=0, channel=e.channel))
            )
            midi_events.append(
                (e.start_ms + e.duration_ms, Message("note_off", note=e.pitch, velocity=0, time=0, channel=e.channel))
            )

        midi_events.sort(key=lambda x: x[0])

        last_tick = start_ms
        for tick, msg in midi_events:
            msg.time = tick - last_tick
            last_tick = tick

        with mido.open_output(self.output, autoreset=True) as outport:  # type: ignore
            now = time.time()
            for tick, msg in midi_events:
                now += msg.time * 0.001  # ms to sec
                dt = now - time.time()
                if dt > 0:
                    time.sleep(dt)
                outport.send(msg)
