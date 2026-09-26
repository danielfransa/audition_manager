"""PortAudio adapter. Device access is deferred until playback."""

import os
import sys
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.transport import PlaybackState, PlaybackTransport

if TYPE_CHECKING:
    import sounddevice as sd


class AudioOutput:
    def __init__(self) -> None:
        self.transport = PlaybackTransport()
        self._stream: "sd.OutputStream | None" = None

    def play(self, audio: AudioBuffer | None = None, *, loop: bool | None = None) -> None:
        import sounddevice as sd

        try:
            sd.query_devices(kind="output")
        except sd.PortAudioError as error:
            message = (
                "Não foi possível acessar uma saída de áudio padrão. "
                "Verifique o dispositivo de saída nas configurações de som do sistema."
            )
            if sys.platform == "linux" and "wsl" in os.environ.get("PULSE_SERVER", "").lower():
                message += (
                    " No Arch Linux com WSLg, instale alsa-plugins e pulseaudio-alsa "
                    "(sudo pacman -S --needed alsa-plugins pulseaudio-alsa). "
                    "Confira a conexão com pactl info e reinicie o aplicativo."
                )
            raise RuntimeError(f"{message}\n\nDetalhe técnico: {error}") from error

        if audio is not None:
            self.close()
            self.transport.load(audio)
            try:
                self._stream = sd.OutputStream(
                    samplerate=audio.sample_rate,
                    channels=audio.samples.shape[1],
                    dtype="float32",
                    callback=self._callback,
                )
            except Exception:
                self.transport.clear()
                raise
        if self._stream is None:
            raise ValueError("Carregue um áudio antes de reproduzir.")
        if loop is not None:
            self.transport.set_loop(loop)
        if self._stream.active and self.transport.snapshot()[0] == PlaybackState.PLAYING:
            return
        self._stream.stop()
        self.transport.play()
        try:
            self._stream.start()
        except Exception:
            self.transport.pause()
            raise

    def _callback(
        self, outdata: NDArray[np.float32], frames: int, time: object, status: object
    ) -> None:
        import sounddevice as sd

        if self.transport.fill(outdata):
            raise sd.CallbackStop

    def pause(self) -> None:
        if self._stream is not None:
            self._stream.stop()
        self.transport.pause()

    def set_loop(self, enabled: bool) -> None:
        self.transport.set_loop(enabled)

    def stop(self) -> None:
        if self._stream is not None:
            self._stream.abort()
        self.transport.stop()

    def close(self) -> None:
        if self._stream is not None:
            self._stream.close()
            self._stream = None
        self.transport.clear()
