"""Canvas class and file I/O for Tempera .canvas files."""

import zipfile
from collections import OrderedDict
from pathlib import Path
from typing import Union

import numpy as np

from .audio import decode_flac, encode_flac, generate_mip_levels
from .constants import BASE_SAMPLES, NUM_MIP_LEVELS, NUM_TRACKS
from .parameters import parse_parameters, serialize_parameters


class Canvas:
    """Represents a complete Tempera .canvas file.

    Parameters are stored as an OrderedDict preserving the original key order.
    Typed accessors are provided for common parameters, but the raw dict
    is the source of truth — this ensures unknown/version-specific parameters
    survive round-trips.
    """

    def __init__(self):
        self.params = OrderedDict()
        self.track_audio = [None] * NUM_TRACKS

    def get(self, key: str, default=None):
        """Get a parameter value by key."""
        return self.params.get(key, default)

    def set(self, key: str, value):
        """Set a parameter value by key."""
        self.params[key] = value

    @property
    def canvas_version(self) -> int:
        return int(self.params.get('canvasVersion', 15))

    @canvas_version.setter
    def canvas_version(self, val: int):
        self.params['canvasVersion'] = val

    @property
    def master_volume(self) -> float:
        return float(self.params.get('masterVolume', 1.0))

    @master_volume.setter
    def master_volume(self, val: float):
        self.params['masterVolume'] = val

    def track_name(self, i: int) -> str:
        return str(self.params.get(f'track{i}Name', ''))

    def set_track_name(self, i: int, name: str):
        self.params[f'track{i}Name'] = name

    def track_amp(self, i: int) -> float:
        return float(self.params.get(f'track{i}Amp', 0.5))

    def track_tuning(self, i: int) -> float:
        return float(self.params.get(f'track{i}Tuning', 440.0))

    def track_from(self, i: int) -> int:
        return int(self.params.get(f'track{i}From', 0))

    def track_to(self, i: int) -> int:
        return int(self.params.get(f'track{i}To', BASE_SAMPLES * 2))

    def emitter_name(self, i: int) -> str:
        return str(self.params.get(f'emittor{i}Name', f'Emitter {i+1}'))

    def cell_emitter(self, i: int) -> int:
        return int(self.params.get(f'cellEmitter{i}', -1))


def load(path: Union[str, Path]) -> Canvas:
    """Load a .canvas file and return a Canvas object."""
    path = Path(path)
    with zipfile.ZipFile(path, 'r') as zf:
        param_text = zf.read('parameters.txt').decode('utf-8')
        canvas = Canvas()
        canvas.params = parse_parameters(param_text)

        for track in range(NUM_TRACKS):
            flac_name = f'{track}_0.flac'
            if flac_name in zf.namelist():
                canvas.track_audio[track] = decode_flac(zf.read(flac_name))

    return canvas


def save(canvas: Canvas, path: Union[str, Path]) -> None:
    """Save a Canvas object to a .canvas file.

    Generates all 8 mip levels per track and writes parameters.txt.
    FLAC files are stored uncompressed (method=store) as the original format does.
    """
    path = Path(path)
    with zipfile.ZipFile(path, 'w', compression=zipfile.ZIP_STORED) as zf:
        for track in range(NUM_TRACKS - 1, -1, -1):
            audio = canvas.track_audio[track]
            if audio is None:
                audio = np.zeros((BASE_SAMPLES, 2))

            levels = generate_mip_levels(audio)
            for mip in range(NUM_MIP_LEVELS - 1, -1, -1):
                flac_name = f'{track}_{mip}.flac'
                zf.writestr(flac_name, encode_flac(levels[mip]))

        zf.writestr('parameters.txt', serialize_parameters(canvas.params))
