import pytest
from alloy_core.schemas.composition import MaterialComposition, ATOMIC_WEIGHTS


def test_composition_normalization():
    # Percentage input
    comp = MaterialComposition(fractions={"Ti": 90.0, "Al": 6.0, "V": 4.0}, basis="weight")
    assert abs(comp.fractions["Ti"] - 0.90) < 1e-4
    assert abs(comp.fractions["Al"] - 0.06) < 1e-4
    assert abs(comp.fractions["V"] - 0.04) < 1e-4
    assert comp.base_element == "Ti"
    assert comp.alloy_family == "titanium"


def test_composition_conversions():
    # Ti-6Al-4V (wt%) -> at% -> wt% round trip
    comp_wt = MaterialComposition(fractions={"Ti": 0.90, "Al": 0.06, "V": 0.04}, basis="weight")
    comp_at = comp_wt.to_atomic_fractions()
    assert comp_at.basis == "atomic"
    assert sum(comp_at.fractions.values()) == pytest.approx(1.0, rel=1e-4)

    comp_roundtrip = comp_at.to_weight_fractions()
    assert comp_roundtrip.basis == "weight"
    assert comp_roundtrip.fractions["Ti"] == pytest.approx(0.90, rel=1e-3)
    assert comp_roundtrip.fractions["Al"] == pytest.approx(0.06, rel=1e-3)
    assert comp_roundtrip.fractions["V"] == pytest.approx(0.04, rel=1e-3)


def test_composition_vec_and_entropy():
    # Equiatomic CoCrFeNi
    comp = MaterialComposition(fractions={"Co": 0.25, "Cr": 0.25, "Fe": 0.25, "Ni": 0.25}, basis="atomic")
    vec = comp.calculate_vec()
    # (9 + 6 + 8 + 10) / 4 = 33 / 4 = 8.25
    assert vec == pytest.approx(8.25, rel=1e-4)

    s_mix = comp.calculate_ideal_mixing_entropy()
    # R * ln(4) = 8.314 * 1.386 = 11.526 J/(mol·K)
    assert s_mix == pytest.approx(11.526, rel=1e-2)


def test_formula_string():
    comp = MaterialComposition(fractions={"Ti": 0.90, "Al": 0.06, "V": 0.04}, basis="weight")
    formula = comp.formula_string()
    assert "Ti" in formula
    assert "6Al" in formula
    assert "4V" in formula


def test_invalid_element():
    with pytest.raises(ValueError):
        MaterialComposition(fractions={"FakeElement": 1.0})
