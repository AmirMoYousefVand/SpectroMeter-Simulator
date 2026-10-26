"""
Mechanical Audio Feedback Synthesizer.
Synthesizes in-memory PCM WAV audio samples and plays them asynchronously via winsound.
Provides authentic physical sound effects for spectrometer clamps, fine screws, and vernier rotation.
"""

import sys
import io
import wave
import math
import struct
from typing import Optional

class AudioEffects:
    """Zero-dependency sound generator for spectrometer tactile mechanical feedback."""

    _MUTED: bool = False
    _CACHE = {}

    @classmethod
    def set_muted(cls, muted: bool):
        cls._MUTED = bool(muted)

    @classmethod
    def is_muted(cls) -> bool:
        return cls._MUTED

    @classmethod
    def _create_wav_bytes(cls, samples: list, sample_rate: int = 22050) -> bytes:
        """Encodes float samples in [-1.0, 1.0] to standard 16-bit mono PCM WAV bytes."""
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sample_rate)
            raw = bytearray()
            for s in samples:
                val = int(max(-1.0, min(1.0, s)) * 32767.0)
                raw.extend(struct.pack('<h', val))
            wav.writeframes(raw)
        return buf.getvalue()

    @classmethod
    def _get_ratchet_tick_wav(cls) -> bytes:
        if "ratchet" not in cls._CACHE:
            # 10ms decaying high-frequency tick (2400 Hz)
            rate = 22050
            num_samples = int(rate * 0.012)
            samples = []
            for i in range(num_samples):
                t = i / rate
                decay = math.exp(-t * 350.0)
                freq = 2400.0 - (t * 80000.0)
                samples.append(0.35 * decay * math.sin(2.0 * math.pi * max(200.0, freq) * t))
            cls._CACHE["ratchet"] = cls._create_wav_bytes(samples, rate)
        return cls._CACHE["ratchet"]

    @classmethod
    def _get_tangent_click_wav(cls) -> bytes:
        if "tangent" not in cls._CACHE:
            # Crisp metallic micro-click (3800 Hz)
            rate = 22050
            num_samples = int(rate * 0.008)
            samples = []
            for i in range(num_samples):
                t = i / rate
                decay = math.exp(-t * 600.0)
                samples.append(0.25 * decay * math.sin(2.0 * math.pi * 3800.0 * t))
            cls._CACHE["tangent"] = cls._create_wav_bytes(samples, rate)
        return cls._CACHE["tangent"]

    @classmethod
    def _get_clamp_wav(cls) -> bytes:
        if "clamp" not in cls._CACHE:
            # Damped mechanical thud (650 Hz + 1800 Hz latch)
            rate = 22050
            num_samples = int(rate * 0.035)
            samples = []
            for i in range(num_samples):
                t = i / rate
                decay = math.exp(-t * 120.0)
                s = 0.4 * math.sin(2.0 * math.pi * 650.0 * t) + 0.3 * math.sin(2.0 * math.pi * 1800.0 * t)
                samples.append(decay * s)
            cls._CACHE["clamp"] = cls._create_wav_bytes(samples, rate)
        return cls._CACHE["clamp"]

    @classmethod
    def _play_wav_bytes(cls, wav_bytes: bytes):
        """Asynchronously plays WAV bytes using winsound without blocking GUI."""
        if cls._MUTED or not sys.platform.startswith("win"):
            return
        try:
            import winsound
            winsound.PlaySound(wav_bytes, winsound.SND_MEMORY | winsound.SND_ASYNC)
        except Exception:
            pass

    @classmethod
    def play_vernier_tick(cls):
        """Plays rotational tick sound when telescope angle changes."""
        cls._play_wav_bytes(cls._get_ratchet_tick_wav())

    @classmethod
    def play_tangent_click(cls):
        """Plays fine micrometer click when tangent screw is turned."""
        cls._play_wav_bytes(cls._get_tangent_click_wav())

    @classmethod
    def play_clamp_sound(cls):
        """Plays mechanical latch click when clamp is toggled."""
        cls._play_wav_bytes(cls._get_clamp_wav())
