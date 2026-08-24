"""
Adapter bridging alloy-morph ICME simulations with canonical alloy-core schemas.
"""

from typing import Dict, Any, Optional
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.microstructure import (
    MicrostructureState,
    PrecipitatePopulation,
    GrainMorphology
)
from alloy_core.schemas.thermal import ThermalHistoryState
from alloy_core.schemas.properties import (
    PropertyTensor,
    MechanicalProperties,
    ThermophysicalProperties
)
from alloy_core.schemas.manufacturing import ProcessRecipe, ManufacturingRoute, LPBFParameters
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier


class MorphAdapter:
    """Converts between alloy-morph datatypes and canonical alloy_core schemas."""

    @staticmethod
    def to_canonical_composition(morph_comp_dict: Dict[str, Any], base_elem: Optional[str] = None) -> MaterialComposition:
        """Converts alloy-morph composition format to canonical MaterialComposition."""
        if "elements" in morph_comp_dict:
            elements = morph_comp_dict["elements"]
            base = morph_comp_dict.get("base_element", base_elem)
        else:
            elements = morph_comp_dict
            base = base_elem
        return MaterialComposition(
            fractions=elements,
            basis="weight",
            base_element=base
        )

    @staticmethod
    def to_canonical_microstructure(morph_micro_dict: Dict[str, Any]) -> MicrostructureState:
        """Converts alloy-morph MicrostructureState dict/instance to canonical MicrostructureState."""
        grain_size_um = morph_micro_dict.get("grain_size_um", 10.0)
        rel_dens = morph_micro_dict.get("relative_density", 0.995)
        sol_frac = morph_micro_dict.get("solidified_fraction", 1.0)
        crack_idx = morph_micro_dict.get("cracking_susceptibility_index", 0.0)
        disloc = morph_micro_dict.get("dislocation_density_m2", 1e14)

        precips: Dict[str, PrecipitatePopulation] = {}
        raw_precips = morph_micro_dict.get("precipitates", {})
        for name, p_data in raw_precips.items():
            if isinstance(p_data, dict):
                precips[name] = PrecipitatePopulation(
                    phase_name=p_data.get("phase_name", name),
                    mean_radius_nm=p_data.get("mean_radius_nm", 0.0),
                    volume_fraction=p_data.get("volume_fraction", 0.0),
                    number_density_m3=p_data.get("number_density_m3", 0.0),
                    nucleation_rate_m3_s=p_data.get("nucleation_rate_m3_s", 0.0)
                )

        return MicrostructureState(
            grains=GrainMorphology(mean_grain_size_um=grain_size_um),
            precipitates=precips,
            relative_density=rel_dens,
            solidified_fraction=sol_frac,
            cracking_susceptibility_index=crack_idx,
            dislocation_density_m2=disloc
        )

    @staticmethod
    def to_canonical_properties(
        morph_mech_dict: Dict[str, Any],
        morph_thermo_dict: Optional[Dict[str, Any]] = None
    ) -> PropertyTensor:
        """Converts alloy-morph mechanical and thermophysical outputs to PropertyTensor."""
        mech = MechanicalProperties(
            yield_strength_mpa=morph_mech_dict.get("yield_strength_mpa", 0.0),
            ultimate_tensile_strength_mpa=morph_mech_dict.get("ultimate_tensile_strength_mpa", 0.0),
            elongation_pct=morph_mech_dict.get("elongation_pct", 0.0),
            youngs_modulus_gpa=morph_mech_dict.get("youngs_modulus_gpa", 100.0),
            poissons_ratio=morph_mech_dict.get("poissons_ratio", 0.33),
            hardness_hv=morph_mech_dict.get("hardness_hv"),
            strengthening_breakdown_mpa=morph_mech_dict.get("strengthening_contributions", {})
        )

        t_data = morph_thermo_dict or {}
        thermo = ThermophysicalProperties(
            thermal_conductivity_w_m_k=t_data.get("thermal_conductivity", 20.0),
            specific_heat_j_kg_k=t_data.get("specific_heat", 500.0),
            density_kg_m3=t_data.get("density", 4500.0),
            liquidus_temp_k=t_data.get("liquidus_temperature", 1928.0),
            solidus_temp_k=t_data.get("solidus_temperature", 1878.0),
            latent_heat_fusion_j_kg=t_data.get("latent_heat_fusion", 390000.0),
            laser_absorptivity=t_data.get("laser_absorptivity", 0.35)
        )

        return PropertyTensor(mechanical=mech, thermophysical=thermo)
