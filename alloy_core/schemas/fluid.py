"""
Canonical Melt Pool & Fluid Dynamics Schemas for alloy-core.
Captures hydrodynamic flow, Marangoni convection, keyhole depression, and porosity defect maps.
"""

from __future__ import annotations
from typing import Optional, Dict
from pydantic import BaseModel, Field


class MeltPoolGeometry(BaseModel):
    """3D geometrical dimensions of the dynamic melt pool."""
    length_um: float = Field(..., gt=0.0, description="Melt pool total length in micrometers")
    width_um: float = Field(..., gt=0.0, description="Melt pool maximum width in micrometers")
    depth_um: float = Field(..., gt=0.0, description="Melt pool penetration depth in micrometers")
    tail_length_um: float = Field(default=0.0, ge=0.0, description="Length of trailing liquid tail")
    aspect_ratio_d_w: float = Field(..., gt=0.0, description="Depth-to-width ratio (d/w)")
    keyhole_depth_um: Optional[float] = Field(default=None, ge=0.0, description="Vapor cavity keyhole depth")


class MeltPoolThermalState(BaseModel):
    """Hydrodynamic and thermal state within the melt pool."""
    peak_temperature_k: float = Field(..., gt=0.0, description="Peak surface temperature in Kelvin")
    max_cooling_rate_k_s: float = Field(..., gt=0.0, description="Maximum cooling rate G*R in K/s")
    max_thermal_gradient_k_m: float = Field(..., gt=0.0, description="Maximum thermal gradient G in K/m")
    solidification_velocity_m_s: float = Field(..., ge=0.0, description="Solidification front velocity R in m/s")
    marangoni_velocity_m_s: float = Field(default=0.0, ge=0.0, description="Peak Marangoni thermocapillary flow speed in m/s")
    recoil_pressure_pa: float = Field(default=0.0, ge=0.0, description="Peak recoil vapor pressure in Pascals")


class PoreDefectMap(BaseModel):
    """Porosity, defect risk, and spatter quantification."""
    regime: str = Field(..., description="'conduction', 'transition', 'keyhole', or 'lack_of_fusion'")
    keyhole_pore_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="Keyhole pore formation probability [0, 1]")
    lack_of_fusion_risk: float = Field(default=0.0, ge=0.0, le=1.0, description="Lack-of-fusion defect risk [0, 1]")
    spatter_risk_index: float = Field(default=0.0, ge=0.0, le=1.0, description="Spatter / denudation severity index [0, 1]")
    predicted_relative_density: float = Field(default=0.995, ge=0.0, le=1.0, description="Estimated as-built relative density")


class MeltPoolCFDResult(BaseModel):
    """Complete container for high-fidelity fluid & melt-pool CFD simulations."""
    geometry: MeltPoolGeometry
    thermal_state: MeltPoolThermalState
    defect_map: PoreDefectMap
    provenance_solver: str = Field(default="alloy-fluid-lbm", description="Name/version of the fluid CFD solver")
    metadata: Dict[str, float] = Field(default_factory=dict)
