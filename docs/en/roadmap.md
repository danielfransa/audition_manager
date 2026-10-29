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

Listening and compilation still need native Linux and Windows validation.

## Internationalization

1. Portuguese/English runtime catalog, selector, immediate switching, and
   persistence — **implemented**.
2. Short bilingual public README and complete PT/EN installation and user guides
   — **implemented**.
3. Bilingual technical status, development, validation, roadmap, and decision
   navigation — **implemented for review**.

## Next stages

### Windows distribution

Build and validate the portable package on real Windows with both languages and
the NAM runtime. Evaluate installer, signing, and GitHub Releases afterward.
The PowerShell build, frozen-executable smoke test, and manual GitHub Actions
workflow are implemented; a successful artifact and listening test are pending.

### Live guitar input

Research WASAPI/ASIO, buffers, rates, concurrency, and latency before changing
the DSP architecture. The exploratory target is 48 kHz at 64/128 frames. Audio
callbacks must not perform I/O, model loading, or large allocation.

### AM4DATA, BlackBox, and IR-Box

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
