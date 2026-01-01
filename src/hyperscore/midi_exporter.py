from mido import Message, MetaMessage, MidiFile, MidiTrack


class MidiExporter:
    def __init__(
        self,
        *,
        ticks_per_beat: int = 500,  # TODO: 1msを使うため500としているが、480として変換するのが良い
        tempo: int = 500_000,
    ):
        self.ticks_per_beat = ticks_per_beat
        self.tempo = tempo

    def export(
        self,
        score,
        path: str,
        start_ms: int = 0,
        end_ms: int | None = None,
    ) -> None:
        midi = MidiFile(ticks_per_beat=self.ticks_per_beat)
        track = MidiTrack()
        midi.tracks.append(track)

        track.append(MetaMessage("set_tempo", tempo=self.tempo, time=0))

        events = score.events_between(
            start_ms,
            end_ms if end_ms is not None else float("inf"),
        )

        midi_events = []
        for e in events:
            midi_events.append(
                (e.start_ms, Message("note_on", note=e.pitch, velocity=e.velocity, time=0, channel=e.chan))
            )
            midi_events.append(
                (e.start_ms + e.duration_ms, Message("note_off", note=e.pitch, velocity=0, time=0, channel=e.chan))
            )

        midi_events.sort(key=lambda x: x[0])

        last_tick = start_ms
        for tick, msg in midi_events:
            msg.time = tick - last_tick
            track.append(msg)
            last_tick = tick

        midi.save(path)
