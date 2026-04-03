"""
Audio feedback engine for Neural Speed Academy.

Synthesizes short tones as in-memory WAV data.
On Windows, plays via winsound.PlaySound (SND_MEMORY).
On other platforms, falls back to QAudioSink.
"""
from __future__ import annotations

import io
import math
import platform
import struct
import threading
import wave
from typing import Optional

_IS_WINDOWS = platform.system() == "Windows"
_SAMPLE_RATE = 44100

if _IS_WINDOWS:
    import winsound


# --- Tone synthesis (shared across platforms) ---

def _generate_tone(freq: float, duration_ms: int, volume: float = 0.5) -> bytes:
    """Generate a sine wave as signed 16-bit PCM samples."""
    n = int(_SAMPLE_RATE * duration_ms / 1000)
    fade = int(_SAMPLE_RATE * 0.008)
    samples = []
    for i in range(n):
        t = i / _SAMPLE_RATE
        val = math.sin(2 * math.pi * freq * t) * volume
        if i < fade:
            val *= i / fade
        elif i > n - fade:
            val *= (n - i) / fade
        samples.append(int(val * 32767))
    return struct.pack(f"<{n}h", *samples)


def _generate_sweep(f0: float, f1: float, duration_ms: int, volume: float = 0.5) -> bytes:
    """Generate a frequency sweep as signed 16-bit PCM samples."""
    n = int(_SAMPLE_RATE * duration_ms / 1000)
    fade = int(_SAMPLE_RATE * 0.008)
    samples = []
    for i in range(n):
        t = i / _SAMPLE_RATE
        f = f0 + (f1 - f0) * (i / n)
        val = math.sin(2 * math.pi * f * t) * volume
        if i < fade:
            val *= i / fade
        elif i > n - fade:
            val *= (n - i) / fade
        samples.append(int(val * 32767))
    return struct.pack(f"<{n}h", *samples)


def _pcm_to_wav(pcm: bytes) -> bytes:
    """Wrap raw PCM data in a WAV container."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(_SAMPLE_RATE)
        w.writeframes(pcm)
    return buf.getvalue()


# Tone definitions: name -> (pcm_generator_func)
_TONE_DEFS = {
    "correct":    lambda vol: _generate_sweep(400, 600, 80, vol),
    "incorrect":  lambda vol: _generate_sweep(400, 250, 120, vol),
    "tick":       lambda vol: _generate_tone(800, 30, vol * 0.6),
    "completion": lambda vol: (
        _generate_tone(523.25, 100, vol)
        + b"\x00\x00" * int(_SAMPLE_RATE * 0.03)
        + _generate_tone(659.25, 140, vol)
    ),
}

# Non-Windows: try QAudioSink
_HAS_QT_AUDIO = False
if not _IS_WINDOWS:
    try:
        from PyQt6.QtMultimedia import QAudioFormat, QAudioSink, QAudio
        from PyQt6.QtCore import QBuffer, QIODevice, QByteArray
        _HAS_QT_AUDIO = True
    except ImportError:
        pass


class AudioEngine:
    """Plays synthesized audio cues with volume control."""

    def __init__(self):
        self._enabled: bool = True
        self._volume: float = 0.5
        self._cache: dict[str, bytes] = {}
        # QAudioSink state (non-Windows)
        self._sink: Optional[object] = None
        self._buf: Optional[object] = None
        self._ba: Optional[object] = None
        self._format: Optional[object] = None

        if _HAS_QT_AUDIO:
            fmt = QAudioFormat()
            fmt.setSampleRate(_SAMPLE_RATE)
            fmt.setChannelCount(1)
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
        self._cache.clear()

    def play(self, tone_name: str) -> None:
        """Play a named tone. No-op if disabled or unavailable."""
        if not self._enabled or tone_name not in _TONE_DEFS:
            return

        # Cache key includes volume so tones regenerate on volume change
        cache_key = f"{tone_name}_{self._volume:.2f}"
        if cache_key not in self._cache:
            pcm = _TONE_DEFS[tone_name](self._volume)
            if _IS_WINDOWS:
                self._cache[cache_key] = _pcm_to_wav(pcm)
            else:
                self._cache[cache_key] = pcm

        data = self._cache[cache_key]

        if _IS_WINDOWS:
            self._play_windows(data)
        elif _HAS_QT_AUDIO:
            self._play_qt(data)

    def _play_windows(self, wav_data: bytes) -> None:
        """Play WAV data via winsound in a background thread."""
        def _do():
            try:
                winsound.PlaySound(
                    wav_data,
                    winsound.SND_MEMORY | winsound.SND_NODEFAULT,
                )
            except Exception:
                pass
        threading.Thread(target=_do, daemon=True).start()

    def _play_qt(self, pcm_data: bytes) -> None:
        """Play raw PCM via QAudioSink."""
        if not self._format:
            return
        try:
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
            self._sink = sink
            self._buf = buf
            self._ba = ba

            def _on_state(state):
                if state == QAudio.State.IdleState:
                    sink.stop()

            sink.stateChanged.connect(_on_state)
            sink.start(buf)
        except Exception:
            pass


# Module-level singleton
audio_engine = AudioEngine()
