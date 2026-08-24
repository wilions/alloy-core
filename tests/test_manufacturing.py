import pytest
from alloy_core.schemas.manufacturing import (
    ManufacturingRoute,
    ProcessRecipe,
    LPBFParameters,
    PMSinteringParameters,
    ThermalCycleStage,
    HeatTreatmentSchedule
)


def test_lpbf_parameters():
    params = LPBFParameters(
        laser_power_w=250.0,
        scan_velocity_m_s=1.2,
        hatch_spacing_um=100.0,
        layer_thickness_um=30.0
    )
    # VED = P / (v * h * t) = 250 / (1200 * 0.1 * 0.03) = 250 / 3.6 = 69.44 J/mm³
    ved = params.volumetric_energy_density_j_mm3()
    assert ved == pytest.approx(69.444, rel=1e-3)


def test_heat_treatment_schedule():
    stages = [
        ThermalCycleStage(
            stage_name="Solutionize",
            start_temp_k=298.15,
            target_temp_k=1198.15,
            ramp_rate_k_s=10.0,
            dwell_time_seconds=3600.0
        ),
        ThermalCycleStage(
            stage_name="Aging",
            start_temp_k=298.15,
            target_temp_k=753.15,
            ramp_rate_k_s=5.0,
            dwell_time_seconds=14400.0
        )
    ]
    schedule = HeatTreatmentSchedule(schedule_name="T6", stages=stages)
    # Ramp 1: 900 / 10 = 90s + 3600s = 3690s
    # Ramp 2: 455 / 5 = 91s + 14400s = 14491s
    # Total = 18181s
    assert schedule.total_duration_seconds() == pytest.approx(18181.0, rel=1e-3)


def test_process_recipe_validation():
    recipe = ProcessRecipe(
        recipe_id="REC-001",
        route=ManufacturingRoute.LPBF
    )
    assert recipe.lpbf_params is not None
    assert recipe.lpbf_params.laser_power_w == 200.0
