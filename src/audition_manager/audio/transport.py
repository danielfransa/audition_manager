"""Playback cursor and transitions, independent of Qt and PortAudio."""

from dataclasses import dataclass
from enum import StrEnum
from threading import Lock

import numpy as np
from numpy.typing import NDArray

from audition_manager.audio.files import AudioBuffer


class PlaybackState(StrEnum):
    EMPTY = "empty"
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    FINISHED = "finished"


@dataclass(frozen=True)
class PlaybackCheckpoint:
    audio: AudioBuffer
    state: PlaybackState
    position: float
    loop: bool


class PlaybackTransport:
    def __init__(self) -> None:
        self._lock = Lock()
        self._audio: AudioBuffer | None = None
        self._position = 0
        self._state = PlaybackState.EMPTY
        self._loop = False

    def snapshot(self) -> tuple[PlaybackState, float, float]:
        with self._lock:
            if self._audio is None:
                return self._state, 0.0, 0.0
            rate = self._audio.sample_rate
            return self._state, self._position / rate, len(self._audio.samples) / rate

    def checkpoint(self) -> PlaybackCheckpoint | None:
        with self._lock:
            if self._audio is None:
                return None
            return PlaybackCheckpoint(
                self._audio, self._state,
                self._position / self._audio.sample_rate, self._loop,
            )

    def load(
        self, audio: AudioBuffer, *, position: float = 0,
        state: PlaybackState = PlaybackState.STOPPED,
    ) -> None:
        if len(audio.samples) == 0 or audio.sample_rate <= 0:
            raise ValueError("O áudio deve conter amostras e uma taxa válida.")
        with self._lock:
            self._audio = audio
            self._position = min(int(position * audio.sample_rate), len(audio.samples))
            self._state = state

    def replace(self, audio: AudioBuffer) -> None:
        """Swap a rendered track atomically while retaining its playback cursor."""
        with self._lock:
            if self._audio is None or audio.sample_rate != self._audio.sample_rate:
                raise ValueError("A troca contínua requer a mesma taxa de amostragem.")
            if len(audio.samples) == 0:
                raise ValueError("O áudio deve conter amostras.")
            self._audio = audio
            self._position = min(self._position, len(audio.samples))

    def clear(self) -> None:
        with self._lock:
            self._audio = None
            self._position = 0
            self._state = PlaybackState.EMPTY

    def set_loop(self, enabled: bool) -> None:
        with self._lock:
            self._loop = enabled

    def play(self) -> None:
        with self._lock:
            if self._audio is None:
                raise ValueError("Carregue um áudio antes de reproduzir.")
            if self._state == PlaybackState.FINISHED:
                self._position = 0
            self._state = PlaybackState.PLAYING

    def pause(self) -> None:
        with self._lock:
            if self._state == PlaybackState.PLAYING:
                self._state = PlaybackState.PAUSED

    def stop(self) -> None:
        with self._lock:
            self._position = 0
            self._state = PlaybackState.STOPPED if self._audio is not None else PlaybackState.EMPTY

    def fill(self, output: NDArray[np.float32]) -> bool:
        """Fill a device block; return True after copying the final frame."""
        output.fill(0)
        with self._lock:
            if self._audio is None or self._state != PlaybackState.PLAYING:
                return False
            samples = self._audio.samples
            written = 0
            while written < len(output):
                count = min(len(output) - written, len(samples) - self._position)
                output[written:written + count] = samples[self._position:self._position + count]
                self._position += count
                written += count
                if self._position == len(samples):
                    if self._loop:
                        self._position = 0
                    else:
                        self._state = PlaybackState.FINISHED
                        return True
            return False
