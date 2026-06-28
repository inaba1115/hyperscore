# Changelog

## 0.1.0

Initial public release.

- Structural music composition framework
- Explicit TimeSpan-based time model
- Rhythm DSL with proportional expansion
- MIDI export and playback
- Experimental, research-oriented API

## 0.2.0

### Breaking Changes
- `TimeSpanPipeline` is now **generative**:
  transforms map `TimeSpan -> Iterable[TimeSpan]` instead of returning
  a single `TimeSpan` or `None`.
- `TimeSpanPipeline.apply()` now returns `list[TimeSpan]`.
- Drop semantics have changed:
  returning an empty list now indicates dropping a `TimeSpan`.
- Global Largest Remainder Method (LRM)–based MIDI quantization
  has been removed.

### Added
- **Generative TimeSpan transforms**:
  - `duplicate(n)` – duplicate a TimeSpan into multiple identical spans
  - `split_even(n)` – evenly subdivide a TimeSpan into `n` contiguous parts
  - `split_by(ratios)` – subdivide a TimeSpan according to relative ratios
- **Predicate-based filtering transforms**:
  - `drop_if(predicate)`
  - `keep_if(predicate)`
- Deterministic, per-event MIDI tick quantization
  (`ms_to_ticks_int`).
- Explicit tests guaranteeing MIDI `note_on` / `note_off`
  ordering correctness.
- Updated example demonstrating generative
  `TimeSpanPipeline` usage (1 → N expansion).

### Changed
- `TimeSpanPipeline` documentation updated to reflect
  generative (monadic) semantics.
- MIDI export now favors **local temporal consistency**
  over global timing optimality.
- Core public API has been reduced and clarified.

### Removed
- `gate` and `lift_map` are no longer re-exported from
  `hyperscore.core` (they remain available via
  `time_transforms` for backward compatibility).
- LRM-based MIDI quantization utilities and their tests.

### Notes
- MIDI is treated as a **lossy output format**.
- Structural correctness is enforced at the `TimeSpan`
  level, not at the MIDI level.

## 0.3.0

- Export `TimeSpanTransform` type to make it easier for users to define their own functions.
- Removed the deprecated function (`gate`).
- Add `duplicate_by` and `gate_by` functions.
