# Decision register

Architecture decision records (ADRs) are historical snapshots written with each
increment. Older constraints may have been resolved; read the
[current status](status.md) first. The original records are preserved in
Portuguese, while this register provides their English titles and outcomes.

| ADR | Decision and outcome |
| --- | --- |
| [0001](../decisions/0001-fundacao.md) | Foundation and first vertical slice: establish the layered desktop application and audit one small delivery at a time. |
| [0002](../decisions/0002-linux-wsl-fontes.md) | Linux, WSL, and fonts: make Linux a supported target and choose an installed, readable Qt font. |
| [0003](../decisions/0003-saida-wslg.md) | WSLg audio bridge: use ALSA PulseAudio plugins and provide actionable device errors. |
| [0004](../decisions/0004-player.md) | Playback transport: own position, pause, stop, loop, and stream state outside global sounddevice helpers. |
| [0005](../decisions/0005-troca-ir-git.md) | Automatic IR switching and Git: preserve playback position, discard stale work, and version small increments. |
| [0006](../decisions/0006-bypass-cache.md) | Bypass, shortcuts, and session cache: keep interaction fast with a bounded render cache. |
| [0007](../decisions/0007-biblioteca-sqlite.md) | SQLite library: persist metadata, favorites, ratings, and notes without copying audio into the database. |
| [0008](../decisions/0008-dispositivo-ganho.md) | Output device and gain: expose PortAudio device choice and safe master attenuation. |
| [0009](../decisions/0009-filtros-notas.md) | Library filters and notes: separate browsing metadata from audio processing. |
| [0010](../decisions/0010-exportacao-favoritos.md) | Favorite export: copy selected files transactionally while preserving relative structure and never overwriting a destination. |
| [0011](../decisions/0011-scan-assincrono.md) | Asynchronous cancellable scan: keep Qt responsive and reject obsolete scan results. |
| [0012](../decisions/0012-preferencias.md) | Application preferences: use atomic JSON writes and safe fallbacks for unavailable resources. |
| [0013](../decisions/0013-crossfade.md) | Short IR crossfade: use a 10 ms linear transition when stream formats match. |
| [0014](../decisions/0014-nam-a2-am4-windows.md) | NAM A2 first, AM4DATA later, and Windows packaging: validate an official open runtime before proprietary conversion work. |
| [0015](../decisions/0015-estrelas-clicaveis.md) | Clickable ratings: make the five-star control directly editable while preserving keyboard shortcuts. |
| [0016](../decisions/0016-readme-instalacao.md) | Public README and multiplatform installation: separate contributor detail from user onboarding. |
| [0017](../decisions/0017-seletor-pasta-irs.md) | IR folder dialog: show WAV contents before the user confirms the directory. |
| [0018](../decisions/0018-audios-exemplo.md) | Repository samples: include redistributable test assets and exclude Windows Zone.Identifier streams. |
| [0019](../decisions/0019-cadeia-nam-a2-ir.md) | Offline NAM A2 plus IR chain: isolate the native renderer and preserve IR-only operation. |
| [0020](../decisions/0020-biblioteca-capturas.md) | NAM capture library: give captures independent search, metadata, navigation, and preferences. |
| [0021](../decisions/0021-comparacao-nivel-nam.md) | NAM comparison level: add capture gain, peak metering, and end-to-end peak protection. |
| [0022](../decisions/0022-exportacao-favoritos-nam-ir.md) | Joint favorite export: let users include captures, IRs, or both without empty category folders. |
| [0023](../decisions/0023-compatibilidade-nam-full-lite-legado.md) | A2 Full/Lite and legacy NAM: pass slimming only to A2 and expose detected architecture/version. |
| [0024](../decisions/0024-i18n-aplicacao.md) | Application i18n: use a small runtime catalog, immediate language switching, and persisted locale. |
| [0025](../decisions/0025-documentacao-publica-bilingue.md) | Bilingual public docs: keep the root README short and route readers to complete PT/EN guides. |
| [0026](../decisions/0026-documentacao-tecnica-bilingue.md) | Bilingual technical docs: publish current English references while keeping immutable Portuguese history and bilingual ADR navigation. |
| [0027](../decisions/0027-build-windows-automatizado.md) | Verifiable Windows build: smoke-test the frozen executable and generate a short-lived ZIP through a read-only manual workflow. |
| [0028](../decisions/0028-polimento-windows.md) | Windows polish: balance capture/IR list space, hide the native renderer console, and package only Git-tracked samples. |
