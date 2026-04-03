"""
Audio feedback engine for Neural Speed Academy.

Uses sounddevice with a persistent OutputStream for zero-latency playback.
The stream stays open so there's no device-open overhead per tone.
"""
from __future__ import annotations

import threading
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

def _sine(freq: float, duration_ms: int, volume: float) -> "np.ndarray":
    n = int(_SAMPLE_RATE * duration_ms / 1000)
    fade = int(_SAMPLE_RATE * 0.005)
    t = np.arange(n, dtype=np.float32) / _SAMPLE_RATE
    out = np.sin(2 * np.pi * freq * t, dtype=np.float32) * volume
    if fade > 0 and n > 2 * fade:
        out[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
        out[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    return out


def _sweep(f0: float, f1: float, duration_ms: int, volume: float) -> "np.ndarray":
    n = int(_SAMPLE_RATE * duration_ms / 1000)
    fade = int(_SAMPLE_RATE * 0.005)
    t = np.arange(n, dtype=np.float32) / _SAMPLE_RATE
    freqs = np.linspace(f0, f1, n, dtype=np.float32)
    phase = np.cumsum(freqs) / _SAMPLE_RATE
    out = (np.sin(2 * np.pi * phase) * volume).astype(np.float32)
    if fade > 0 and n > 2 * fade:
        out[:fade] *= np.linspace(0, 1, fade, dtype=np.float32)
        out[-fade:] *= np.linspace(1, 0, fade, dtype=np.float32)
    return out


_TONE_BUILDERS = {}
if _HAS_AUDIO:
    _TONE_BUILDERS = {
        "correct": lambda vol: _sweep(400, 600, 80, vol),
        "incorrect": lambda vol: _sweep(400, 250, 120, vol),
        "tick": lambda vol: _sine(800, 30, vol * 0.6),
        "completion": lambda vol: np.concatenate([
            _sine(523.25, 100, vol),
            np.zeros(int(_SAMPLE_RATE * 0.03), dtype=np.float32),
            _sine(659.25, 140, vol),
        ]),
    }


class AudioEngine:
    """Plays synthesized audio cues via a persistent sounddevice stream."""

    def __init__(self):
        self._enabled: bool = True
        self._volume: float = 0.5
        self._cache: dict = {}
        self._stream: Optional[object] = None
        self._lock = threading.Lock()
        self._write_pos: int = 0

    def _ensure_stream(self) -> bool:
        """Open a persistent output stream if not already open."""
        if self._stream is not None:
            return True
        if not _HAS_AUDIO:
            return False
        try:
            self._stream = sd.OutputStream(
                samplerate=_SAMPLE_RATE,
                channels=1,
                dtype="float32",
                blocksize=0,
                latency="low",
            )
            self._stream.start()
            return True
        except Exception:
            self._stream = None
            return False

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
        """Play a named tone. Non-blocking. No-op if disabled."""
        if not self._enabled or not _HAS_AUDIO:
            return
        if tone_name not in _TONE_BUILDERS:
            return
        if not self._ensure_stream():
            return

        key = f"{tone_name}_{self._volume:.2f}"
        if key not in self._cache:
            self._cache[key] = _TONE_BUILDERS[tone_name](self._volume)

        data = self._cache[key]

        # Write to stream in background thread to avoid blocking UI
        def _write():
            try:
                with self._lock:
                    self._stream.write(data.reshape(-1, 1))
            except Exception:
                pass

        threading.Thread(target=_write, daemon=True).start()

    def close(self) -> None:
        """Close the audio stream."""
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
            self._stream = None


# Module-level singleton
audio_engine = AudioEngine()
