import numpy as np

from tempyra import BASE_SAMPLES, mip_sample_count
from tempyra.audio import decode_flac, encode_flac, generate_mip_levels


def test_flac_roundtrip():
    """FLAC encode/decode should be lossless within 16-bit quantization."""
    rng = np.random.default_rng(42)
    audio = rng.uniform(-0.9, 0.9, (1024, 2))
    encoded = encode_flac(audio)
    decoded = decode_flac(encoded)
    assert decoded.shape == audio.shape
    # 16-bit quantization: max error ~1 LSB
    assert np.max(np.abs(decoded - audio)) < 2e-5


def test_flac_mono_to_stereo():
    """Mono input should be expanded to stereo."""
    mono = np.random.randn(512).astype(np.float64) * 0.5
    encoded = encode_flac(mono)
    decoded = decode_flac(encoded)
    assert decoded.shape == (512, 2)


def test_generate_mip_levels_correct_sizes():
    audio = np.zeros((BASE_SAMPLES, 2))
    levels = generate_mip_levels(audio)
    assert len(levels) == 8
    for i, level in enumerate(levels):
        assert level.shape[0] == mip_sample_count(i)
        assert level.shape[1] == 2


def test_generate_mip_levels_pads_short_audio():
    short = np.ones((1000, 2))
    levels = generate_mip_levels(short)
    assert levels[0].shape[0] == BASE_SAMPLES
    # First 1000 samples should be 1.0, rest should be 0.0
    assert np.all(levels[0][:1000] == 1.0)
    assert np.all(levels[0][1000:] == 0.0)


def test_generate_mip_levels_truncates_long_audio():
    long = np.ones((BASE_SAMPLES + 5000, 2))
    levels = generate_mip_levels(long)
    assert levels[0].shape[0] == BASE_SAMPLES
