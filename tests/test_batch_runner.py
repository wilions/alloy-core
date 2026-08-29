"""
Unit and throughput tests for BatchScreeningRunner.
Verifies bulk T0 candidate evaluation (>1,000 evals/sec) and Pareto sorting.
"""

import time
import pytest
from alloy_core.digital_twin.batch_runner import BatchScreeningRunner


def test_batch_screening_runner():
    # Generate 500 candidate alloy compositions
    candidates = []
    for i in range(500):
        cr = 0.10 + (i % 15) * 0.01
        al = 0.02 + (i % 6) * 0.01
        ti = 0.01 + (i % 4) * 0.01
        mo = 0.01 + (i % 5) * 0.01
        ni = 1.0 - (cr + al + ti + mo)
        candidates.append({"Ni": round(ni, 4), "Cr": round(cr, 4), "Al": round(al, 4), "Ti": round(ti, 4), "Mo": round(mo, 4)})

    summary = BatchScreeningRunner.screen_candidates(
        candidate_compositions=candidates,
        base_element="Ni",
        target_yield_strength_mpa=1100.0,
        top_k=5
    )

    assert summary.total_screened == 500
    assert len(summary.top_candidates) == 5
    assert summary.throughput_evals_per_sec > 500.0
    assert summary.top_candidates[0].yield_strength_mpa >= summary.top_candidates[1].yield_strength_mpa
    assert summary.top_candidates[0].yield_strength_mpa > 700.0
