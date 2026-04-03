"""
Audio feedback engine for Neural Speed Academy.

Synthesizes short tones using QAudioSink + raw PCM data.
Gracefully degrades to no-ops if PyQt6.QtMultimedia is unavailable.
"""
from __future__ import annotations

import math
import struct
from typing import Optional

# Attempt to import multimedia — fall back silently if missing
try:
    from PyQt6.QtMultimedia import QAudioFormat, QAudioSink, QMediaDevices
    from PyQt6.QtCore import QBuffer, QIODevice, QByteArray
    _HAS_AUDIO = True
except ImportError:
    _HAS_AUDIO = False


# --- Tone synthesis ---

_SAMPLE_RATE = 44100
_CHANNELS = 1
_SAMPLE_SIZE = 16  # bits


def _generate_tone(
    frequency: float,
    duration_ms: int,
    volume: float = 0.5,
    fade_ms: int = 10,
) -> bytes:
    """Generate a sine wave as signed 16-bit PCM data."""
    n_samples = int(_SAMPLE_RATE * duration_ms / 1000)
    fade_samples = int(_SAMPLE_RATE * fade_ms / 1000)
    samples = []
    for i in range(n_samples):
        t = i / _SAMPLE_RATE
        val = math.sin(2 * math.pi * frequency * t) * volume

        # Fade in/out to avoid clicks
        if i < fade_samples:
            val *= i / fade_samples
        elif i > n_samples - fade_samples:
            val *= (n_samples - i) / fade_samples

        samples.append(int(val * 32767))
    return struct.pack(f"<{len(samples)}h", *samples)


def _generate_sweep(
    freq_start: float,
    freq_end: float,
    duration_ms: int,
    volume: float = 0.5,
    fade_ms: int = 10,
) -> bytes:
    """Generate a frequency sweep (rising or falling tone)."""
    n_samples = int(_SAMPLE_RATE * duration_ms / 1000)
    fade_samples = int(_SAMPLE_RATE * fade_ms / 1000)
    samples = []
    for i in range(n_samples):
        t = i / _SAMPLE_RATE
        progress = i / n_samples
        freq = freq_start + (freq_end - freq_start) * progress
        val = math.sin(2 * math.pi * freq * t) * volume

        if i < fade_samples:
            val *= i / fade_samples
        elif i > n_samples - fade_samples:
            val *= (n_samples - i) / fade_samples

        samples.append(int(val * 32767))
    return struct.pack(f"<{len(samples)}h", *samples)


def _generate_chime(volume: float = 0.5) -> bytes:
    """Two-note ascending chime for exercise completion."""
    note1 = _generate_tone(523.25, 120, volume)  # C5
    gap = b"\x00\x00" * int(_SAMPLE_RATE * 0.04)  # 40ms silence
    note2 = _generate_tone(659.25, 180, volume)   # E5
    return note1 + gap + note2


# --- Pre-built tone definitions ---

_TONE_DEFS = {
    "correct":    lambda vol: _generate_sweep(400, 600, 100, vol),
    "incorrect":  lambda vol: _generate_sweep(400, 250, 150, vol),
    "tick":       lambda vol: _generate_tone(800, 40, vol * 0.6),
    "completion": lambda vol: _generate_chime(vol),
}


class AudioEngine:
    """Plays synthesized audio cues. Thread-safe singleton pattern."""

    def __init__(self):
        self._enabled: bool = True
        self._volume: float = 0.5  # 0.0 – 1.0
        self._sink: Optional[object] = None
        self._buf: Optional[object] = None
        self._ba: Optional[object] = None
        self._format: Optional[object] = None
        self._cache: dict[str, bytes] = {}

        if _HAS_AUDIO:
            fmt = QAudioFormat()
            fmt.setSampleRate(_SAMPLE_RATE)
            fmt.setChannelCount(_CHANNELS)
            fmt.setSampleFormat(QAudioFormat.SampleFormat.Int16)
            self._format = fmt

    @property
    def enabled(self) -> bool:
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = value

    @property
    def volume(self) -> float:
        return self._volume

    @volume.setter
    def volume(self, value: float) -> None:
        self._volume = max(0.0, min(1.0, value))
        self._cache.clear()  # regenerate tones at new volume

    def play(self, tone_name: str) -> None:
        """Play a named tone. No-op if audio is disabled or unavailable."""
        if not self._enabled or not _HAS_AUDIO or not self._format:
            return
        if tone_name not in _TONE_DEFS:
            return

        # Use cached PCM data or generate
        if tone_name not in self._cache:
            self._cache[tone_name] = _TONE_DEFS[tone_name](self._volume)

        pcm_data = self._cache[tone_name]

        try:
            # Stop any previous playback
            if self._sink is not None:
                self._sink.stop()
                self._sink = None
            if self._buf is not None:
                self._buf.close()
                self._buf = None

            ba = QByteArray(pcm_data)
            buf = QBuffer()
            buf.setData(ba)
            if not buf.open(QIODevice.OpenModeFlag.ReadOnly):
                return

            sink = QAudioSink(self._format)

            # Keep references alive for entire playback duration
            self._sink = sink
            self._buf = buf
            self._ba = ba  # prevent QByteArray garbage collection

            def _on_state(state):
                from PyQt6.QtMultimedia import QAudio
                if state == QAudio.State.IdleState:
                    sink.stop()

            sink.stateChanged.connect(_on_state)
            sink.start(buf)
        except Exception:
            pass  # audio failure is never fatal


# Module-level singleton
audio_engine = AudioEngine()
