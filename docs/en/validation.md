# Validation guide

The automated suite provides repeatable regression coverage. Audio drivers,
perceived sound, latency, and native packaging require manual platform tests.
The complete chronological log is preserved in
[`docs/validacao.md`](../validacao.md) in Portuguese.

## Automated checks

From the active virtual environment:

```bash
python -m pytest -q
python -m compileall -q src tests
git diff --check
```

Current baseline: **87 tests passing**.

## Common functional checklist

1. Start the application and switch between Português and English; restart and
   confirm the selected language was restored.
2. Load `samples/di/clean_guitar.wav`, `samples/captures`, and `samples/ir`.
3. Confirm automatic processing through `DI → NAM → IR`.
4. Switch captures with `Ctrl+←/→` and IRs with `←/→` while playing.
5. Compare A2 Full/Lite and test NAM (`N`) and IR (`B`) bypasses independently.
6. Exercise Play/Pause/Stop/Loop, output device, NAM gain, and master gain.
7. Set favorites, ratings, and notes; restart and confirm persistence.
8. Export both categories and each category alone. Verify no empty directory is
   created and existing destinations are not overwritten.

## Windows 10/11

1. Build with `scripts/build-windows.ps1` on Windows, not WSL. Alternatively,
   use the **Windows portable package** GitHub workflow.
2. Extract the complete ZIP into a clean path without a development venv.
3. Run `AuditionManager.exe` and repeat the common checklist using WASAPI.
4. Confirm the bundled NAM runtime is found and no console-only dependency is
   required.
5. Close during playback and verify a clean process exit.

This platform remains **pending** until tested on a real Windows machine.

## Native Linux

1. Install the packages listed in the [installation guide](installation.md).
2. Test with the distribution's normal PipeWire/PulseAudio/ALSA configuration.
3. Repeat the common checklist and confirm fonts, dialogs, and device selection.

Native Linux remains **pending**; successful WSLg testing does not close it.

## WSL/WSLg baseline

The user confirmed interface, playback, and PortAudio output under Arch WSL after
installing `alsa-plugins` and `pulseaudio-alsa`. This environment is suitable for
fast iteration, but not for final native-Linux or Windows acceptance.

## Release gate

Do not publish a binary release until the Windows package and native Linux run
are validated and third-party license notices are reviewed.
