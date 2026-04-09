"""Format constants for Tempera .canvas files."""

NUM_TRACKS = 8
NUM_MIP_LEVELS = 8
NUM_EMITTERS = 4
NUM_CELLS = 64
SAMPLE_RATE = 48000
BASE_SAMPLES = 524288  # 2^19

# Mip level sample counts, empirically determined from Tempera output.
# Each level is approximately previous * 10/13, but exact rounding is firmware-specific.
_MIP_COUNTS = (524288, 403298, 310229, 238637, 183567, 141205, 108619, 83553)


def mip_sample_count(level: int) -> int:
    """Return the expected sample count for a given mip level (0-7)."""
    return _MIP_COUNTS[level]
