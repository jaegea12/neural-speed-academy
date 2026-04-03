"""
Audio feedback engine for Neural Speed Academy.

Uses sounddevice for low-latency cross-platform audio playback.
Tones are synthesized as numpy arrays and played non-blocking.
Falls back to silent no-ops if sounddevice or numpy is unavailable.
"""
from __future__ import annotations

import math
from typing import Optional

_SAMPLE_RATE = 44100

try:
    import numpy as np
    import sounddevice as sd
    _HAS_AUDIO = True
except ImportError:
    _HAS_AUDIO = False
    np = None  # type: ignore


# --- Tone synthesis ---

def _sine(freq: float, duration_ms: int, volume: float, fade_ms: int = 8) -> "np.ndarray":
    """Generate a sine wave as a numpy float32 array."""
    n = int(_SAMPLE_RATE * duration_ms / 1000)
    fade = int(_SAMPLE_RATE * fade_ms / 1000)
    t = np.arange(n, dtype=np.float32) / _SAMPLE_RATE
    out = np.sin(2 * np.pi * freq * t, dtype=np.float32) * volume
    # Fade in/out
    if fade > 0 and n > 2 * fade:
        out[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
        out[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    return out


def _sweep(f0: float, f1: float, duration_ms: int, volume: float, fade_ms: int = 8) -> "np.ndarray":
    """Generate a frequency sweep as a numpy float32 array."""
    n = int(_SAMPLE_RATE * duration_ms / 1000)
    fade = int(_SAMPLE_RATE * fade_ms / 1000)
    t = np.arange(n, dtype=np.float32) / _SAMPLE_RATE
    freqs = np.linspace(f0, f1, n, dtype=np.float32)
    phase = np.cumsum(freqs) / _SAMPLE_RATE
    out = (np.sin(2 * np.pi * phase, dtype=np.float32) * volume).astype(np.float32)
    if fade > 0 and n > 2 * fade:
        out[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
        out[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    return out


# Tone builders: volume -> numpy array
def _build_tones():
    if not _HAS_AUDIO:
        return {}
    return {
        "correct": lambda vol: _sweep(400, 600, 80, vol),
        "incorrect": lambda vol: _sweep(400, 250, 120, vol),
        "tick": lambda vol: _sine(800, 30, vol * 0.6),
        "completion": lambda vol: np.concatenate([
            _sine(523.25, 100, vol),
            np.zeros(int(_SAMPLE_RATE * 0.03), dtype=np.float32),
            _sine(659.25, 140, vol),
        ]),
    }

_TONE_BUILDERS = _build_tones()


class AudioEngine:
    """Plays synthesized audio cues via sounddevice."""

    def __init__(self):
        self._enabled: bool = True
        self._volume: float = 0.5
        self._cache: dict = {}

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

        key = f"{tone_name}_{self._volume:.2f}"
        if key not in self._cache:
            self._cache[key] = _TONE_BUILDERS[tone_name](self._volume)

        data = self._cache[key]

        try:
            sd.play(data, samplerate=_SAMPLE_RATE)
        except Exception:
            pass


# Module-level singleton
audio_engine = AudioEngine()
