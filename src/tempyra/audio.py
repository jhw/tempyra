"""Audio encoding, decoding, and mip level generation."""

import io
from pathlib import Path
from typing import Union

import numpy as np
import soundfile as sf

from .constants import BASE_SAMPLES, NUM_MIP_LEVELS, SAMPLE_RATE, mip_sample_count


def encode_flac(audio: np.ndarray) -> bytes:
    """Encode a numpy array to FLAC bytes (48kHz, 16-bit, stereo)."""
    buf = io.BytesIO()
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])
    sf.write(buf, audio, SAMPLE_RATE, format='FLAC', subtype='PCM_16')
    return buf.getvalue()


def decode_flac(data: bytes) -> np.ndarray:
    """Decode FLAC bytes to a numpy array."""
    buf = io.BytesIO(data)
    audio, sr = sf.read(buf)
    return audio


def generate_mip_levels(audio: np.ndarray) -> list:
    """Generate 8 mip levels from full-resolution stereo audio.

    The input should be a numpy array of shape (N, 2) with N >= BASE_SAMPLES.
    If shorter, it will be zero-padded. If longer, it will be truncated.

    Returns a list of 8 numpy arrays, one per mip level.
    """
    if len(audio) > BASE_SAMPLES:
        audio = audio[:BASE_SAMPLES]
    elif len(audio) < BASE_SAMPLES:
        channels = audio.shape[1] if audio.ndim > 1 else 1
        pad = np.zeros((BASE_SAMPLES - len(audio), channels))
        audio = np.vstack([audio, pad])

    levels = [audio]
    for level in range(1, NUM_MIP_LEVELS):
        target = mip_sample_count(level)
        levels.append(audio[:target])

    return levels


def load_audio_file(path: Union[str, Path], target_sr: int = SAMPLE_RATE) -> np.ndarray:
    """Load an audio file and return it as a numpy array at the target sample rate.

    Returns stereo float64 audio. Mono files are duplicated to stereo.
    """
    audio, sr = sf.read(str(path))
    if audio.ndim == 1:
        audio = np.column_stack([audio, audio])

    if sr != target_sr:
        duration = len(audio) / sr
        target_len = int(duration * target_sr)
        indices = np.linspace(0, len(audio) - 1, target_len)
        idx_floor = np.floor(indices).astype(int)
        idx_ceil = np.minimum(idx_floor + 1, len(audio) - 1)
        frac = (indices - idx_floor)[:, np.newaxis]
        audio = audio[idx_floor] * (1 - frac) + audio[idx_ceil] * frac

    return audio
