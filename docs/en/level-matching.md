# Fair level comparison

This document defines how Audition Manager will reduce loudness bias while
comparing NAM captures and IRs. “Level matching” means gain adjustment; it does
not equalize bass, mids, or treble.

## Current implementation

The application already:

- reads NAM `metadata.loudness`, `input_level_dbu`, and `output_level_dbu`;
- provides **Match volume automatically**, disabled by default;
- uses NAM loudness to move the capture toward a -18 dB target;
- bounds compensation between -24 and +12 dB;
- keeps manual NAM gain separate and peak protection active.

This improves comparisons between captures with compatible metadata, but does
not account for level changes caused by an IR or the specific DI content. It is
therefore not the final normalization method.

## What LUFS means

LUFS means *Loudness Units relative to Full Scale*. Peak dBFS only observes the
largest sample; LUFS estimates perceived level over time. Equal-peak signals can
still sound very different because of duration, density, and frequency content.

Audition Manager measures the complete processed DI loop. BS.1770 applies
frequency weighting (K-weighting), combines channel energy, and gates very quiet
sections so long pauses do not make a capture appear artificially quieter.

- **Peak dBFS:** maximum digital amplitude, used for clipping protection.
- **RMS:** a simple average-energy measurement without the selected perceptual
  weighting and gating.
- **Integrated LUFS:** loudness estimate across the complete loop and the app's
  primary comparison measurement.
- **LU:** relative loudness difference; a 3 dB gain change is approximately a
  3 LU change for this matching operation.

## Why -18 LUFS

`-18 LUFS` is the project's internal comparison target, not EBU R128's broadcast
delivery recommendation. It stays close to normalization conventions used in
the NAM ecosystem and leaves headroom below 0 dBFS for guitar transients.

```text
compensation in dB = -18 LUFS - measured integrated loudness
```

A chain at `-12 LUFS` receives `-6 dB`; one at `-22 LUFS` receives `+4 dB`.
Correction is bounded to `-24/+12 dB`, manual gain remains separate, and the
checkbox always allows original output-level differences to be heard.

## Measurement implemented for the next alpha

The application now measures the actual selected chain output:

```text
reference DI → optional NAM → optional IR → measurement → compensation → peak protection
```

1. Render without automatic compensation and before final peak protection.
2. Measure integrated loudness using the ITU-R BS.1770/EBU R128 family, including
   gating so pauses in the DI do not artificially lower the result.
3. Calculate the difference from a -18 LUFS target.
4. Bound correction between -24 and +12 dB.
5. Apply correction, then user-selected manual gain, then clipping protection.
6. Display the method, measured loudness, calculated correction, and any limit.

Peak is not the primary measurement because equal peaks can have very different
perceived loudness. This version has no RMS fallback. Empty, silent, too-short,
or non-finite audio uses NAM metadata when available and otherwise receives
0 dB; both outcomes are identified and cached.

## Cache, UI, and acceptance

SQLite measurements will be keyed by DI, optional NAM, optional IR, A2 Full/Lite
mode, algorithm version, and target. File identity changes invalidate the cache.
The UI will distinguish measured full-chain values, NAM metadata estimates,
unavailable matching, and bounded corrections. Users can always disable matching
to hear real output-level differences.

Acceptance covers NAM with and without metadata, IR-only, NAM-only, and NAM + IR;
repeatability; cache reuse and invalidation; no timbre change; and a clear
separation between loudness measurement and peak protection.

## References used

- [ITU-R BS.1770](https://www.itu.int/rec/R-REC-BS.1770/en)
- [EBU R128](https://tech.ebu.ch/publications/r128)
- [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm)
- [NAM file specification](https://github.com/sdatkinson/neural-amp-modeler/blob/main/docs/source/model-file.rst)
- [Official NeuralAmpModeler plugin implementation](https://github.com/sdatkinson/NeuralAmpModelerPlugin/blob/main/NeuralAmpModeler/NeuralAmpModeler.cpp)
