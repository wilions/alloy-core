"""
Adapter bridging alloy-pilot (AlloyForge autonomous discovery) with canonical alloy-core schemas.
"""

from typing import Dict, Any, Optional
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.manufacturing import (
    ProcessRecipe,
    ManufacturingRoute,
    LPBFParameters,
    PMSinteringParameters
)
from alloy_core.schemas.microstructure import MicrostructureState, GrainMorphology
from alloy_core.schemas.properties import (
    PropertyTensor,
    MechanicalProperties,
    ThermophysicalProperties
)
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier
from alloy_core.schemas.pspp import PSPPState


class PilotAdapter:
    """Converts between alloy-pilot (AlloyForge) objects and canonical PSPPState."""

    @staticmethod
    def candidate_to_pspp_state(candidate_dict: Dict[str, Any]) -> PSPPState:
        """Converts an AlloyForge PSPPCandidate dictionary to a canonical PSPPState."""
        # 1. Composition
        raw_comp = candidate_dict.get("composition", {})
        if "elements" in raw_comp:
            comp = MaterialComposition(
                fractions=raw_comp["elements"],
                basis=raw_comp.get("basis", "weight"),
                base_element=raw_comp.get("base_element")
            )
        else:
            comp = MaterialComposition(fractions=raw_comp, basis="weight")

        # 2. Recipe
        raw_recipe = candidate_dict.get("recipe", {})
        route_str = raw_recipe.get("route", "lpbf")
        try:
            route = ManufacturingRoute(route_str)
        except ValueError:
            route = ManufacturingRoute.LPBF
        
        recipe = ProcessRecipe(
            recipe_id=raw_recipe.get("recipe_id", f"REC-{candidate_dict.get('candidate_id', 'DEFAULT')}"),
            route=route,
            notes=raw_recipe.get("notes", {})
        )

        # 3. Microstructure
        raw_micro = candidate_dict.get("microstructural_descriptors", {})
        micro = None
        if raw_micro:
            grain_size = raw_micro.get("grain_size_um", 10.0)
            micro = MicrostructureState(grains=GrainMorphology(mean_grain_size_um=grain_size))

        # 4. Properties
        raw_props = candidate_dict.get("predicted_properties") or candidate_dict.get("experimental_properties") or {}
        props = None
        if raw_props:
            mech_data = raw_props.get("mechanical", raw_props)
            thermo_data = raw_props.get("thermophysical", {})
            mech = MechanicalProperties(
                yield_strength_mpa=mech_data.get("yield_strength_mpa", 0.0),
                ultimate_tensile_strength_mpa=mech_data.get("ultimate_tensile_strength_mpa", 0.0),
                elongation_pct=mech_data.get("elongation_pct", 0.0),
                youngs_modulus_gpa=mech_data.get("youngs_modulus_gpa", 100.0)
            )
            thermo = ThermophysicalProperties(
                thermal_conductivity_w_m_k=thermo_data.get("thermal_conductivity_w_m_k", 20.0),
                specific_heat_j_kg_k=thermo_data.get("specific_heat_j_kg_k", 500.0),
                density_kg_m3=thermo_data.get("density_kg_m3", 4500.0),
                liquidus_temp_k=thermo_data.get("liquidus_temp_k", 1928.0),
                solidus_temp_k=thermo_data.get("solidus_temp_k", 1878.0)
            )
            props = PropertyTensor(mechanical=mech, thermophysical=thermo)

        # 5. Evidence
        ev = EvidenceRecord.generate(
            pillar=ProvenancePillar.ALLOY_PILOT,
            tier=DataTier.SURROGATE,
            payload=candidate_dict,
            metadata={"candidate_id": candidate_dict.get("candidate_id")}
        )

        return PSPPState(
            candidate_id=candidate_dict.get("candidate_id", "CAN-UNKNOWN"),
            designation=candidate_dict.get("name", comp.formula_string()),
            composition=comp,
            recipe=recipe,
            microstructure=micro,
            properties=props,
            evidence=ev,
            elo_score=candidate_dict.get("elo_score", 1000.0),
            confidence_score=candidate_dict.get("confidence_score", 0.5),
            status=candidate_dict.get("status", "proposed")
        )
