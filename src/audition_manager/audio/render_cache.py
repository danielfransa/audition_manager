"""Bounded session cache, owned by the single rendering worker at a time."""

from collections import OrderedDict
from collections.abc import Callable
from pathlib import Path

from audition_manager.audio.files import AudioBuffer, load_wav
from audition_manager.audio.ir_processor import limit_peak


def file_identity(path: Path) -> tuple[Path, int, int, int]:
    resolved = path.resolve()
    stat = resolved.stat()
    return resolved, stat.st_mtime_ns, stat.st_ctime_ns, stat.st_size


class RenderCache:
    def __init__(self, max_bytes: int = 128 * 1024 * 1024, max_entries: int = 4) -> None:
        self.max_bytes = max_bytes
        self.max_entries = max_entries
        self._items: OrderedDict[tuple, AudioBuffer] = OrderedDict()
        self.bytes_used = 0

    def render(
        self, di: Path, ir: Path | None,
        renderer: Callable[[Path, Path], AudioBuffer],
    ) -> AudioBuffer:
        key = (file_identity(di), file_identity(ir) if ir else None)
        if key in self._items:
            self._items.move_to_end(key)
            return self._items[key]
        audio = renderer(di, ir) if ir else limit_peak(load_wav(di))
        size = audio.samples.nbytes
        # Do not reuse results if a file changed while it was being read.
        current = (file_identity(di), file_identity(ir) if ir else None)
        if key != current or size > self.max_bytes or self.max_entries <= 0:
            return audio
        while self._items and (
            self.bytes_used + size > self.max_bytes or len(self._items) >= self.max_entries
        ):
            _, removed = self._items.popitem(last=False)
            self.bytes_used -= removed.samples.nbytes
        self._items[key] = audio
        self.bytes_used += size
        return audio
