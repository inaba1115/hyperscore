# hyperscore

**hyperscore** is a structural music composition framework that models music as explicit, composable structure rather than notation or performance.  
Time is represented uniformly using immutable time spans, pitch is handled as pitch-class structure independent of register, and rhythm is expressed as relative proportions resolved into concrete time only when needed. External formats such as MIDI are treated as lossy boundaries, not as the source of truth. hyperscore is designed for experimentation, analysis, and integration with algorithmic systems, rather than for score engraving or DAW-style workflows.

---

## Minimal example

```python
from hyperscore import CHORDS, Score, ZippedNotes, parse_rhythm
from hyperscore.core import NoteEvent, TimeSpan, bpm_to_ms
from hyperscore.io import MidiExporter
from hyperscore.rhythm import rhythm_ast_to_timespans
```

### 1. Define harmonic material

```python
# Use a predefined chord as a pitch-class reference
chord = CHORDS["major"]
```

### 2. Describe rhythm structurally

```python
# Parse a simple rhythm DSL
ast = parse_rhythm("1*4")

# Convert beats to absolute time (milliseconds)
total = int(bpm_to_ms(120, 1))

# Expand rhythm into explicit TimeSpans
spans = rhythm_ast_to_timespans(ast, total=total)
```

### 3. Build a score

```python
score: Score[NoteEvent] = Score()

pitch_cycle = iter([60, 62, 64, 67])  # C D E G

score.add_timespans(
    spans,
    factory=lambda span: NoteEvent(
        pitch=next(pitch_cycle),
        velocity=100,
        span=span,
        channel=0,
    ),
)
```

The `Score` stores events on an explicit time axis.  
No tempo, meter, or performance semantics are assumed.

### 4. Export to MIDI

```python
exporter = MidiExporter()
exporter.export(score, "example.mid")
```

This writes a standard MIDI file using global time quantization.

---

## What this example demonstrates

- Rhythm is expressed as **structure**, not notation
- Time is handled explicitly via immutable `TimeSpan` objects
- Pitch and rhythm are **independent layers**
- MIDI is treated as a **lossy output format**

For more advanced usage, see:

- `examples/`
- `tests/test_smoke.py`

---

## Optional: ZippedNotes shortcut

```python
score = Score()

score.add(
    pitch=[60, 62, 64, 67],
    velocity=[100],
    duration=[250],
    channel=[0],
    event_factory=lambda **kw: NoteEvent(
        pitch=kw["pitch"],
        velocity=kw["velocity"],
        span=TimeSpan(0, kw["duration"]),
        channel=kw["channel"],
    ),
)
```

This is a convenience API; for complex timing, prefer `TimeSpan`-based workflows.

---

## Project status

- Python >= 3.10
- Typed (`py.typed`)
- Experimental / research-oriented
- API may evolve between minor versions

hyperscore favors clarity of structure and explicitness of time
over completeness or stylistic prescription.
