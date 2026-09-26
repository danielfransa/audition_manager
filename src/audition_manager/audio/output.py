"""PortAudio adapter. Device access is deferred until playback."""

import os
import sys
from dataclasses import dataclass
from math import pow
from typing import TYPE_CHECKING

import numpy as np
from numpy.typing import NDArray

from audition_manager.audio.files import AudioBuffer
from audition_manager.audio.transport import PlaybackState, PlaybackTransport

if TYPE_CHECKING:
    import sounddevice as sd


@dataclass(frozen=True)
class OutputDevice:
    index: int
    name: str
    host_api: str


class AudioOutput:
    def __init__(self) -> None:
        self.transport = PlaybackTransport()
        self._stream: "sd.OutputStream | None" = None
        self._device: int | None = None
        self._gain_linear = 1.0

    def list_devices(self) -> list[OutputDevice]:
        import sounddevice as sd

        devices = []
        for index, info in enumerate(sd.query_devices()):
            if info["max_output_channels"] <= 0:
                continue
            host_api = sd.query_hostapis(info["hostapi"])["name"]
            devices.append(OutputDevice(index, info["name"], host_api))
        return devices

    @property
    def device(self) -> int | None:
        return self._device

    def set_gain_db(self, gain_db: float) -> None:
        if not -24 <= gain_db <= 0:
            raise ValueError("O ganho deve estar entre -24 e 0 dB.")
        self._gain_linear = pow(10, gain_db / 20)

    def set_device(self, device: int | None) -> None:
        if device == self._device:
            return
        checkpoint = self.transport.checkpoint()
        self._close_stream()
        self._device = device
        if checkpoint is None:
            return
        try:
            self._open_stream(checkpoint.audio)
            self.transport.load(
                checkpoint.audio, position=checkpoint.position, state=checkpoint.state
            )
            self.transport.set_loop(checkpoint.loop)
            if checkpoint.state == PlaybackState.PLAYING:
                self._stream.start()
        except Exception:
            self.transport.load(
                checkpoint.audio, position=checkpoint.position,
                state=PlaybackState.PAUSED,
            )
            self.transport.set_loop(checkpoint.loop)
            raise

    def play(self, audio: AudioBuffer | None = None, *, loop: bool | None = None) -> None:
        import sounddevice as sd

        try:
            sd.query_devices(self._device, kind="output")
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
            self.load(audio)
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

    def load(self, audio: AudioBuffer) -> None:
        self.close()
        self.transport.load(audio)
        try:
            self._open_stream(audio)
        except Exception:
            self.transport.clear()
            raise

    def _open_stream(self, audio: AudioBuffer) -> None:
        import sounddevice as sd

        self._stream = sd.OutputStream(
            samplerate=audio.sample_rate, channels=audio.samples.shape[1],
            dtype="float32", callback=self._callback, device=self._device,
        )

    def replace(self, audio: AudioBuffer) -> None:
        if self._stream is None:
            self.load(audio)
            return
        if (self._stream.channels == audio.samples.shape[1]
                and self._stream.samplerate == audio.sample_rate):
            self.transport.replace(audio)
            return
        # A different channel layout needs a new device stream.
        self._stream.stop()
        state, position, _ = self.transport.snapshot()
        self.load(audio)
        self.transport.load(audio, position=position, state=state)
        if state == PlaybackState.PLAYING:
            try:
                self._stream.start()
            except Exception:
                self.transport.pause()
                raise

    def _callback(
        self, outdata: NDArray[np.float32], frames: int, time: object, status: object
    ) -> None:
        import sounddevice as sd

        finished = self.transport.fill(outdata)
        np.multiply(outdata, self._gain_linear, out=outdata)
        if finished:
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
        self._close_stream()
        self.transport.clear()

    def _close_stream(self) -> None:
        if self._stream is not None:
            self._stream.close()
            self._stream = None
