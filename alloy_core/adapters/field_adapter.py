from typing import Dict, Any, List, Optional
import numpy as np

from alloy_core.schemas.microstructure import (
    MicrostructureState,
    GrainMorphology,
    PhaseConstituent,
    ComplexionState
)


class FieldAdapter:
    """Converts alloy-field numerical results into canonical alloy-core data contracts."""

    @staticmethod
    def ca_result_to_microstructure_state(
        num_grains: int = 50,
        mean_grain_size_um: float = 15.0,
        grain_aspect_ratio: float = 2.0,
        regime: str = "columnar",
        base_phase: str = "Matrix_Phase"
    ) -> MicrostructureState:
        morph_type = "columnar" if regime == "columnar" else ("equiaxed" if regime == "equiaxed" else "cellular")
        aspect = max(1.0, float(grain_aspect_ratio))
        if regime == "equiaxed":
            aspect = 1.1

        grains = GrainMorphology(
            mean_grain_size_um=float(mean_grain_size_um),
            aspect_ratio=aspect,
            morphology_type=morph_type,
            grain_size_d10_um=float(mean_grain_size_um * 0.6),
            grain_size_d90_um=float(mean_grain_size_um * 1.5)
        )

        phases = {
            base_phase: PhaseConstituent(
                phase_name=base_phase,
                fraction=1.0
            )
        }

        return MicrostructureState(
            grains=grains,
            phases=phases,
            solidified_fraction=1.0,
            relative_density=0.999
        )

