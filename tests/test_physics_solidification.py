import pytest
from alloy_core.physics.solidification import UnifiedSolidificationEngine


def test_scheil_solidification_curve():
    # Aluminum alloy 6061-like freezing range
    res = UnifiedSolidificationEngine.calculate_scheil_curve(
        liquidus_temp_k=925.0,
        solidus_temp_k=855.0,
        partition_coefficient_k0=0.15
    )

    assert res.liquidus_temp_k == 925.0
    assert res.solidus_temp_k == 855.0
    assert res.freezing_range_k == 70.0
    assert len(res.solid_fractions) == 100
    assert res.solid_fractions[0] == 0.0
    assert res.solid_fractions[-1] == 1.0
    assert res.cracking_susceptibility_index > 0.0


def test_cracking_index_sensitivity():
    # Wide freezing range (high cracking) vs Narrow freezing range (low cracking)
    res_crack_prone = UnifiedSolidificationEngine.calculate_scheil_curve(
        liquidus_temp_k=930.0,
        solidus_temp_k=800.0,
        partition_coefficient_k0=0.10
    )
    res_resistant = UnifiedSolidificationEngine.calculate_scheil_curve(
        liquidus_temp_k=930.0,
        solidus_temp_k=910.0,
        partition_coefficient_k0=0.90
    )
    assert res_crack_prone.cracking_susceptibility_index > res_resistant.cracking_susceptibility_index
