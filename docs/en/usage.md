# User guide — English

## First test

1. Start with `mise run run` or `audition-manager`.
2. Select **Português** or **English** from the language selector.
3. Click **Open DI WAV** and open `samples/di/clean_guitar.wav`.
4. Click **Select NAM capture folder** and choose `samples/captures`.
5. Select `riffsmith-clean.nam` or `riffsmith-distorted.nam`.
6. Click **Select IR folder** and choose `samples/ir`.
7. Select an IR. Audio is processed as `DI → NAM → IR`.

## Compare tones

- Click or use `Ctrl+←/→` to switch captures.
- Click or use `←/→` to switch IRs.
- Use **A2 Full** for higher fidelity or **A2 Lite** for faster processing.
- Adjust NAM gain to compare captures at similar levels.
- Press `N` to bypass the capture and `B` to bypass the IR.
- The meter shows the processed peak before master output gain.

## Organize the library

IRs and captures have independent search, favorite filter, rating, and notes.
Metadata is stored in the local database; audio files are not copied into it.
The last DI, folders, capture, device, gains, Loop, and language are restored
when the resources are still available.

## Export favorites

1. Mark IRs and captures as favorites.
2. Click **Export favorites…**.
3. Choose where the new folder will be created.
4. Enter its name and select **Captures**, **IRs**, or both.

Only selected categories are created:

```text
Chosen name/
├── Captures/
└── IRs/
```

Empty folders are omitted and an existing destination is never overwritten.

## Current limits

- Processing is offline; live guitar input is not available yet.
- DI files are limited to 5 minutes and IRs to 2 seconds.
- NAM A2 and legacy architectures supported by the runtime are accepted, but
  unusual historical files may still be rejected by NeuralAmpModelerCore.
- Direct pedalboard transfer is not implemented yet.
