"""
Adapter bridging alloy-fluid simulation results with canonical alloy-core MeltPoolCFDResult contracts.
"""

from typing import Dict, Any, Optional

from alloy_core.schemas.fluid import (
    MeltPoolGeometry,
    MeltPoolThermalState,
    PoreDefectMap,
    MeltPoolCFDResult
)


class FluidAdapter:
    """Converts alloy-fluid CFD simulation outputs into canonical MeltPoolCFDResult schemas."""

    @staticmethod
    def to_cfd_result(
        length_um: float,
        width_um: float,
        depth_um: float,
        peak_temperature_k: float,
        max_cooling_rate_k_s: float,
        solidification_velocity_m_s: float,
        max_thermal_gradient_k_m: float = 1e6,
        marangoni_velocity_m_s: float = 0.5,
        recoil_pressure_pa: float = 1e4,
        regime: str = "conduction",
        keyhole_pore_risk: float = 0.05,
        lack_of_fusion_risk: float = 0.02,
        spatter_risk_index: float = 0.1,
        predicted_relative_density: float = 0.998
    ) -> MeltPoolCFDResult:
        geometry = MeltPoolGeometry(
            length_um=length_um,
            width_um=width_um,
            depth_um=depth_um,
            aspect_ratio_d_w=round(depth_um / max(width_um, 1.0), 3)
        )

        thermal = MeltPoolThermalState(
            peak_temperature_k=peak_temperature_k,
            max_cooling_rate_k_s=max_cooling_rate_k_s,
            max_thermal_gradient_k_m=max_thermal_gradient_k_m,
            solidification_velocity_m_s=solidification_velocity_m_s,
            marangoni_velocity_m_s=marangoni_velocity_m_s,
            recoil_pressure_pa=recoil_pressure_pa
        )

        defect = PoreDefectMap(
            regime=regime,
            keyhole_pore_risk=keyhole_pore_risk,
            lack_of_fusion_risk=lack_of_fusion_risk,
            spatter_risk_index=spatter_risk_index,
            predicted_relative_density=predicted_relative_density
        )

        return MeltPoolCFDResult(
            geometry=geometry,
            thermal_state=thermal,
            defect_map=defect,
            provenance_solver="alloy-fluid-cfd-v0.1.0"
        )
