"""
Audio feedback engine for Neural Speed Academy.

Uses winsound.Beep on Windows for zero-latency tones.
Falls back to QAudioSink with synthesized PCM on other platforms.
"""
from __future__ import annotations

import platform
import threading
from typing import Optional

_IS_WINDOWS = platform.system() == "Windows"

if _IS_WINDOWS:
    import winsound

    def _play_beep(freq: int, duration_ms: int) -> None:
        """Non-blocking beep via winsound in a thread."""
        threading.Thread(
            target=winsound.Beep, args=(freq, duration_ms), daemon=True
        ).start()

    def _tone_correct() -> None:
        _play_beep(600, 80)

    def _tone_incorrect() -> None:
        _play_beep(250, 120)

    def _tone_tick() -> None:
        _play_beep(800, 30)

    def _tone_completion() -> None:
        def _chime():
            winsound.Beep(523, 100)  # C5
            winsound.Beep(659, 150)  # E5
        threading.Thread(target=_chime, daemon=True).start()

    _TONE_FUNCS = {
        "correct": _tone_correct,
        "incorrect": _tone_incorrect,
        "tick": _tone_tick,
        "completion": _tone_completion,
    }
    _HAS_AUDIO = True

else:
    # Fallback: QAudioSink with synthesized PCM
    import math
    import struct

    _TONE_FUNCS = {}
    _HAS_AUDIO = False

    try:
        from PyQt6.QtMultimedia import QAudioFormat, QAudioSink, QAudio
        from PyQt6.QtCore import QBuffer, QIODevice, QByteArray
        _HAS_AUDIO = True
    except ImportError:
        pass

    _SAMPLE_RATE = 44100

    def _generate_tone(frequency: float, duration_ms: int, volume: float = 0.5) -> bytes:
        n_samples = int(_SAMPLE_RATE * duration_ms / 1000)
        fade = int(_SAMPLE_RATE * 0.01)
        samples = []
        for i in range(n_samples):
            t = i / _SAMPLE_RATE
            val = math.sin(2 * math.pi * frequency * t) * volume
            if i < fade:
                val *= i / fade
            elif i > n_samples - fade:
                val *= (n_samples - i) / fade
            samples.append(int(val * 32767))
        return struct.pack(f"<{len(samples)}h", *samples)

    def _generate_sweep(f0: float, f1: float, ms: int, vol: float = 0.5) -> bytes:
        n = int(_SAMPLE_RATE * ms / 1000)
        fade = int(_SAMPLE_RATE * 0.01)
        samples = []
        for i in range(n):
            t = i / _SAMPLE_RATE
            f = f0 + (f1 - f0) * (i / n)
            val = math.sin(2 * math.pi * f * t) * vol
            if i < fade:
                val *= i / fade
            elif i > n - fade:
                val *= (n - i) / fade
            samples.append(int(val * 32767))
        return struct.pack(f"<{len(samples)}h", *samples)

    if _HAS_AUDIO:
        _TONE_DEFS = {
            "correct":    lambda vol: _generate_sweep(400, 600, 100, vol),
            "incorrect":  lambda vol: _generate_sweep(400, 250, 150, vol),
            "tick":       lambda vol: _generate_tone(800, 40, vol * 0.6),
            "completion": lambda vol: (
                _generate_tone(523.25, 120, vol)
                + b"\x00\x00" * int(_SAMPLE_RATE * 0.04)
                + _generate_tone(659.25, 180, vol)
            ),
        }


class AudioEngine:
    """Plays audio cues. Uses winsound on Windows, QAudioSink elsewhere."""

    def __init__(self):
        self._enabled: bool = True
        self._volume: float = 0.5
        # QAudioSink state (non-Windows only)
        self._sink: Optional[object] = None
        self._buf: Optional[object] = None
        self._ba: Optional[object] = None
        self._format: Optional[object] = None
        self._cache: dict[str, bytes] = {}

        if _HAS_AUDIO and not _IS_WINDOWS:
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
        """Play a named tone. No-op if audio is disabled or unavailable."""
        if not self._enabled or not _HAS_AUDIO:
            return

        if _IS_WINDOWS:
            func = _TONE_FUNCS.get(tone_name)
            if func:
                func()
            return

        # Non-Windows: QAudioSink path
        if not self._format or tone_name not in _TONE_DEFS:
            return

        if tone_name not in self._cache:
            self._cache[tone_name] = _TONE_DEFS[tone_name](self._volume)

        pcm_data = self._cache[tone_name]

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
