"""
Canonical Property Tensor and Uncertainty Schemas for the Alloy Intelligence Suite.
Enforces rigorous SI units, standard mechanical/thermal descriptors, and uncertainty propagation.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, Optional, Tuple, Any
from pydantic import BaseModel, Field, model_validator


class DistributionType(str, Enum):
    NORMAL = "normal"
    LOGNORMAL = "lognormal"
    UNIFORM = "uniform"
    EMPIRICAL = "empirical"


class UncertaintyEstimate(BaseModel):
    """Parametric or empirical uncertainty description for physical measurements and predictions."""
    mean: float = Field(..., description="Expected value / central estimate")
    std_dev: float = Field(default=0.0, ge=0.0, description="Standard deviation (1-sigma)")
    distribution: DistributionType = Field(default=DistributionType.NORMAL, description="Distribution profile")
    credible_interval_95: Tuple[float, float] = Field(default=(0.0, 0.0), description="95% credible interval [q0.025, q0.975]")
    provenance: str = Field(default="model_epistemic", description="Origin of uncertainty estimate")

    @model_validator(mode="after")
    def compute_interval(self) -> "UncertaintyEstimate":
        if self.credible_interval_95 == (0.0, 0.0) and self.std_dev > 0.0:
            if self.distribution == DistributionType.NORMAL:
                self.credible_interval_95 = (self.mean - 1.96 * self.std_dev, self.mean + 1.96 * self.std_dev)
            elif self.distribution == DistributionType.UNIFORM:
                half_w = 1.732 * self.std_dev
                self.credible_interval_95 = (self.mean - half_w, self.mean + half_w)
        return self


class MechanicalProperties(BaseModel):
    """Consolidated mechanical performance indicators."""
    yield_strength_mpa: float = Field(..., ge=0.0, description="0.2% offset yield strength in MPa")
    ultimate_tensile_strength_mpa: float = Field(..., ge=0.0, description="Ultimate tensile strength in MPa")
    elongation_pct: float = Field(default=0.0, ge=0.0, description="Tensile elongation to failure (%)")
    youngs_modulus_gpa: float = Field(default=100.0, gt=0.0, description="Elastic modulus in GPa")
    shear_modulus_gpa: Optional[float] = Field(default=None, gt=0.0, description="Shear modulus in GPa")
    poissons_ratio: float = Field(default=0.33, ge=0.0, le=0.5, description="Poisson's ratio")
    hardness_hv: Optional[float] = Field(default=None, ge=0.0, description="Vickers microhardness (HV)")
    fracture_toughness_kic_mpa_m05: Optional[float] = Field(default=None, ge=0.0, description="Plane-strain fracture toughness K_IC in MPa·m^0.5")
    dbtt_k: Optional[float] = Field(default=None, description="Ductile-to-brittle transition temperature in Kelvin")
    strengthening_breakdown_mpa: Dict[str, float] = Field(
        default_factory=dict,
        description="Decomposition: {'lattice_friction': ..., 'solid_solution': ..., 'hall_petch': ..., 'precipitation': ..., 'taylor_dislocation': ...}"
    )


class ThermophysicalProperties(BaseModel):
    """Thermophysical and transport properties."""
    thermal_conductivity_w_m_k: float = Field(..., gt=0.0, description="Thermal conductivity k in W/(m·K)")
    specific_heat_j_kg_k: float = Field(..., gt=0.0, description="Specific heat capacity Cp in J/(kg·K)")
    density_kg_m3: float = Field(..., gt=0.0, description="Mass density rho in kg/m³")
    liquidus_temp_k: float = Field(..., gt=0.0, description="Liquidus temperature in Kelvin")
    solidus_temp_k: float = Field(..., gt=0.0, description="Solidus temperature in Kelvin")
    latent_heat_fusion_j_kg: float = Field(default=390000.0, ge=0.0, description="Latent heat of fusion in J/kg")
    thermal_expansion_coeff_1_k: Optional[float] = Field(default=None, description="Linear CTE alpha in 1/K")
    laser_absorptivity: float = Field(default=0.35, ge=0.0, le=1.0, description="Dimensionless optical absorptivity")


class PropertyTensor(BaseModel):
    """
    Unified property container holding mechanical, thermophysical, and uncertainty estimates.
    """
    mechanical: MechanicalProperties
    thermophysical: ThermophysicalProperties
    uncertainties: Dict[str, UncertaintyEstimate] = Field(default_factory=dict)
    cost_index_usd_kg: Optional[float] = Field(default=None, ge=0.0, description="Raw materials estimated cost per kg")
    temperature_evaluation_k: float = Field(default=293.15, gt=0.0, description="Evaluation temperature in Kelvin")
