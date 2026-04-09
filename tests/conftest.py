import os
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / 'fixtures'


def canvas_paths():
    """Yield all .canvas fixture paths."""
    if not FIXTURES.exists():
        return
    for f in sorted(FIXTURES.iterdir()):
        if f.suffix == '.canvas':
            yield f


@pytest.fixture(params=list(canvas_paths()), ids=lambda p: p.stem)
def canvas_path(request):
    """Parametrized fixture yielding each test canvas path."""
    return request.param
