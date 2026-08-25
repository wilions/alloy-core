"""
Integration tests for the cross-MCP synergy pipelines in alloy-core.
"""

import pytest
from alloy_core.synergy import (
    AMDurabilityPipeline,
    ClosedLoopDiscoveryPipeline,
    PMDurabilityPipeline
)


def test_am_durability_pipeline_execution():
    res = AMDurabilityPipeline.run(
        alloy_name="Inconel 718",
        composition={"Ni": 0.53, "Cr": 0.19, "Fe": 0.18, "Nb": 0.05, "Mo": 0.03, "Ti": 0.01, "Al": 0.01},
        base_element="Ni",
        laser_power_w=200.0,
        scan_speed_m_s=1.0
    )
    assert res.alloy_designation == "Inconel 718"
    assert res.melt_pool_dimensions_um["depth_um"] > 0
    assert res.mean_grain_size_um > 0
    assert res.fatigue_limit_mpa > 0
    assert res.creep_time_to_rupture_hours > 0
    assert isinstance(res.safe_operational_envelope, bool)


def test_closed_loop_discovery_cycle():
    res = ClosedLoopDiscoveryPipeline.run_cycle(
        target_property="yield_strength_mpa",
        target_value=1100.0,
        base_element="Ni"
    )
    assert res.predicted_property_value > 500.0
    assert res.active_learning_acquisition_score > 0
    assert res.thermodynamic_passed is True
    assert "recommendation" in res.model_dump()


def test_pm_durability_pipeline_execution():
    res = PMDurabilityPipeline.run(
        alloy_name="Mo-Ti-Zr-C",
        composition={"Mo": 0.98, "Ti": 0.01, "Zr": 0.008, "C": 0.002},
        sintering_temp_k=1723.15,
        dwell_time_min=25.0
    )
    assert res.alloy_name == "Mo-Ti-Zr-C"
    assert 0.8 < res.final_sintered_relative_density <= 1.0
    assert res.yield_strength_mpa > 0
    assert res.creep_rupture_life_hours > 0
