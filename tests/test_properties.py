import pytest
from alloy_core.schemas.properties import (
    PropertyTensor,
    MechanicalProperties,
    ThermophysicalProperties,
    UncertaintyEstimate,
    DistributionType
)


def test_property_tensor_and_uncertainty():
    mech = MechanicalProperties(
        yield_strength_mpa=850.0,
        ultimate_tensile_strength_mpa=950.0,
        elongation_pct=12.5,
        youngs_modulus_gpa=115.0
    )
    thermo = ThermophysicalProperties(
        thermal_conductivity_w_m_k=18.5,
        specific_heat_j_kg_k=520.0,
        density_kg_m3=4430.0,
        liquidus_temp_k=1930.0,
        solidus_temp_k=1880.0
    )
    unc = {
        "yield_strength_mpa": UncertaintyEstimate(
            mean=850.0,
            std_dev=25.0,
            distribution=DistributionType.NORMAL
        )
    }
    prop_tensor = PropertyTensor(
        mechanical=mech,
        thermophysical=thermo,
        uncertainties=unc
    )

    assert prop_tensor.mechanical.yield_strength_mpa == 850.0
    assert prop_tensor.thermophysical.thermal_conductivity_w_m_k == 18.5
    # 95% interval for N(850, 25) = [850 - 1.96*25, 850 + 1.96*25] = [801.0, 899.0]
    ci = prop_tensor.uncertainties["yield_strength_mpa"].credible_interval_95
    assert ci[0] == pytest.approx(801.0, rel=1e-3)
    assert ci[1] == pytest.approx(899.0, rel=1e-3)
