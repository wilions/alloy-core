import pytest
from alloy_core.schemas.microstructure import (
    MicrostructureState,
    PrecipitatePopulation,
    GrainMorphology,
    ComplexionState
)


def test_microstructure_state():
    precips = {
        "Al3Sc": PrecipitatePopulation(
            phase_name="Al3Sc",
            mean_radius_nm=2.5,
            volume_fraction=0.015,
            number_density_m3=1e22
        )
    }
    micro = MicrostructureState(
        grains=GrainMorphology(mean_grain_size_um=1.5, morphology_type="bimodal"),
        precipitates=precips,
        relative_density=0.998,
        dislocation_density_m2=5e14
    )
    assert micro.grains.mean_grain_size_um == 1.5
    assert micro.total_precipitate_volume_fraction() == pytest.approx(0.015)
    assert micro.relative_density == 0.998
