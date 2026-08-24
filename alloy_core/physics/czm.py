"""
Unified Cohesive Zone Model (CZM) & Fracture Mechanics Engine.
Computes interfacial traction-separation response, critical energy release rate G_c,
plane-strain fracture toughness K_IC, and DBTT temperature transitions.
"""

from __future__ import annotations
import math
from typing import Dict, Optional, Tuple
from pydantic import BaseModel, Field


class CZMResult(BaseModel):
    """Result of cohesive zone fracture modeling."""
    cohesive_strength_mpa: float = Field(..., description="Peak traction sigma_max (MPa)")
    critical_separation_nm: float = Field(..., description="Critical displacement delta_c (nm)")
    critical_energy_release_rate_j_m2: float = Field(..., description="Fracture energy G_c (J/m²)")
    fracture_toughness_kic_mpa_m05: float = Field(..., description="Plane-strain K_IC (MPa·m^0.5)")
    brittle_cleavage_stress_mpa: float = Field(..., description="Cleavage stress sigma_f (MPa)")
    predicted_dbtt_k: Optional[float] = Field(default=None, description="Predicted DBTT (K)")


class UnifiedCZMEngine:
    """Consolidated Cohesive Zone and Griffith-Irwin-Orowan fracture solver."""

    @classmethod
    def evaluate_fracture_toughness(
        cls,
        youngs_modulus_gpa: float,
        poissons_ratio: float = 0.33,
        yield_strength_mpa: float = 800.0,
        grain_size_um: float = 10.0,
        porosity_fraction: float = 0.005,
        inclusion_volume_fraction: float = 0.001,
        grain_boundary_energy_j_m2: float = 0.6,
        surface_energy_j_m2: float = 2.0
    ) -> CZMResult:
        """
        Calculates cohesive traction-separation and macroscopic K_IC.
        Integrates metallic plastic dissipation, grain size Hall-Petch cleavage, and porosity.
        """
        E_pa = youngs_modulus_gpa * 1e9
        nu = poissons_ratio
        d_m = grain_size_um * 1e-6

        # 1. Effective fracture energy G_c (J/m²)
        g_cleave = max(2.0 * surface_energy_j_m2 - grain_boundary_energy_j_m2, 0.5)

        # Orowan plastic work dissipation in ductile metals (typically ~15,000 - 30,000 J/m²)
        plastic_dissipation_base = 20000.0 * (yield_strength_mpa / 800.0) * (1.0 - math.sqrt(max(porosity_fraction, 0.0)))
        G_c = g_cleave + plastic_dissipation_base
        
        # Inclusion penalty
        if inclusion_volume_fraction > 0.0:
            G_c *= math.exp(-25.0 * inclusion_volume_fraction)

        # 2. Cohesive strength sigma_max (MPa)
        sigma_max_mpa = (youngs_modulus_gpa * 1e3 / 10.0) * (1.0 - 2.5 * porosity_fraction)

        # 3. Critical separation delta_c = G_c / (e * sigma_max)
        delta_c_m = (G_c / (math.e * (sigma_max_mpa * 1e6))) if sigma_max_mpa > 0 else 1e-9
        delta_c_nm = delta_c_m * 1e9

        # 4. Plane-strain fracture toughness K_IC = sqrt(E * G_c / (1 - nu^2))
        E_prime = E_pa / (1.0 - nu**2)
        kic_pa_m05 = math.sqrt(E_prime * G_c)
        kic_mpa_m05 = kic_pa_m05 * 1e-6

        # 5. Cleavage stress and DBTT estimation
        sigma_cleavage_mpa = math.sqrt((2.0 * E_pa * surface_energy_j_m2) / (math.pi * max(d_m, 1e-8))) * 1e-6
        if yield_strength_mpa > 0:
            dbtt_k = 300.0 * (yield_strength_mpa / max(sigma_cleavage_mpa, 1.0))**0.5
        else:
            dbtt_k = None

        return CZMResult(
            cohesive_strength_mpa=round(sigma_max_mpa, 2),
            critical_separation_nm=round(delta_c_nm, 3),
            critical_energy_release_rate_j_m2=round(G_c, 2),
            fracture_toughness_kic_mpa_m05=round(kic_mpa_m05, 2),
            brittle_cleavage_stress_mpa=round(sigma_cleavage_mpa, 2),
            predicted_dbtt_k=round(dbtt_k, 1) if dbtt_k else None
        )
