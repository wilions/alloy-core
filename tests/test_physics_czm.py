import pytest
from alloy_core.physics.czm import UnifiedCZMEngine


def test_czm_fracture_toughness():
    # Ti-6Al-4V typical parameters
    res = UnifiedCZMEngine.evaluate_fracture_toughness(
        youngs_modulus_gpa=115.0,
        poissons_ratio=0.33,
        yield_strength_mpa=880.0,
        grain_size_um=5.0,
        porosity_fraction=0.002,
        inclusion_volume_fraction=0.0005
    )

    assert res.cohesive_strength_mpa > 1000.0
    assert res.fracture_toughness_kic_mpa_m05 > 40.0  # Ti-6Al-4V K_IC in ~50-80 MPa m^0.5 range
    assert res.fracture_toughness_kic_mpa_m05 < 120.0
    assert res.critical_energy_release_rate_j_m2 > 10.0


def test_czm_porosity_penalty():
    res_dense = UnifiedCZMEngine.evaluate_fracture_toughness(
        youngs_modulus_gpa=115.0,
        porosity_fraction=0.001
    )
    res_porous = UnifiedCZMEngine.evaluate_fracture_toughness(
        youngs_modulus_gpa=115.0,
        porosity_fraction=0.05
    )
    # Porosity significantly degrades K_IC and cohesive strength
    assert res_dense.fracture_toughness_kic_mpa_m05 > res_porous.fracture_toughness_kic_mpa_m05
    assert res_dense.cohesive_strength_mpa > res_porous.cohesive_strength_mpa
