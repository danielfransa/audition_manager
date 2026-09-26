"""Playback cursor and transitions, independent of Qt and PortAudio."""

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

    def load(self, audio: AudioBuffer) -> None:
        if len(audio.samples) == 0 or audio.sample_rate <= 0:
            raise ValueError("O áudio deve conter amostras e uma taxa válida.")
        with self._lock:
            self._audio = audio
            self._position = 0
            self._state = PlaybackState.STOPPED

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
