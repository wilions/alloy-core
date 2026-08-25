"""
Canonical Multicomponent Diffusion & Kinetic Transport Schemas for alloy-core.
Covers DICTRA-class mobility, interdiffusion profiles, and flux states.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DiffusionCouple(BaseModel):
    """Configuration of a diffusion couple or boundary conditions."""
    left_composition: Dict[str, float] = Field(..., description="Left-end elemental mole/mass fractions")
    right_composition: Dict[str, float] = Field(..., description="Right-end elemental mole/mass fractions")
    temperature_k: float = Field(..., gt=0.0, description="Isothermal temperature in Kelvin")
    time_s: float = Field(..., gt=0.0, description="Diffusion annealing duration in seconds")
    geometry: str = Field(default="planar", description="'planar', 'cylindrical', or 'spherical'")


class DiffusionCoefficientTensor(BaseModel):
    """Multicomponent interdiffusion coefficient matrix D_tilde_{ij} at specified T and composition."""
    solvent: str = Field(..., description="Dependent solvent element")
    solutes: List[str] = Field(..., description="Independent solute element list")
    temperature_k: float = Field(..., gt=0.0)
    matrix_d: List[List[float]] = Field(..., description="Matrix of interdiffusion coefficients in m^2/s")
    provenance_tdb: Optional[str] = Field(default=None, description="Source mobility/thermodynamic database name")


class DiffusionProfile(BaseModel):
    """1D/Spatial composition profiles resulting from multicomponent diffusion solver."""
    grid_x_um: List[float] = Field(..., description="Spatial grid points in micrometers")
    time_s: float = Field(..., gt=0.0, description="Elapsed diffusion time in seconds")
    concentrations: Dict[str, List[float]] = Field(..., description="Element -> concentration array across grid_x_um")
    phase_boundary_positions_um: Dict[str, float] = Field(
        default_factory=dict,
        description="Phase name -> boundary position x in micrometers"
    )
    homogenization_index: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Index of chemical homogeneity (0 = segregated, 1 = uniform)"
    )


class InterdiffusionFluxState(BaseModel):
    """Interdiffusion flux distribution J_i across spatial coordinates."""
    grid_x_um: List[float] = Field(..., description="Spatial grid points in micrometers")
    fluxes_mol_m2_s: Dict[str, List[float]] = Field(..., description="Element -> flux array across grid_x_um")
    kirkendall_velocity_m_s: Optional[List[float]] = Field(
        default=None,
        description="Kirkendall marker shift velocity profile across coordinates"
    )
