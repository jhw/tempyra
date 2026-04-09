"""Parameter parsing and serialization for Tempera parameters.txt."""

from collections import OrderedDict

from .constants import NUM_TRACKS


def parse_value(raw: str):
    """Parse a parameter value string into int, float, or str.

    Preserves the exact raw string if it cannot be parsed as a number,
    including any leading/trailing whitespace (some track names have this).
    """
    stripped = raw.strip()
    try:
        if '.' in stripped or 'e' in stripped.lower():
            return float(stripped)
        return int(stripped)
    except ValueError:
        return raw


def format_value(val) -> str:
    """Format a value for parameters.txt."""
    if isinstance(val, float):
        return f"{val:g}"
    return str(val)


def is_track_key(key: str) -> bool:
    """Check if a parameter key is a track parameter."""
    return key.startswith('track') and len(key) > 5 and key[5].isdigit()


def track_key_parts(key: str):
    """Split a track key like 'track3Amp' into (3, 'Amp')."""
    rest = key[5:]
    i = 0
    while i < len(rest) and rest[i].isdigit():
        i += 1
    return int(rest[:i]), rest[i:]


def parse_parameters(text: str) -> OrderedDict:
    """Parse parameters.txt content into an OrderedDict.

    Preserves the original key ordering so round-trip serialization is exact.
    """
    params = OrderedDict()
    for line in text.strip().splitlines():
        if ':' not in line:
            continue
        key, _, val = line.partition(':')
        params[key.strip()] = parse_value(val)
    return params


def serialize_parameters(params: OrderedDict) -> str:
    """Serialize parameters to the parameters.txt format.

    Non-track parameters are sorted alphabetically.
    Track parameters preserve their original insertion order.
    """
    non_track = OrderedDict()
    track_entries = []

    for key, val in params.items():
        if is_track_key(key):
            track_entries.append((key, val))
        else:
            non_track[key] = val

    lines = []

    for key in sorted(non_track.keys()):
        lines.append(f"{key}:{format_value(val)}" if False else f"{key}:{format_value(non_track[key])}")

    for key, val in track_entries:
        lines.append(f"{key}:{format_value(val)}")

    return '\n'.join(lines) + '\n'
