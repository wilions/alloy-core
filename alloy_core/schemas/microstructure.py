"""
Canonical Microstructure State Schemas for the Alloy Intelligence Suite.
Bridges mesoscale kinetics (KWN, Zener pinning), solid-state complexions,
and crystal plasticity mechanics across all manufacturing routes.
"""

from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class PrecipitatePopulation(BaseModel):
    """Morphological and kinetic state of a dispersed second-phase precipitate population."""
    phase_name: str = Field(..., description="Precipitate phase (e.g. 'Al3Sc', 'gamma_prime', 'MC_carbide')")
    mean_radius_nm: float = Field(default=0.0, ge=0.0, description="Mean equivalent sphere radius in nanometers")
    volume_fraction: float = Field(default=0.0, ge=0.0, le=1.0, description="Volume fraction (0.0 to 1.0)")
    number_density_m3: float = Field(default=0.0, ge=0.0, description="Number density in particles per m³")
    nucleation_rate_m3_s: float = Field(default=0.0, ge=0.0, description="Instantaneous nucleation rate J in m⁻³·s⁻¹")
    aspect_ratio: float = Field(default=1.0, ge=1.0, description="Particle aspect ratio (needle/plate/sphere)")


class GrainMorphology(BaseModel):
    """Grain structure and crystallographic morphology descriptors."""
    mean_grain_size_um: float = Field(default=10.0, gt=0.0, description="Equivalent grain diameter in micrometers")
    grain_size_d10_um: Optional[float] = Field(default=None, gt=0.0)
    grain_size_d90_um: Optional[float] = Field(default=None, gt=0.0)
    aspect_ratio: float = Field(default=1.0, ge=1.0, description="Grain aspect ratio (columnar vs equiaxed)")
    morphology_type: str = Field(default="equiaxed", description="'equiaxed', 'columnar', 'bimodal', 'cellular'")
    recrystallized_fraction: float = Field(default=0.0, ge=0.0, le=1.0)


class ComplexionState(BaseModel):
    """Grain boundary segregation and complexion stabilization (specifically for refractory/PM alloys)."""
    solute_coverage_fraction: float = Field(default=0.0, ge=0.0, le=1.0, description="Grain boundary solute monolayer coverage x_gb")
    grain_boundary_energy_j_m2: float = Field(default=0.6, ge=0.0, description="Effective grain boundary energy gamma_gb in J/m²")
    complexion_transition_temp_k: Optional[float] = Field(default=None, description="Transition temperature to bilayer/interlayer complexion")
    segregating_species: List[str] = Field(default_factory=list, description="Primary segregating elements (e.g. ['Zr', 'Hf'])")


class PhaseConstituent(BaseModel):
    """Constituent matrix or primary phase."""
    phase_name: str = Field(..., description="Phase identifier (e.g. 'FCC_A1', 'BCC_A2', 'HCP_A3', 'Laves')")
    fraction: float = Field(..., ge=0.0, le=1.0, description="Phase fraction (mole or volume)")
    lattice_parameter_a_nm: Optional[float] = Field(default=None, gt=0.0)
    lattice_parameter_c_nm: Optional[float] = Field(default=None, gt=0.0)


class MicrostructureState(BaseModel):
    """
    Consolidated canonical mesoscale microstructure representation.
    Enables unified evaluation across AM melt pools, casting ingots, and sintered PM billets.
    """
    grains: GrainMorphology = Field(default_factory=GrainMorphology)
    phases: Dict[str, PhaseConstituent] = Field(default_factory=dict)
    precipitates: Dict[str, PrecipitatePopulation] = Field(default_factory=dict)
    complexion: Optional[ComplexionState] = None
    dislocation_density_m2: float = Field(default=1e14, ge=0.0, description="Total dislocation density in lines/m²")
    relative_density: float = Field(default=1.0, ge=0.0, le=1.0, description="Relative density (1.0 - porosity fraction)")
    solidified_fraction: float = Field(default=1.0, ge=0.0, le=1.0, description="Solid fraction f_s")
    cracking_susceptibility_index: float = Field(default=0.0, ge=0.0, description="|df_s/d(T^0.5)| solidification cracking index")
    oxide_inclusion_volume_fraction: float = Field(default=0.0, ge=0.0, le=1.0, description="Non-metallic inclusion fraction")

    def total_precipitate_volume_fraction(self) -> float:
        return sum(p.volume_fraction for p in self.precipitates.values())
