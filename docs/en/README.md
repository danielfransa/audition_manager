# Audition Manager — English

Audition Manager is an open-source desktop application for guitarists to audition,
compare, and organize IRs and NAM captures before copying them to pedalboards,
modelers, or other libraries.

## Current status

Available now:

- WAV DI selection and recursive IR scanning;
- automatic offline playback when switching an IR or capture;
- NAM A2 Full/Lite captures and compatible legacy models;
- `DI → NAM → IR` chain with independent bypass controls;
- search, filters, favorites, ratings, and notes for IRs and captures;
- NAM gain, master gain, peak meter, Loop, Play/Pause, and Stop;
- favorite export into separate `Captures` and `IRs` folders;
- Portuguese and English interface;
- two DIs, four IRs, and two MIT-licensed NAM captures for testing.

The portable package is validated on real Windows hardware. The next alpha will
focus on level-matched comparison, followed by live guitar input, blind
comparison, and finally the Windows installer. Direct BlackBox/IR-Box transfer
remains future research.

## Getting started

1. Follow the [Linux, Windows, or WSL installation guide](installation.md).
2. Open the [user guide](usage.md).
3. Use the files under [`samples/`](../../samples/README.md) for the first test.

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| Space | Play/Pause |
| B | Bypass IR |
| N | Bypass NAM capture |
| F | Favorite IR |
| 1–5 | Rate IR |
| 0 | Clear IR rating |
| ←/→ | Navigate IRs |
| Ctrl+←/→ | Navigate captures |

## Documentation

- [Installation](installation.md)
- [User guide](usage.md)
- [Current status](status.md)
- [Roadmap](roadmap.md)
- [Development and architecture](development.md)
- [Validation](validation.md)
- [Fair level-comparison design](level-matching.md)
- [Next alpha draft](../releases/v0.2.0-alpha.md)
- [Decision register](decisions.md)

## License

The code is released under the [MIT license](../../LICENSE). Dependencies, IRs,
captures, and other audio files keep their own licenses. Review the documentation
under [`samples/`](../../samples/README.md) before redistributing examples.
