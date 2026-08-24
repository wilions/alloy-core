import pytest
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.thermal import ThermalHistoryState
from alloy_core.physics.kwn import UnifiedKWNEngine, SYSTEM_PRECIPITATE_DB


def test_kwn_al3sc_precipitation():
    # Scalmalloy-like Al-Sc-Zr composition
    comp = MaterialComposition(
        fractions={"Al": 0.965, "Sc": 0.007, "Zr": 0.003, "Mg": 0.025},
        basis="weight"
    )

    # 4-hour aging at 325°C (598.15 K)
    th = ThermalHistoryState()
    times = [0.0, 60.0, 1800.0, 3600.0, 7200.0, 14400.0]
    temps = [298.15, 598.15, 598.15, 598.15, 598.15, 598.15]
    for t, T in zip(times, temps):
        th.add_point(t, T)

    res = UnifiedKWNEngine.solve(
        phase_name="Al3Sc",
        composition=comp,
        thermal_history=th,
        initial_mean_radius_nm=0.5
    )

    assert res.phase_name == "Al3Sc"
    assert res.mean_radius_nm > 0.5  # Precipitate grew
    assert res.mean_radius_nm < 40.0  # Nanoscale L12 precipitates
    assert res.number_density_m3 > 0.0


def test_kwn_empty_thermal():
    comp = MaterialComposition(fractions={"Al": 0.99, "Sc": 0.01})
    th = ThermalHistoryState()
    res = UnifiedKWNEngine.solve("Al3Sc", comp, th)
    assert res.mean_radius_nm == 0.0
