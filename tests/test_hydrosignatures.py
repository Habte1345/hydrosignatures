"""Tests for PyNHD package."""
import io
import json
from pathlib import Path
from typing import Any, Dict, Tuple

import numpy as np
import pandas as pd
import pytest

import hydrosignatures as hs

try:
    import typeguard  # noqa: F401
except ImportError:
    has_typeguard = False
else:
    has_typeguard = True


def assert_close(a: float, b: float) -> bool:
    assert np.isclose(a, b, rtol=1e-3).all()


@pytest.fixture
def datasets() -> Tuple[pd.Series, pd.Series, Dict[str, Any]]:
    df = pd.read_csv(Path("tests", "test_data.csv"), index_col=0, parse_dates=True)
    with open(Path("tests", "test_data.json")) as f:
        sig_expected = json.load(f)
    return df.q_mmpd, df.p_mmpd, sig_expected


@pytest.mark.skipif(has_typeguard, reason="Broken if Typeguard is enabled")
def test_signatures(datasets):
    q_mmpd, p_mmpd, sig_expected = datasets
    sig = hs.HydroSignatures(q_mmpd, p_mmpd)
    sig_dict = sig.values._asdict()
    mm = sig_expected.pop("mean_monthly")
    assert all(np.isclose(sig_dict[key], val, rtol=1.0e-3) for key, val in sig_expected.items())
    assert np.allclose(pd.DataFrame(mm), sig.values.mean_monthly)


def test_show_versions():
    f = io.StringIO()
    hs.show_versions(file=f)
    assert "INSTALLED VERSIONS" in f.getvalue()
