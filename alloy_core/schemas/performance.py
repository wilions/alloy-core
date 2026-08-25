"""
Canonical Long-Term Lifecycle Performance Schemas for alloy-core.
Covers microstructural fatigue, creep rupture, and high-temperature environmental oxidation.
"""

from __future__ import annotations
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class FatigueSNState(BaseModel):
    """Microstructure-sensitive fatigue life metrics and S-N response."""
    fatigue_limit_mpa: float = Field(..., gt=0.0, description="Fatigue strength at 10^7 cycles (endurance limit) in MPa")
    r_ratio: float = Field(default=-1.0, description="Stress ratio R = sigma_min / sigma_max")
    basquin_exponent_b: float = Field(default=-0.1, description="Basquin fatigue strength exponent")
    fatigue_indicator_parameter_fip: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Tanaka-Mura / microstructural plastic slip initiation indicator"
    )
    predicted_cycles_to_initiation: Optional[float] = Field(default=None, gt=0.0)


class CreepRuptureState(BaseModel):
    """High-temperature creep resistance and stress-rupture metrics."""
    test_temperature_k: float = Field(..., gt=0.0, description="Creep test temperature in Kelvin")
    applied_stress_mpa: float = Field(..., gt=0.0, description="Applied constant tensile stress in MPa")
    minimum_creep_rate_1_s: float = Field(..., gt=0.0, description="Steady-state secondary creep rate (1/s)")
    time_to_rupture_hours: float = Field(..., gt=0.0, description="Predicted time to rupture in hours")
    monkman_grant_product: float = Field(default=0.1, gt=0.0, description="dot{eps}_s * t_r constant")
    larson_miller_parameter: float = Field(..., gt=0.0, description="LMP = T * (20 + log10(t_r)) / 1000")


class OxidationKineticsState(BaseModel):
    """High-temperature oxidation and scale growth kinetics."""
    exposure_temperature_k: float = Field(..., gt=0.0)
    duration_hours: float = Field(..., gt=0.0)
    parabolic_rate_constant_kp_mg2_cm4_s: float = Field(..., ge=0.0, description="Parabolic oxidation rate kp")
    mass_gain_mg_cm2: float = Field(..., ge=0.0, description="Total mass gain per unit area")
    oxide_scale_thickness_um: float = Field(..., ge=0.0, description="Protective oxide scale thickness in um")
    internal_oxidation_depth_um: float = Field(default=0.0, ge=0.0, description="Depth of internal oxidation penetration")
    spallation_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="Oxide scale spallation risk [0, 1]")


class PerformanceEnvelope(BaseModel):
    """Holistic multi-physics lifecycle performance envelope."""
    fatigue: Optional[FatigueSNState] = None
    creep: Optional[CreepRuptureState] = None
    oxidation: Optional[OxidationKineticsState] = None
    max_service_temperature_k: float = Field(..., gt=0.0, description="Allowable maximum continuous service temperature")
    provenance_models: Dict[str, str] = Field(default_factory=dict)
