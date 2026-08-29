"""
Constitutive Strengthening Superposition Kernels.
Computes Hall-Petch grain boundary strengthening, Orowan dislocation looping,
solid solution strengthening, and precipitate shearing superposition.
"""

from __future__ import annotations
import math
from typing import Dict, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class StrengthBreakdownResult:
    lattice_friction_mpa: float
    hall_petch_mpa: float
    solid_solution_mpa: float
    precipitation_mpa: float
    dislocation_forest_mpa: float
    total_yield_strength_mpa: float
    ultimate_tensile_strength_mpa: float


def calculate_yield_strength_superposition(
    grain_size_um: float,
    solute_concentrations: Dict[str, float],
    precipitate_volume_fraction: float = 0.0,
    mean_precipitate_radius_nm: float = 5.0,
    base_element: str = "Ni",
    dislocation_density_m2: float = 1e12,
    shear_modulus_gpa: float = 80.0,
    burgers_vector_nm: float = 0.25,
    taylor_factor: float = 3.06
) -> StrengthBreakdownResult:
    """
    Computes metallic yield strength via linear/root-sum-square superposition:
    sigma_y = sigma_0 + Delta sigma_HP + sqrt( Delta sigma_SS^2 + Delta sigma_ppt^2 ) + Delta sigma_rho
    """
    # 1. Lattice friction stress sigma_0
    friction_db = {"Ni": 50.0, "Fe": 70.0, "Al": 20.0, "Ti": 120.0, "Mo": 250.0, "W": 350.0}
    sigma_0 = friction_db.get(base_element, 60.0)
    
    # 2. Hall-Petch grain boundary strengthening: k_HP / sqrt(d)
    k_hp_db = {"Ni": 450.0, "Fe": 550.0, "Al": 200.0, "Ti": 600.0, "Mo": 750.0}
    k_hp = k_hp_db.get(base_element, 450.0)
    d_eff = max(0.05, grain_size_um)
    delta_hp = k_hp / math.sqrt(d_eff)
    
    # 3. Solid solution strengthening: sum( k_i * c_i^0.5 )
    ss_coeff_db = {"Cr": 350.0, "Mo": 850.0, "W": 920.0, "Al": 220.0, "Ti": 450.0, "Co": 80.0, "Fe": 110.0}
    delta_ss = 0.0
    for elem, c_val in solute_concentrations.items():
        if elem != base_element:
            k_elem = ss_coeff_db.get(elem, 250.0)
            delta_ss += k_elem * math.sqrt(max(0.0, c_val))
            
    # 4. Precipitation strengthening (Orowan looping / Friedel shearing)
    g_mpa = shear_modulus_gpa * 1000.0
    b_nm = burgers_vector_nm
    r_nm = max(0.5, mean_precipitate_radius_nm)
    f_v = max(0.0, min(1.0, precipitate_volume_fraction))
    
    if f_v > 0:
        # Effective inter-particle spacing lambda = sqrt(2*pi/3) * r * (1/sqrt(f) - 1)
        lambda_nm = max(1.0, math.sqrt(2.0 * math.pi / 3.0) * r_nm * (1.0 / math.sqrt(f_v) - 1.0))
        # Orowan bowing stress: M * (0.8 * G * b / (2 * pi * lambda)) * ln(2 * r / r_0)
        delta_ppt = taylor_factor * (0.8 * g_mpa * (b_nm / lambda_nm) / (2.0 * math.pi)) * math.log(max(1.1, 2.0 * r_nm / 0.5))
    else:
        delta_ppt = 0.0
        
    # 5. Taylor dislocation forest hardening: M * alpha * G * b * sqrt(rho)
    rho = max(1e10, dislocation_density_m2)
    b_m = burgers_vector_nm * 1e-9
    delta_rho = taylor_factor * 0.3 * (g_mpa * 1e6) * b_m * math.sqrt(rho) * 1e-6
    
    # 6. Combined yield strength
    direct_terms = sigma_0 + delta_hp + delta_rho
    obstacle_terms = math.sqrt(delta_ss**2 + delta_ppt**2)
    total_yield = direct_terms + obstacle_terms
    uts = total_yield * 1.25 + 50.0
    
    return StrengthBreakdownResult(
        lattice_friction_mpa=round(sigma_0, 1),
        hall_petch_mpa=round(delta_hp, 1),
        solid_solution_mpa=round(delta_ss, 1),
        precipitation_mpa=round(delta_ppt, 1),
        dislocation_forest_mpa=round(delta_rho, 1),
        total_yield_strength_mpa=round(total_yield, 1),
        ultimate_tensile_strength_mpa=round(uts, 1)
    )
