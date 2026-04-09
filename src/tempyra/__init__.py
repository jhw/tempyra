"""Tempyra — Python library for Beetlecrab Tempera .canvas files."""

from .audio import generate_mip_levels, load_audio_file
from .canvas import Canvas, load, save
from .constants import (
    BASE_SAMPLES,
    NUM_CELLS,
    NUM_EMITTERS,
    NUM_MIP_LEVELS,
    NUM_TRACKS,
    SAMPLE_RATE,
    mip_sample_count,
)

__version__ = "0.1.0"

__all__ = [
    "Canvas",
    "load",
    "save",
    "load_audio_file",
    "generate_mip_levels",
    "mip_sample_count",
    "BASE_SAMPLES",
    "NUM_CELLS",
    "NUM_EMITTERS",
    "NUM_MIP_LEVELS",
    "NUM_TRACKS",
    "SAMPLE_RATE",
]
