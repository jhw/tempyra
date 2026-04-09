import io
import os
import tempfile
import zipfile

import numpy as np
import soundfile as sf

import tempyra


def test_load(canvas_path):
    """Loading a canvas should produce valid Canvas with audio."""
    canvas = tempyra.load(canvas_path)
    assert isinstance(canvas, tempyra.Canvas)
    assert canvas.canvas_version > 0
    for i in range(tempyra.NUM_TRACKS):
        audio = canvas.track_audio[i]
        assert audio is not None
        assert audio.shape == (tempyra.BASE_SAMPLES, 2)


def test_load_save_roundtrip(canvas_path):
    """Save then reload should preserve shapes and params."""
    canvas = tempyra.load(canvas_path)

    with tempfile.NamedTemporaryFile(suffix='.canvas', delete=False) as f:
        out_path = f.name

    try:
        tempyra.save(canvas, out_path)

        with zipfile.ZipFile(canvas_path) as orig_zf, \
             zipfile.ZipFile(out_path) as new_zf:
            assert sorted(orig_zf.namelist()) == sorted(new_zf.namelist())

            for name in orig_zf.namelist():
                if name.endswith('.flac'):
                    orig_audio, _ = sf.read(io.BytesIO(orig_zf.read(name)))
                    new_audio, _ = sf.read(io.BytesIO(new_zf.read(name)))
                    assert orig_audio.shape == new_audio.shape, \
                        f"{name}: {orig_audio.shape} != {new_audio.shape}"

            orig_params = orig_zf.read('parameters.txt').decode()
            new_params = new_zf.read('parameters.txt').decode()
            assert orig_params == new_params
    finally:
        os.unlink(out_path)


def test_create_from_scratch():
    """Create a canvas from scratch and verify structure."""
    canvas = tempyra.Canvas()
    canvas.set('canvasVersion', 15)
    canvas.set('masterVolume', 0.9)
    canvas.set('track0Name', 'test_sine.wav')
    canvas.set('track0Amp', 0.75)

    t = np.linspace(0, 10.922667, tempyra.BASE_SAMPLES)
    sine = np.sin(2 * np.pi * 440 * t) * 0.5
    canvas.track_audio[0] = np.column_stack([sine, sine])

    silence = np.zeros((tempyra.BASE_SAMPLES, 2))
    for i in range(1, 8):
        canvas.track_audio[i] = silence

    with tempfile.NamedTemporaryFile(suffix='.canvas', delete=False) as f:
        out_path = f.name

    try:
        tempyra.save(canvas, out_path)

        with zipfile.ZipFile(out_path) as zf:
            names = zf.namelist()
            assert 'parameters.txt' in names
            assert len(names) == 65

            for mip in range(8):
                audio, sr = sf.read(io.BytesIO(zf.read(f'0_{mip}.flac')))
                assert sr == 48000
                assert audio.shape == (tempyra.mip_sample_count(mip), 2)

        loaded = tempyra.load(out_path)
        assert loaded.track_name(0) == 'test_sine.wav'
        assert loaded.track_amp(0) == 0.75
        diff = np.max(np.abs(loaded.track_audio[0] - canvas.track_audio[0]))
        assert diff < 2e-5
    finally:
        os.unlink(out_path)


def test_canvas_accessors():
    """Test typed convenience accessors."""
    canvas = tempyra.Canvas()
    canvas.set('canvasVersion', 15)
    canvas.set('masterVolume', 0.8)
    canvas.set('track0Name', 'test.wav')
    canvas.set('track0Amp', 0.6)
    canvas.set('track0Tuning', 432.0)
    canvas.set('track0From', 100)
    canvas.set('track0To', 500000)
    canvas.set('emittor0Name', 'My Emitter')
    canvas.set('cellEmitter5', 2)

    assert canvas.canvas_version == 15
    assert canvas.master_volume == 0.8
    assert canvas.track_name(0) == 'test.wav'
    assert canvas.track_amp(0) == 0.6
    assert canvas.track_tuning(0) == 432.0
    assert canvas.track_from(0) == 100
    assert canvas.track_to(0) == 500000
    assert canvas.emitter_name(0) == 'My Emitter'
    assert canvas.cell_emitter(5) == 2
