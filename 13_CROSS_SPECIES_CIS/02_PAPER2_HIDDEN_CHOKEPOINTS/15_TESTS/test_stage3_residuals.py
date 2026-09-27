"""Unit tests for Stage 3 residualization math (Paper 2, Freeze 1 gate).

Run: pytest 15_TESTS/test_stage3_residuals.py -q
(stdlib + numpy/pandas/scipy only)
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "04_DEGREE_CONTROL"))

from compute_residuals import fit_predict, orthogonality  # noqa: E402


def _synthetic_subject(n: int = 456, seed: int = 0):
    """CIS ~ log-linear in degree + heteroscedastic noise (realistic shape)."""
    rng = np.random.default_rng(seed)
    degree = rng.integers(20, 220, size=n).astype(float)
    cis = 1e-5 * np.log1p(degree) + rng.normal(0, 2e-6, size=n) * (degree / 100)
    return degree, cis


def test_ols_recovers_linear_truth():
    rng = np.random.default_rng(1)
    x = rng.uniform(10, 200, 500)
    y = 3.0 * x - 2.0 + rng.normal(0, 0.01, 500)
    fitted, _ = fit_predict(x, y, "ols")
    assert np.abs(fitted - y).mean() < 0.05


def test_spline_beats_linear_on_nonlinear_truth():
    """Amendment 2 primary: raw-CIS spline must beat linear on nonlinear truth."""
    degree, cis = _synthetic_subject(seed=2)
    fitted_lin, _ = fit_predict(degree, cis, "ols")
    fitted_spl, _ = fit_predict(degree, cis, "spline_ols", df=4)
    assert np.isfinite(fitted_spl).all()
    assert np.abs(cis - fitted_spl).mean() < np.abs(cis - fitted_lin).mean()


def test_spline_handles_negative_cis_without_nan():
    """Regression test for Amendments 1-2: signed CIS must not produce NaN."""
    rng = np.random.default_rng(7)
    degree = rng.integers(20, 220, 300).astype(float)
    cis = 1e-5 * np.log1p(degree) + rng.normal(0, 8e-6, 300)  # ~40% negative
    fitted, _ = fit_predict(degree, cis, "spline_ols", df=4)
    assert np.isfinite(fitted).all()


def test_residual_orthogonal_to_degree_after_correct_fit():
    degree, cis = _synthetic_subject(seed=3)
    fitted, _ = fit_predict(degree, cis, "spline_ols", df=4)
    resid = cis - fitted
    rho = orthogonality(resid, degree)
    assert abs(rho) < 0.15  # loose bound: noise is heteroscedastic by design


def test_orthogonality_detects_uncorrected_degree_signal():
    rng = np.random.default_rng(4)
    x = rng.uniform(10, 200, 400)
    y = 1e-5 * x + rng.normal(0, 1e-6, 400)   # raw CIS still carries degree
    assert abs(orthogonality(y, x)) > 0.7


def test_quantile_bins_median_flat_within_bin():
    rng = np.random.default_rng(5)
    x = rng.uniform(0, 100, 1000)
    y = np.sin(x / 10) + rng.normal(0, 0.001, 1000)
    fitted, _ = fit_predict(x, y, "quantile_bins", q=20)
    # fitted values must be one of the bin medians (few unique values)
    assert len(np.unique(np.round(fitted, 10))) <= 20


def test_poly_df1_matches_ols():
    rng = np.random.default_rng(6)
    x = rng.uniform(0, 50, 300)
    y = 2 * x + 1 + rng.normal(0, 0.01, 300)
    f1, _ = fit_predict(x, y, "ols")
    f2, _ = fit_predict(x, y, "poly", df=1)
    assert np.allclose(f1, f2, atol=1e-8)
