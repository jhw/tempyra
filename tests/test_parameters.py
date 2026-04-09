import zipfile

from tempyra.parameters import parse_parameters, serialize_parameters


def test_parameter_roundtrip(canvas_path):
    """Parameters should round-trip exactly."""
    with zipfile.ZipFile(canvas_path) as zf:
        orig = zf.read('parameters.txt').decode()

    params = parse_parameters(orig)
    serialized = serialize_parameters(params)
    assert orig == serialized


def test_parse_value_types():
    from tempyra.parameters import parse_value

    assert parse_value('42') == 42
    assert isinstance(parse_value('42'), int)

    assert parse_value('3.14') == 3.14
    assert isinstance(parse_value('3.14'), float)

    assert parse_value('hello') == 'hello'
    assert isinstance(parse_value('hello'), str)

    # Leading space preserved for strings
    assert parse_value(' spaced name') == ' spaced name'
