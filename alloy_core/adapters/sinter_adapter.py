"""
Adapter bridging alloy-sinter powder metallurgy ICME simulations with canonical alloy-core schemas.
"""

from typing import Dict, Any, Optional
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.microstructure import (
    MicrostructureState,
    GrainMorphology,
    ComplexionState
)
from alloy_core.schemas.properties import (
    PropertyTensor,
    MechanicalProperties,
    ThermophysicalProperties,
    UncertaintyEstimate,
    DistributionType
)
from alloy_core.schemas.manufacturing import ProcessRecipe, ManufacturingRoute, PMSinteringParameters
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier


class SinterAdapter:
    """Converts between alloy-sinter (PowderMetallurgy) datatypes and canonical alloy_core schemas."""

    @staticmethod
    def to_canonical_composition(sinter_comp_dict: Dict[str, Any]) -> MaterialComposition:
        """Converts ChemicalComposition from alloy-sinter to MaterialComposition."""
        fractions = sinter_comp_dict.get("fractions", {})
        basis = "atomic" if sinter_comp_dict.get("basis") == "atomic_fraction" else "weight"
        base = sinter_comp_dict.get("base_element", "Mo")
        return MaterialComposition(
            fractions=fractions,
            basis=basis,
            base_element=base
        )

    @staticmethod
    def to_canonical_microstructure(sinter_stage_envelope: Dict[str, Any]) -> MicrostructureState:
        """Converts Stage 04 Sintering output envelope to MicrostructureState."""
        payload = sinter_stage_envelope.get("payload", sinter_stage_envelope)
        
        grain_size_nm = payload.get("final_grain_size_nm", payload.get("grain_size_nm", 1000.0))
        grain_size_um = grain_size_nm * 1e-3
        rel_density = payload.get("final_relative_density", payload.get("relative_density", 0.99))
        
        complexion = None
        if "grain_boundary_coverage" in payload or "x_gb" in payload:
            x_gb = payload.get("grain_boundary_coverage", payload.get("x_gb", 0.0))
            gamma_gb = payload.get("gamma_gb_j_m2", 0.6)
            complexion = ComplexionState(
                solute_coverage_fraction=x_gb,
                grain_boundary_energy_j_m2=gamma_gb
            )

        return MicrostructureState(
            grains=GrainMorphology(mean_grain_size_um=grain_size_um),
            complexion=complexion,
            relative_density=rel_density
        )

    @staticmethod
    def to_canonical_uncertainties(uncertainties_dict: Dict[str, Any]) -> Dict[str, UncertaintyEstimate]:
        """Converts alloy-sinter UncertaintyEstimate objects to canonical UncertaintyEstimate."""
        result = {}
        for key, u_data in uncertainties_dict.items():
            if isinstance(u_data, dict):
                dist_str = u_data.get("distribution", "normal")
                dist_enum = DistributionType.NORMAL
                if dist_str == "uniform":
                    dist_enum = DistributionType.UNIFORM
                elif dist_str == "lognormal":
                    dist_enum = DistributionType.LOGNORMAL
                
                result[key] = UncertaintyEstimate(
                    mean=u_data.get("mean", 0.0),
                    std_dev=u_data.get("std_dev", 0.0),
                    distribution=dist_enum,
                    credible_interval_95=tuple(u_data.get("credible_interval_95", (0.0, 0.0))),
                    provenance=u_data.get("provenance", "alloy-sinter")
                )
        return result
