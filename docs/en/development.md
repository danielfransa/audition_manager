# Development and architecture

## Environment

`mise.toml` pins Python 3.12.13, creates `.venv`, and exposes three tasks:

```bash
mise run install
mise run test
mise run run
```

A manual venv is documented in the [installation guide](installation.md).
Dependency ranges live in `pyproject.toml`; there is no cross-platform lockfile yet.

## Structure

- `audio/files.py`: WAV loading and validation.
- `audio/ir_processor.py`: offline convolution and resampling.
- `audio/nam.py`: NAM validation and native-renderer orchestration.
- `audio/render_cache.py`: bounded LRU cache and bypass preparation.
- `audio/transport.py`: states, cursor, blocks, and crossfade.
- `audio/output.py`: sounddevice/PortAudio stream.
- `library/scanner.py`: WAV and NAM discovery and metadata.
- `library/repository.py`: SQLite migrations and IR/capture persistence.
- `library/exporter.py`: transactional favorite export.
- `config/settings.py`: per-platform data paths.
- `config/preferences.py`: atomic JSON preferences.
- `i18n.py`: runtime Portuguese/English message catalog.
- `ui/main_window.py`: window and worker coordination.
- `main.py`: application composition and logging.

PySide6 provides the UI, NumPy represents samples, SciPy handles convolution
and resampling, soundfile reads WAV, sounddevice outputs audio, and SQLite stores
library metadata. Responsibilities and dependencies are separated according to
SOLID and Clean Code without introducing abstractions before a concrete need.

## Tests

```bash
python -m pytest
python -m compileall -q src tests
git diff --check
```

Tests create temporary WAV files and use fake audio output. They cover DSP,
scanning, database migrations, export, preferences, transport, i18n, and the
offscreen Qt interface. They cannot confirm an OS driver, audible output, or
hardware latency.

## Current technical limits

- Mono/stereo WAV up to 192 kHz, DI up to 300 seconds, and IR up to 2 seconds.
- DI, IR, capture output, and final render are held in memory during processing.
- IRs are resampled to the signal; their complete tail is included in output.
- Peaks above 0.95 are attenuated without perceptual loudness normalization.
- NAM gain is applied after the capture and before the IR. The meter measures
  processed peak before master output gain.
- A2 Full passes `--slim 1.0`; A2 Lite passes `--slim 0.0`; legacy models do not
  receive `--slim`.
- Position counts frames sent to the device and can lead audible playback by one
  buffer. Seeking through the position bar is not supported.
- Crossfade requires matching channel counts; mono/stereo changes reopen stream.
- Scanning is asynchronous after initial enumeration; cancellation occurs
  between files.
- Removed files disappear from the UI, but their metadata stays in SQLite.

## Process and version control

Each increment records a decision, updates roadmap and validation, runs relevant
checks, and ends in a reviewable commit. Development happens on `develop`;
virtual environments, application data, and personal audio stay outside Git.

The Portuguese [historical validation log](../validacao.md) retains the complete
WSL/WSLg investigation and each incremental result. Current information is in
the [status](status.md), [validation](validation.md), and
[decision register](decisions.md).
