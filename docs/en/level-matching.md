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

Technical references: [ITU-R BS.1770](https://www.itu.int/rec/R-REC-BS.1770/en)
and [EBU R128](https://tech.ebu.ch/publications/r128).
