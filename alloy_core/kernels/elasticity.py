"""
Voigt-Reuss-Hill (VRH) Elastic Moduli Homogenization Kernels.
Computes isotropic polycrystalline bulk modulus K, shear modulus G,
Young's modulus E, Poisson's ratio nu, and Pugh ratio from single-crystal stiffness C_ij.
"""

from __future__ import annotations
import math
from typing import Dict, Tuple
from dataclasses import dataclass


@dataclass(frozen=True)
class VRHModuliResult:
    bulk_modulus_gpa: float
    shear_modulus_gpa: float
    youngs_modulus_gpa: float
    poissons_ratio: float
    pugh_ratio_k_g: float
    cauchy_pressure_gpa: float
    elastic_anisotropy_zenner: float


def vrh_cubic_homogenization(c11: float, c12: float, c44: float) -> VRHModuliResult:
    """
    Computes VRH polycrystal averages for cubic symmetry:
    K_V = K_R = (c11 + 2*c12) / 3
    G_V = (c11 - c12 + 3*c44) / 5
    G_R = 5 * (c11 - c12) * c44 / (4*c44 + 3*(c11 - c12))
    G_VRH = (G_V + G_R) / 2
    """
    k_vrh = (c11 + 2.0 * c12) / 3.0
    
    g_v = (c11 - c12 + 3.0 * c44) / 5.0
    denom = 4.0 * c44 + 3.0 * (c11 - c12)
    g_r = (5.0 * (c11 - c12) * c44 / denom) if denom > 0 else g_v
    
    g_vrh = 0.5 * (g_v + g_r)
    
    # Young's modulus E = 9 * K * G / (3 * K + G)
    e_vrh = (9.0 * k_vrh * g_vrh) / (3.0 * k_vrh + g_vrh) if (3.0 * k_vrh + g_vrh) > 0 else 0.0
    # Poisson's ratio nu = (3 * K - 2 * G) / (2 * (3 * K + G))
    nu_vrh = (3.0 * k_vrh - 2.0 * g_vrh) / (2.0 * (3.0 * k_vrh + g_vrh)) if (3.0 * k_vrh + g_vrh) > 0 else 0.3
    
    pugh = k_vrh / g_vrh if g_vrh > 0 else 0.0
    cauchy_p = c12 - c44
    zenner = (2.0 * c44) / (c11 - c12) if (c11 - c12) != 0 else 1.0
    
    return VRHModuliResult(
        bulk_modulus_gpa=round(k_vrh, 2),
        shear_modulus_gpa=round(g_vrh, 2),
        youngs_modulus_gpa=round(e_vrh, 2),
        poissons_ratio=round(nu_vrh, 4),
        pugh_ratio_k_g=round(pugh, 3),
        cauchy_pressure_gpa=round(cauchy_p, 2),
        elastic_anisotropy_zenner=round(zenner, 3)
    )
