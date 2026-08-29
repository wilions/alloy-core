"""
Cohesive Zone Modeling (CZM) and Fracture Mechanics Kernels.
Implements exponential (Needleman), bilinear, and PPR traction-separation laws,
Griffith-Irwin energy release rates, and Hall-Petch cleavage transitions.
"""

from __future__ import annotations
import math
from typing import Dict, Tuple, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class TractionSeparationPoint:
    separation_nm: float
    normal_traction_mpa: float
    tangential_traction_mpa: float


def exponential_needleman_tsl(
    delta_n_nm: float,
    sigma_max_mpa: float,
    critical_separation_delta_0_nm: float
) -> float:
    """
    Exponential Needleman Traction-Separation Law:
    T_n(delta) = sigma_max * (delta / delta_0) * exp( 1 - delta / delta_0 )
    """
    if critical_separation_delta_0_nm <= 0:
        return 0.0
    ratio = max(0.0, delta_n_nm / critical_separation_delta_0_nm)
    return sigma_max_mpa * ratio * math.exp(1.0 - ratio)


def bilinear_tsl(
    delta_n_nm: float,
    sigma_max_mpa: float,
    delta_init_nm: float,
    delta_final_nm: float
) -> float:
    """
    Bilinear Traction-Separation Law:
    Linear elasticity up to delta_init, linear softening from delta_init to delta_final.
    """
    if delta_n_nm <= 0:
        return 0.0
    if delta_n_nm <= delta_init_nm:
        return sigma_max_mpa * (delta_n_nm / max(1e-6, delta_init_nm))
    elif delta_n_nm < delta_final_nm:
        return sigma_max_mpa * (delta_final_nm - delta_n_nm) / max(1e-6, delta_final_nm - delta_init_nm)
    else:
        return 0.0


def evaluate_fracture_energy_and_kic(
    youngs_modulus_gpa: float,
    poissons_ratio: float,
    yield_strength_mpa: float,
    surface_energy_j_m2: float = 2.0,
    grain_boundary_energy_j_m2: float = 0.6,
    porosity_fraction: float = 0.0,
    inclusion_volume_fraction: float = 0.0
) -> Tuple[float, float, float]:
    """
    Computes effective fracture energy G_c (J/m²), cohesive strength sigma_max (MPa),
    and plane-strain fracture toughness K_IC (MPa·m^0.5).
    """
    # Ideal cleavage energy (Griffith)
    g_cleave = max(2.0 * surface_energy_j_m2 - grain_boundary_energy_j_m2, 0.5)
    
    # Plastic dissipation work in ductile metallic matrices
    plastic_work = 20000.0 * (yield_strength_mpa / 800.0) * max(0.1, 1.0 - math.sqrt(max(porosity_fraction, 0.0)))
    g_c = g_cleave + plastic_work
    
    if inclusion_volume_fraction > 0:
        g_c *= math.exp(-25.0 * inclusion_volume_fraction)
        
    sigma_max_mpa = (youngs_modulus_gpa * 1000.0 / 10.0) * max(0.1, 1.0 - 2.5 * porosity_fraction)
    
    e_prime = (youngs_modulus_gpa * 1e9) / (1.0 - poissons_ratio**2)
    kic_pa_m05 = math.sqrt(e_prime * g_c)
    kic_mpa_m05 = kic_pa_m05 * 1e-6
    
    return float(g_c), float(sigma_max_mpa), float(kic_mpa_m05)
