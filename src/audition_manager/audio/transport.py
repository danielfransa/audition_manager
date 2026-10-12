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
    def __init__(self, crossfade_seconds: float = 0.01) -> None:
        if crossfade_seconds < 0:
            raise ValueError("A duração do crossfade não pode ser negativa.")
        self._lock = Lock()
        self._crossfade_seconds = crossfade_seconds
        self._audio: AudioBuffer | None = None
        self._position = 0
        self._state = PlaybackState.EMPTY
        self._loop = False
        self._fade_old: NDArray[np.float32] | None = None
        self._fade_new_weights: NDArray[np.float32] | None = None
        self._fade_position = 0

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
            self._clear_crossfade()

    def replace(self, audio: AudioBuffer) -> None:
        """Swap a rendered track atomically while retaining its playback cursor."""
        with self._lock:
            if self._audio is None or audio.sample_rate != self._audio.sample_rate:
                raise ValueError("A troca contínua requer a mesma taxa de amostragem.")
            if len(audio.samples) == 0:
                raise ValueError("O áudio deve conter amostras.")
            if audio.samples.shape[1] != self._audio.samples.shape[1]:
                raise ValueError("O crossfade requer o mesmo número de canais.")
            if self._state in {PlaybackState.PLAYING, PlaybackState.PAUSED}:
                self._prepare_crossfade(self._audio)
            else:
                self._clear_crossfade()
            self._audio = audio
            self._position = min(self._position, len(audio.samples))

    def clear(self) -> None:
        with self._lock:
            self._audio = None
            self._position = 0
            self._state = PlaybackState.EMPTY
            self._clear_crossfade()

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
            self._clear_crossfade()

    def fill(self, output: NDArray[np.float32]) -> bool:
        """Fill a device block; return True after copying the final frame."""
        output.fill(0)
        with self._lock:
            if self._audio is None or self._state != PlaybackState.PLAYING:
                return False
            samples = self._audio.samples
            written = 0
            finished = False
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
                        finished = True
                        break
            self._apply_crossfade(output)
            return finished

    def _prepare_crossfade(self, old_audio: AudioBuffer) -> None:
        frame_count = min(
            round(self._crossfade_seconds * old_audio.sample_rate),
            len(old_audio.samples),
        )
        if frame_count < 2:
            self._clear_crossfade()
            return
        old = np.zeros(
            (frame_count, old_audio.samples.shape[1]), dtype=np.float32
        )
        if self._loop:
            indices = (np.arange(frame_count) + self._position) % len(old_audio.samples)
            old[:] = old_audio.samples[indices]
        elif self._position < len(old_audio.samples):
            available = min(frame_count, len(old_audio.samples) - self._position)
            old[:available] = old_audio.samples[
                self._position:self._position + available
            ]
        new_weights = np.linspace(0, 1, frame_count, dtype=np.float32)
        old *= (1 - new_weights)[:, np.newaxis]
        self._fade_old = old
        self._fade_new_weights = new_weights
        self._fade_position = 0

    def _apply_crossfade(self, output: NDArray[np.float32]) -> None:
        if self._fade_old is None or self._fade_new_weights is None:
            return
        remaining = len(self._fade_old) - self._fade_position
        count = min(len(output), remaining)
        fade_slice = slice(self._fade_position, self._fade_position + count)
        output[:count] *= self._fade_new_weights[fade_slice, np.newaxis]
        output[:count] += self._fade_old[fade_slice]
        self._fade_position += count
        if self._fade_position == len(self._fade_old):
            self._clear_crossfade()

    def _clear_crossfade(self) -> None:
        self._fade_old = None
        self._fade_new_weights = None
        self._fade_position = 0
