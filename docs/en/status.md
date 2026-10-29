# Current project status

Updated on **October 29, 2026**. This is the current summary. Decision records
and older sections of the validation log preserve the history and may describe
limitations that have since been resolved.

## Delivered

- Python/PySide6 desktop application targeting Windows and Linux, exercised by
  the user under WSL/WSLg.
- Recursive, asynchronous, cancellable IR scanning and WAV DI selection.
- Offline convolution, resampling, peak protection, position, playback,
  Play/Pause/Stop/Loop, and bypass.
- Automatic IR switching, bounded cache, and 10 ms linear crossfade when the
  stream format remains unchanged.
- SQLite libraries for IRs and NAM captures, with search, filters, favorites,
  clickable 0–5 ratings, keyboard shortcuts, and notes.
- Organized favorite export into separate `Captures` and `IRs` directories,
  preserving source subdirectories and omitting unselected or empty categories.
- Output-device selection, master gain, and WSLg-specific diagnostics.
- Atomic JSON preferences for paths, device, gains, Loop, selections, and
  language, with fallbacks for missing resources.
- `mise`/venv setup, MIT license, technical documentation, and incremental Git
  history on `develop`.
- Two DIs, four IRs, and two MIT-licensed RiffSmith NAM A2 captures for testing.
- Portuguese/English interface with immediate switching and persistence.
- PowerShell script for building a portable PyInstaller package on Windows.
- GitHub Actions workflow that builds on `windows-2022` and
  smoke-tests imports and the bundled NAM runtime before uploading the ZIP.
- Windows package with tracked samples, hidden NAM renderer console, and
  practical minimum space for both capture and IR lists.
- Offline `DI → NAM → IR` chain with independent NAM and IR bypasses.
- Independent NAM gain, processed peak meter, and peak protection.
- A2 Full/Lite modes and structural support for legacy WaveNet, LSTM, ConvNet,
  Linear, and Sequential NAM models.

## Current verification

- Automated suite: **89 tests passing**.
- Bytecode compilation and `git diff --check`: clean in the latest delivery.
- Interface, playback, and PortAudio output confirmed under WSL/WSLg.
- Current integration branch: `develop`.

## NAM A2 in progress

- A2 is the first supported amplifier-capture format.
- `NeuralAmpModelerCore` runs as an isolated native process and is pinned to
  commit `0b3d3c9`; its official renderer loaded a real A2 capture under WSL.
- The application validates `SlimmableContainer`, converts DI audio to mono at
  48 kHz, and combines the NAM result with the selected IR.
- Compilation and listening still require validation on native Linux and a real
  Windows machine. The PyTorch training package is intentionally not bundled.

## BlackBox and AM4DATA

M-VAVE's official software documents NAM-to-AM4DATA conversion. The current plan
is to export and organize `.nam` files in Audition Manager, then use the official
converter. Direct AM4DATA generation and BlackBox/IR-Box transfer require
reliable format or protocol documentation and are not implemented.

## Pending validation

- Build `AuditionManager-Windows-x64.zip` on Windows and validate UI, WASAPI,
  preferences, export, NAM runtime, and shutdown.
- Run the complete native-Linux checklist; WSLg is not a substitute.
- Consider an installer and signing only after the portable package is approved.
- Evaluate clickable ratings and crossfade during regular listening.
- Review third-party notices and redistributed licenses before binary releases.

## Tracking references

- [Roadmap](roadmap.md)
- [Development and architecture](development.md)
- [Validation](validation.md)
- [Decision register](decisions.md)
- [Installation](installation.md) and [user guide](usage.md)
