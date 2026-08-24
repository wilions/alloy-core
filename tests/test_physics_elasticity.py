import pytest
from alloy_core.physics.elasticity import UnifiedElasticityEngine


def test_cubic_elastic_homogenization():
    # Pure Nickel single crystal stiffness constants (GPa)
    # C11 = 247.0, C12 = 147.0, C44 = 125.0
    res = UnifiedElasticityEngine.homogenize_cubic(
        c11_gpa=247.0,
        c12_gpa=147.0,
        c44_gpa=125.0
    )

    # Bulk modulus K = (C11 + 2*C12) / 3 = (247 + 294) / 3 = 180.33 GPa
    assert res.bulk_modulus_vrh_gpa == pytest.approx(180.33, rel=1e-2)
    # Polycrystalline Ni E is ~ 200-220 GPa
    assert res.youngs_modulus_gpa == pytest.approx(215.0, rel=0.10)
    # Ni is ductile: Cauchy pressure C12 - C44 = 147 - 125 = 22 GPa > 0
    assert res.cauchy_pressure_gpa == 22.0
    assert res.pugh_ratio > 1.75  # Ductile Pugh criterion
