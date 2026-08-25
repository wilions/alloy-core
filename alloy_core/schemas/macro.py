"""
Canonical Macro-Scale Thermomechanics & Distortion Schemas for alloy-core.
Covers inherent-strain tensors, layer-by-layer build distortion, and residual stress states.
"""

from __future__ import annotations
from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class InherentStrainTensor(BaseModel):
    """Anisotropic inherent strain tensor components epsilon* for fast macro FEM."""
    eps_xx: float = Field(..., description="Inherent strain in scan direction (X)")
    eps_yy: float = Field(..., description="Inherent strain transverse to scan direction (Y)")
    eps_zz: float = Field(..., description="Inherent strain in build direction (Z)")
    gamma_xy: float = Field(default=0.0, description="Shear inherent strain XY")
    gamma_yz: float = Field(default=0.0, description="Shear inherent strain YZ")
    gamma_zx: float = Field(default=0.0, description="Shear inherent strain ZX")
    effective_thermal_strain: Optional[float] = Field(default=None, description="Volumetric shrinkage thermal strain")


class PartMeshState(BaseModel):
    """Part-scale CAD/FE mesh topology summary."""
    node_count: int = Field(..., gt=0)
    element_count: int = Field(..., gt=0)
    bounding_box_x_mm: float = Field(..., gt=0.0)
    bounding_box_y_mm: float = Field(..., gt=0.0)
    bounding_box_z_mm: float = Field(..., gt=0.0)
    layer_thickness_um: float = Field(default=30.0, gt=0.0)


class ResidualStressState(BaseModel):
    """Residual stress field summary after build completion and cool-down."""
    peak_von_mises_mpa: float = Field(..., ge=0.0, description="Peak von Mises residual stress in MPa")
    peak_tensile_mpa: float = Field(..., description="Maximum principal tensile stress (crack risk) in MPa")
    peak_compressive_mpa: float = Field(..., description="Maximum principal compressive stress in MPa")
    surface_residual_stress_mpa: float = Field(default=0.0, description="As-built top surface residual stress")
    baseplate_interface_stress_mpa: float = Field(default=0.0, description="Residual stress at substrate interface")


class MacroDistortionResult(BaseModel):
    """Macro part deformation, warpage, and springback results."""
    mesh_summary: PartMeshState
    max_displacement_mm: float = Field(..., ge=0.0, description="Maximum total deflection/warpage in mm")
    z_warpage_mm: float = Field(..., description="Maximum vertical (Z) distortion in mm")
    residual_stress: ResidualStressState
    recoater_interference_risk: bool = Field(default=False, description="True if distortion exceeds recoater clearance")
    solver_name: str = Field(default="alloy-macro-fem", description="Name of macro FEM solver")
