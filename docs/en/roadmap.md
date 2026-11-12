# Execution roadmap

Work is delivered in small, auditable increments. Each increment includes code
or documentation, appropriate checks, a decision record, and a review stop.
Windows and Linux are targets; WSL/WSLg is the fast feedback environment.

## Completed foundation and IR MVP

- Python 3.12/mise/venv foundation, MIT licensing, PySide6 UI, and layered audio,
  library, configuration, and interface modules.
- WAV DI and recursive IR selection, offline convolution, playback transport,
  bypass, automatic switching, bounded cache, and short crossfade.
- SQLite metadata, favorites, clickable ratings, notes, search, filters, and
  application preferences.
- Output-device and gain controls, asynchronous scanning, and organized export.

Native Linux and real-Windows acceptance remain open platform checks.

## Completed NAM A2 increment

- Official `NeuralAmpModelerCore` renderer isolated behind a capture processor.
- A2 `SlimmableContainer` validation, Full/Lite selection, and supported legacy
  WaveNet, LSTM, ConvNet, Linear, and Sequential models.
- Offline `DI → NAM → IR` processing with independent bypasses and NAM gain.
- Capture library, metadata, filters, ratings, notes, preferences, and export.

Listening and compilation are validated on Windows; native Linux remains open.

## Internationalization

1. Portuguese/English runtime catalog, selector, immediate switching, and
   persistence — **implemented**.
2. Short bilingual public README and complete PT/EN installation and user guides
   — **implemented**.
3. Bilingual technical status, development, validation, roadmap, and decision
   navigation — **implemented for review**.

## Next stages (approved order)

### 1. Level-matched comparison — next alpha

Deliver each item as a separate, auditable increment, then publish a new alpha
after practical validation of the complete set:

1. Read `loudness`, `input_level_dbu`, and `output_level_dbu` from NAM metadata,
   persist them in SQLite, and display them without changing the audio.
2. Add optional automatic level matching. Turning it off must preserve the
   original level and the existing manual gain workflow.
3. For NAM files without loudness metadata and for IRs, measure a reference
   level with the DI loop and cache the resulting compensation in SQLite until
   either the source file or reference changes.

The feature must clearly indicate when compensation is active, retain peak
protection, and never silently overwrite the source's original level.

### 2. Live guitar input

Research WASAPI/ASIO, buffers, rates, concurrency, and latency before changing
the DSP architecture. The exploratory target is 48 kHz at 64/128 frames. Audio
callbacks must not perform I/O, model loading, or large allocation.

### 3. Blind comparison

Hide filenames, pack/source information, favorites, and previous ratings during
comparison. Reveal them after the user submits a new rating or leaves blind
mode. This stage is intentionally scheduled after live input is consolidated.

### 4. Windows installer

The portable Windows ZIP has already been built, published, and validated on a
real Windows machine. Keep it as the distribution and diagnostic format until
the new alpha, live input, and blind comparison are consolidated. Then evaluate
shortcuts, uninstall support, upgrades, third-party notices, code signing, and
SmartScreen behavior.

### Later: AM4DATA, BlackBox, and IR-Box

Treat each device and format independently. Do not invent proprietary parsers or
USB/MIDI/SysEx protocols. Initially use M-VAVE's official NAM-to-AM4DATA
converter; implement direct transfer only with reliable documentation.

### Library at scale

Evaluate hundreds of captures/IRs, reproducible dependency resolution, and
licenses for all redistributed assets and binary dependencies.

## Main risks

- Memory and preprocessing time grow with duration, channels, and sample rate.
- Continuous switching requires correct synchronization of results and cursor.
- Different rates, IR levels, and convolution tails affect comparison and loops.
- Qt, PortAudio, drivers, and the native NAM runtime need real platform tests.
- MIT covers project code, not the licenses of dependencies or sample assets.

The authoritative Portuguese execution history remains in [`PLAN.md`](../../PLAN.md).
