"""
Adapter bridging alloy-pbf additive build and HIP simulations with canonical alloy-core contracts.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class PbfBuildResult(BaseModel):
    """Canonical representation of PBF additive manufacturing build and HIP post-processing."""
    build_orientation_deg: float = Field(default=0.0, description="Part build inclination angle")
    support_volume_cm3: float = Field(default=0.0, description="Calculated sacrificial support volume")
    as_built_relative_density: float = Field(default=0.992, description="As-printed relative density")
    post_hip_relative_density: float = Field(default=0.9998, description="Relative density after HIP pore closure")
    recoater_interference_risk: bool = Field(default=False, description="Whether warpage risks collision with recoater blade")
    max_part_warpage_mm: float = Field(default=0.0, description="Maximum part-scale thermal warpage")
    solver_name: str = Field(default="alloy-pbf-voxel-v0.1.0", description="PBF simulation engine name")


class PbfAdapter:
    """Converts alloy-pbf simulation outputs into canonical schemas."""

    @staticmethod
    def to_pbf_result(
        support_vol_cm3: float = 0.0,
        as_built_density: float = 0.992,
        post_hip_density: float = 0.9998,
        recoater_risk: bool = False,
        max_warpage_mm: float = 0.0,
        solver_name: str = "alloy-pbf-voxel-v0.1.0"
    ) -> PbfBuildResult:
        return PbfBuildResult(
            support_volume_cm3=support_vol_cm3,
            as_built_relative_density=as_built_density,
            post_hip_relative_density=post_hip_density,
            recoater_interference_risk=recoater_risk,
            max_part_warpage_mm=max_warpage_mm,
            solver_name=solver_name
        )
