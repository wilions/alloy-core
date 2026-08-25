"""
Adapter bridging alloy-macro FEM results with canonical alloy-core MacroDistortionResult contracts.
"""

from typing import Dict, Any, Optional

from alloy_core.schemas.macro import (
    InherentStrainTensor,
    PartMeshState,
    ResidualStressState,
    MacroDistortionResult
)


class MacroAdapter:
    """Converts alloy-macro FEM simulation summaries into canonical MacroDistortionResult schemas."""

    @staticmethod
    def to_inherent_strain_tensor(
        eps_xx: float,
        eps_yy: float,
        eps_zz: float,
        gamma_xy: float = 0.0,
        gamma_yz: float = 0.0,
        gamma_zx: float = 0.0,
        volumetric_strain: float = 0.0
    ) -> InherentStrainTensor:
        return InherentStrainTensor(
            eps_xx=eps_xx,
            eps_yy=eps_yy,
            eps_zz=eps_zz,
            gamma_xy=gamma_xy,
            gamma_yz=gamma_yz,
            gamma_zx=gamma_zx,
            effective_thermal_strain=volumetric_strain
        )

    @staticmethod
    def to_macro_result(
        node_count: int,
        element_count: int,
        max_displacement_mm: float,
        z_warpage_mm: float,
        peak_von_mises_mpa: float,
        peak_tensile_mpa: float,
        peak_compressive_mpa: float = 0.0,
        baseplate_interface_stress_mpa: float = 0.0,
        recoater_interference_risk: bool = False
    ) -> MacroDistortionResult:
        mesh_state = PartMeshState(
            node_count=node_count,
            element_count=element_count,
            bounding_box_x_mm=50.0,
            bounding_box_y_mm=10.0,
            bounding_box_z_mm=12.0
        )

        stress_state = ResidualStressState(
            peak_von_mises_mpa=peak_von_mises_mpa,
            peak_tensile_mpa=peak_tensile_mpa,
            peak_compressive_mpa=peak_compressive_mpa,
            baseplate_interface_stress_mpa=baseplate_interface_stress_mpa
        )

        return MacroDistortionResult(
            mesh_summary=mesh_state,
            max_displacement_mm=max_displacement_mm,
            z_warpage_mm=z_warpage_mm,
            residual_stress=stress_state,
            recoater_interference_risk=recoater_interference_risk,
            solver_name="alloy-macro-fem-v0.1.0"
        )
