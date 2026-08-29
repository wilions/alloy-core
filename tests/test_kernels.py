"""
Unit and Conformance Tests for AlloyCore Fast Physics Kernels.
Verifies Rosenthal thermal, VRH elasticity, CZM fracture, and strength superposition kernels.
"""

import math
import numpy as np
import pytest
from alloy_core.kernels.thermal import (
    rosenthal_3d_point_source,
    eagar_tsai_surface_temperature,
    cooling_rate_and_gradient
)
from alloy_core.kernels.elasticity import vrh_cubic_homogenization
from alloy_core.kernels.fracture import (
    exponential_needleman_tsl,
    bilinear_tsl,
    evaluate_fracture_energy_and_kic
)
from alloy_core.kernels.strength import calculate_yield_strength_superposition


def test_rosenthal_thermal_kernel():
    """Test 3D Rosenthal point-source temperature calculations."""
    # Point directly at beam tail
    t_val = rosenthal_3d_point_source(
        x=-100e-6,
        y=0.0,
        z=0.0,
        laser_power_w=200.0,
        scan_speed_m_s=1.0,
        absorptivity=0.4,
        thermal_conductivity_w_m_k=25.0,
        thermal_diffusivity_m2_s=6.0e-6,
        preheat_temp_k=300.0
    )
    assert t_val > 1000.0, f"Expected melt-pool temperature > 1000 K, got {t_val}"
    
    # Vectorized check
    x_arr = np.linspace(-500e-6, 0.0, 10)
    y_arr = np.zeros_like(x_arr)
    z_arr = np.zeros_like(x_arr)
    t_arr = rosenthal_3d_point_source(
        x=x_arr,
        y=y_arr,
        z=z_arr,
        laser_power_w=200.0,
        scan_speed_m_s=1.0,
        absorptivity=0.4,
        thermal_conductivity_w_m_k=25.0,
        thermal_diffusivity_m2_s=6.0e-6,
        preheat_temp_k=300.0
    )
    assert len(t_arr) == 10
    assert np.all(t_arr >= 300.0)


def test_cooling_rate_and_gradient():
    """Test thermal gradient and cooling rate calculation."""
    g, r, cr = cooling_rate_and_gradient(
        laser_power_w=200.0,
        scan_speed_m_s=1.0,
        absorptivity=0.4,
        thermal_conductivity_w_m_k=25.0,
        thermal_diffusivity_m2_s=6.0e-6,
        solidus_temp_k=1550.0,
        liquidus_temp_k=1620.0
    )
    assert g > 1e5
    assert r == 1.0
    assert cr > 1e5


def test_vrh_elasticity_kernel():
    """Test cubic VRH polycrystal averaging for Nickel single-crystal constants."""
    # Nickel single-crystal: c11 = 247 GPa, c12 = 147 GPa, c44 = 125 GPa
    res = vrh_cubic_homogenization(c11=247.0, c12=147.0, c44=125.0)
    assert 170.0 < res.bulk_modulus_gpa < 190.0
    assert 70.0 < res.shear_modulus_gpa < 95.0
    assert 190.0 < res.youngs_modulus_gpa < 240.0
    assert 0.28 < res.poissons_ratio < 0.35


def test_fracture_czm_kernel():
    """Test CZM traction-separation and fracture toughness."""
    g_c, sigma_max, kic = evaluate_fracture_energy_and_kic(
        youngs_modulus_gpa=210.0,
        poissons_ratio=0.30,
        yield_strength_mpa=900.0
    )
    assert g_c > 1000.0
    assert sigma_max > 1000.0
    assert 40.0 < kic < 150.0

    t_exp = exponential_needleman_tsl(delta_n_nm=5.0, sigma_max_mpa=1500.0, critical_separation_delta_0_nm=5.0)
    assert round(t_exp, 1) == 1500.0


def test_strength_superposition_kernel():
    """Test Hall-Petch + Orowan yield strength superposition."""
    res = calculate_yield_strength_superposition(
        grain_size_um=10.0,
        solute_concentrations={"Cr": 0.20, "Al": 0.05, "Mo": 0.03},
        precipitate_volume_fraction=0.15,
        mean_precipitate_radius_nm=8.0,
        base_element="Ni"
    )
    assert res.total_yield_strength_mpa > 700.0
    assert res.hall_petch_mpa > 100.0
    assert res.precipitation_mpa > 100.0
    assert res.ultimate_tensile_strength_mpa > res.total_yield_strength_mpa
