from tempyra import mip_sample_count, BASE_SAMPLES


def test_mip_sample_counts():
    expected = [524288, 403298, 310229, 238637, 183567, 141205, 108619, 83553]
    for i, exp in enumerate(expected):
        assert mip_sample_count(i) == exp


def test_base_samples():
    assert BASE_SAMPLES == 2**19
