import pytest
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.manufacturing import (
    ProcessRecipe,
    ManufacturingRoute,
    LPBFParameters,
    PMSinteringParameters
)
from alloy_core.digital_twin.runner import DigitalTwinRunner


def test_am_digital_twin_execution():
    comp = MaterialComposition(
        fractions={"Al": 0.965, "Sc": 0.007, "Zr": 0.003, "Mg": 0.025},
        basis="weight"
    )
    recipe = ProcessRecipe(
        recipe_id="REC-SCALMALLOY-LPBF",
        route=ManufacturingRoute.LPBF,
        lpbf_params=LPBFParameters(
            laser_power_w=250.0,
            scan_velocity_m_s=1.2,
            hatch_spacing_um=90.0,
            layer_thickness_um=30.0
        )
    )

    state = DigitalTwinRunner.run_simulation(comp, recipe)

    assert state.status == "simulated"
    assert state.composition.base_element == "Al"
    assert state.microstructure is not None
    assert state.microstructure.grains.mean_grain_size_um > 0.0
    assert state.properties is not None
    assert state.properties.mechanical.yield_strength_mpa > 200.0  # Scalmalloy strength
    assert state.properties.mechanical.fracture_toughness_kic_mpa_m05 > 15.0
    assert state.evidence.provenance_hash is not None


def test_pm_sintering_digital_twin_execution():
    comp = MaterialComposition(
        fractions={"Mo": 0.985, "Ti": 0.012, "Zr": 0.002, "C": 0.001},
        basis="weight"
    )
    recipe = ProcessRecipe(
        recipe_id="REC-TZM-SPS",
        route=ManufacturingRoute.PM_SINTERING,
        pm_params=PMSinteringParameters(
            sintering_temp_k=1873.15,
            dwell_time_minutes=20.0
        )
    )

    state = DigitalTwinRunner.run_simulation(comp, recipe)

    assert state.status == "simulated"
    assert state.composition.base_element == "Mo"
    assert state.microstructure.relative_density > 0.95
    assert state.properties.mechanical.youngs_modulus_gpa == 320.0
    assert state.properties.mechanical.yield_strength_mpa > 600.0
    assert state.evidence.origin_pillar.value == "alloy-sinter"
