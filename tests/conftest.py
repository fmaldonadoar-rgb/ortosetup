import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "tools"))

from make_synthetic_case import make_case  # noqa: E402


@pytest.fixture(scope="session")
def synthetic_case(tmp_path_factory):
    out = tmp_path_factory.mktemp("caso_sintetico")
    make_case(out)
    return out
