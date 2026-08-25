"""
Adapter bridging alloy-diffuse simulation outputs into canonical alloy-core schemas.
"""

from typing import Dict, Any, List, Optional
import numpy as np

from alloy_core.schemas.diffusion import (
    DiffusionProfile,
    InterdiffusionFluxState,
    DiffusionCoefficientTensor,
    DiffusionCouple
)


class DiffuseAdapter:
    """Converts alloy-diffuse numerical outputs into canonical alloy-core data contracts."""

    @staticmethod
    def simulation_to_diffusion_profile(
        grid_x_um: List[float],
        time_points_s: List[float],
        concentrations: Dict[str, Any],
        time_index: int = -1,
        homogenization_index: float = 0.95
    ) -> DiffusionProfile:
        grid_x = [float(x) for x in grid_x_um]
        time_s = float(time_points_s[time_index]) if time_points_s else 0.0
        concs = {}
        for s, arr in concentrations.items():
            if isinstance(arr, np.ndarray):
                if arr.ndim > 1:
                    concs[s] = [float(c) for c in arr[time_index, :]]
                else:
                    concs[s] = [float(c) for c in arr]
            elif isinstance(arr, list):
                concs[s] = [float(c) for c in arr]
            else:
                concs[s] = [float(arr)]

        return DiffusionProfile(
            grid_x_um=grid_x,
            time_s=time_s,
            concentrations=concs,
            homogenization_index=homogenization_index
        )

    @staticmethod
    def mobility_to_diffusion_tensor(
        solvent: str,
        solutes: List[str],
        temperature_k: float,
        matrix_d: List[List[float]],
        provenance_tdb: str = "MOB_ALLOY_DICTRA"
    ) -> DiffusionCoefficientTensor:
        return DiffusionCoefficientTensor(
            solvent=solvent,
            solutes=solutes,
            temperature_k=temperature_k,
            matrix_d=[[float(val) for val in row] for row in matrix_d],
            provenance_tdb=provenance_tdb
        )
