"""
Audio feedback engine for Neural Speed Academy.

Uses sounddevice for low-latency cross-platform audio playback.
Tones are synthesized as numpy-free float arrays and played non-blocking.
Falls back to silent no-ops if sounddevice is unavailable.
"""
from __future__ import annotations

import array
import math
from typing import Optional

_SAMPLE_RATE = 44100

try:
    import sounddevice as sd
    _HAS_AUDIO = True
except ImportError:
    _HAS_AUDIO = False


# --- Tone synthesis ---

def _sine(freq: float, duration_ms: int, volume: float, fade_ms: int = 8) -> array.array:
    """Generate a sine wave as a float array."""
    n = int(_SAMPLE_RATE * duration_ms / 1000)
    fade = int(_SAMPLE_RATE * fade_ms / 1000)
    out = array.array("f")
    for i in range(n):
        t = i / _SAMPLE_RATE
        val = math.sin(2 * math.pi * freq * t) * volume
        if i < fade:
            val *= i / fade
        elif i > n - fade:
            val *= (n - i) / fade
        out.append(val)
    return out


def _sweep(f0: float, f1: float, duration_ms: int, volume: float, fade_ms: int = 8) -> array.array:
    """Generate a frequency sweep as a float array."""
    n = int(_SAMPLE_RATE * duration_ms / 1000)
    fade = int(_SAMPLE_RATE * fade_ms / 1000)
    out = array.array("f")
    for i in range(n):
        t = i / _SAMPLE_RATE
        f = f0 + (f1 - f0) * (i / n)
        val = math.sin(2 * math.pi * f * t) * volume
        if i < fade:
            val *= i / fade
        elif i > n - fade:
            val *= (n - i) / fade
        out.append(val)
    return out


def _silence(duration_ms: int) -> array.array:
    """Generate silence."""
    n = int(_SAMPLE_RATE * duration_ms / 1000)
    return array.array("f", [0.0] * n)


def _concat(*parts: array.array) -> array.array:
    """Concatenate multiple float arrays."""
    out = array.array("f")
    for p in parts:
        out.extend(p)
    return out


# Tone builders: volume -> float array
_TONE_BUILDERS = {
    "correct": lambda vol: _sweep(400, 600, 80, vol),
    "incorrect": lambda vol: _sweep(400, 250, 120, vol),
    "tick": lambda vol: _sine(800, 30, vol * 0.6),
    "completion": lambda vol: _concat(
        _sine(523.25, 100, vol),
        _silence(30),
        _sine(659.25, 140, vol),
    ),
}


class AudioEngine:
    """Plays synthesized audio cues via sounddevice."""

    def __init__(self):
        self._enabled: bool = True
        self._volume: float = 0.5
        self._cache: dict[str, array.array] = {}

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
        """Play a named tone. Non-blocking. No-op if disabled or unavailable."""
        if not self._enabled or not _HAS_AUDIO:
            return
        if tone_name not in _TONE_BUILDERS:
            return

        # Cache tones per volume level
        key = f"{tone_name}_{self._volume:.2f}"
        if key not in self._cache:
            self._cache[key] = _TONE_BUILDERS[tone_name](self._volume)

        data = self._cache[key]

        try:
            sd.play(data, samplerate=_SAMPLE_RATE)
        except Exception:
            pass  # audio failure is never fatal


# Module-level singleton
audio_engine = AudioEngine()
