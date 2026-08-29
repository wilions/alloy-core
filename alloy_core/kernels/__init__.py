"""
AlloyCore Fast Analytical Physics Kernels.
Zero-dependency, high-speed closed-form physics engines for in-process simulation.
"""

from alloy_core.kernels.thermal import (
    rosenthal_3d_point_source,
    eagar_tsai_surface_temperature,
    cooling_rate_and_gradient
)
from alloy_core.kernels.elasticity import (
    VRHModuliResult,
    vrh_cubic_homogenization
)
from alloy_core.kernels.fracture import (
    exponential_needleman_tsl,
    bilinear_tsl,
    evaluate_fracture_energy_and_kic
)
from alloy_core.kernels.strength import (
    StrengthBreakdownResult,
    calculate_yield_strength_superposition
)

__all__ = [
    "rosenthal_3d_point_source",
    "eagar_tsai_surface_temperature",
    "cooling_rate_and_gradient",
    "VRHModuliResult",
    "vrh_cubic_homogenization",
    "exponential_needleman_tsl",
    "bilinear_tsl",
    "evaluate_fracture_energy_and_kic",
    "StrengthBreakdownResult",
    "calculate_yield_strength_superposition"
]
