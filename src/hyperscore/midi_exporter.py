from mido import Message, MetaMessage, MidiFile, MidiTrack


class MidiExporter:
    def __init__(
        self,
        *,
        ticks_per_beat: int = 480,
        tempo: int = 500_000,
    ):
        self.ticks_per_beat = ticks_per_beat
        self.tempo = tempo

    def export(
        self,
        score,
        path: str,
        start_tick: int = 0,
        end_tick: int | None = None,
    ) -> None:
        midi = MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = MidiTrack()
        midi.tracks.append(track)

        track.append(MetaMessage("set_tempo", tempo=self.tempo, time=0))

        events = score.events_between(
            start_tick,
            end_tick if end_tick is not None else float("inf"),
        )

        midi_events = []
        for e in events:
            midi_events.append(
                (e.start_tick, Message("note_on", note=e.pitch, velocity=e.velocity, time=0, channel=e.chan))
            )
            midi_events.append(
                (e.start_tick + e.duration_tick, Message("note_off", note=e.pitch, velocity=0, time=0, channel=e.chan))
            )

        midi_events.sort(key=lambda x: x[0])

        last_tick = start_tick
        for tick, msg in midi_events:
            msg.time = tick - last_tick
            track.append(msg)
            last_tick = tick

        midi.save(path)
