import pytest
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.properties import (
    PropertyTensor,
    MechanicalProperties,
    ThermophysicalProperties
)
from alloy_core.calibration.residual_calibrator import ResidualCalibrator, CalibrationAnchor


def test_residual_calibrator_workflow():
    calibrator = ResidualCalibrator()

    # Add anchors representing MatWeb Ti-6Al-4V records
    comp1 = MaterialComposition(fractions={"Ti": 0.90, "Al": 0.06, "V": 0.04}, basis="weight")
    calibrator.add_anchor(CalibrationAnchor(
        composition=comp1,
        property_name="yield_strength_mpa",
        experimental_value=880.0,
        theoretical_value=820.0,  # +60 MPa residual offset
        source_tag="MATWEB-TI64"
    ))

    # Add second anchor
    comp2 = MaterialComposition(fractions={"Ti": 0.92, "Al": 0.05, "V": 0.03}, basis="weight")
    calibrator.add_anchor(CalibrationAnchor(
        composition=comp2,
        property_name="yield_strength_mpa",
        experimental_value=830.0,
        theoretical_value=780.0,  # +50 MPa offset
        source_tag="MATWEB-TI-NEAR"
    ))

    # Query target composition near Ti-6Al-4V
    target = MaterialComposition(fractions={"Ti": 0.895, "Al": 0.062, "V": 0.043}, basis="weight")
    offset, uncertainty = calibrator.predict_residual("yield_strength_mpa", target)

    assert offset == pytest.approx(58.0, abs=5.0)  # Smoothly interpolated between 50 and 60
    assert uncertainty > 0.0

    # Calibrate a full property tensor
    uncal_tensor = PropertyTensor(
        mechanical=MechanicalProperties(
            yield_strength_mpa=815.0,
            ultimate_tensile_strength_mpa=910.0,
            elongation_pct=10.0
        ),
        thermophysical=ThermophysicalProperties(
            thermal_conductivity_w_m_k=7.0,
            specific_heat_j_kg_k=520.0,
            density_kg_m3=4430.0,
            liquidus_temp_k=1930.0,
            solidus_temp_k=1880.0
        )
    )

    cal_tensor = calibrator.calibrate_property_tensor(uncal_tensor, target)
    assert cal_tensor.mechanical.yield_strength_mpa > 860.0
    assert "yield_strength_mpa" in cal_tensor.uncertainties
    assert cal_tensor.uncertainties["yield_strength_mpa"].std_dev > 0.0


def test_fit_from_props():
    calibrator = ResidualCalibrator()
    records = [
        {"material_name": "Al 7075-T6", "composition": {"Al": 0.90, "Zn": 0.056, "Mg": 0.025, "Cu": 0.016}, "tensile_yield_strength_mpa": 503.0},
        {"material_name": "Al 6061-T6", "composition": {"Al": 0.979, "Mg": 0.01, "Si": 0.006, "Cu": 0.003}, "tensile_yield_strength_mpa": 276.0}
    ]
    count = calibrator.fit_from_props_and_phase(records)
    assert count == 2
