# Tempyra

Python library for reading and writing Beetlecrab Tempera `.canvas` files.

The [Tempera](https://beetlecrab.audio/tempera/) is a hardware granular sampling instrument. A `.canvas` file is its complete patch format — a ZIP archive bundling 8 audio tracks (as FLAC) with all synth parameters.

## Install

```bash
pip install -e .
```

Requires Python 3.9+ and libsndfile (for soundfile).

## Usage

### Load a canvas

```python
import tempyra

canvas = tempyra.load('MyPatch.canvas')

print(canvas.canvas_version)
print(canvas.master_volume)

for i in range(8):
    print(f'Track {i}: {canvas.track_name(i)}')
    audio = canvas.track_audio[i]  # numpy array, shape (524288, 2)
```

### Create a canvas from scratch

```python
import numpy as np
import tempyra

canvas = tempyra.Canvas()
canvas.set('canvasVersion', 15)
canvas.set('masterVolume', 0.9)
canvas.set('tempoClockBPMCanvas', 120)
canvas.set('track0Name', 'MyDrums120BPM.wav')
canvas.set('track0Amp', 0.75)

# Load audio into tracks
canvas.track_audio[0] = tempyra.load_audio_file('drums.wav')

# Fill remaining tracks with silence
silence = np.zeros((tempyra.BASE_SAMPLES, 2))
for i in range(1, 8):
    canvas.track_audio[i] = silence

# Save — mip levels are generated automatically
tempyra.save(canvas, 'MyPatch.canvas')
```

### Modify an existing canvas

```python
import tempyra

canvas = tempyra.load('Original.canvas')
canvas.set('masterVolume', 0.8)
canvas.set('reverbMix', 0.5)
tempyra.save(canvas, 'Modified.canvas')
```

## Canvas file format

See [CANVAS_FORMAT.md](CANVAS_FORMAT.md) for full reverse-engineered documentation of the `.canvas` file format.

### Summary

A `.canvas` file is a ZIP archive (uncompressed) containing:

- **64 FLAC files** — 8 tracks x 8 resolution levels (`{track}_{level}.flac`)
  - 48kHz, 16-bit, stereo
  - Level 0: 524,288 samples (~10.9s), each subsequent level ~77% of previous
- **parameters.txt** — key:value pairs for all synth parameters

Parameters include tracks, emitters (granular voices), modulators, effects (chorus, delay, reverb, degrade), filter, amp envelope, touchgrid settings, and cell-emitter mappings.

## Tests

```bash
pip install -e ".[dev]"
pytest
```

## Resources

### Official

- [Tempera Owner's Manual (PDF)](https://docs.beetlecrab.audio/tempera/_static/tempera_manual.pdf)
- [Tempera Online Manual — Tracks](https://docs.beetlecrab.audio/tempera/tracks.html)
- [Official Canvas Gallery](https://gallery.beetlecrab.audio/patches/)
- [Beetlecrab Tempera Homepage](https://beetlecrab.audio/tempera/)

### Tutorials and canvases

- [Canvas Walkthrough (YouTube)](https://www.youtube.com/watch?v=qzPf6r-FwOk)
- [Canvas From Scratch Tutorial (YouTube)](https://www.youtube.com/watch?v=cIcJK0BDGvk)
- [Free Canvas Downloads — Red Means Recording (Patreon)](https://www.patreon.com/posts/free-download-104016065)
- [New Tempera Canvases — Red Means Recording (Patreon)](https://www.patreon.com/posts/new-tempera-107644277)
