"""
Adapter for converting alloy-props / MatWeb records into canonical alloy-core representations.
"""

from typing import Dict, Any, Optional
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.properties import (
    PropertyTensor,
    MechanicalProperties,
    ThermophysicalProperties
)
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier


class PropsAdapter:
    """Converts alloy-props MatWeb profiles into canonical PropertyTensor and Composition."""

    @staticmethod
    def to_canonical_property_tensor(matweb_entry: Dict[str, Any]) -> PropertyTensor:
        """Converts raw or processed MatWeb dictionary to PropertyTensor."""
        mech_raw = matweb_entry.get("mechanical_properties", matweb_entry)
        thermo_raw = matweb_entry.get("thermal_properties", matweb_entry)

        mech = MechanicalProperties(
            yield_strength_mpa=float(mech_raw.get("tensile_yield_strength_mpa", mech_raw.get("yield_strength_mpa", 0.0))),
            ultimate_tensile_strength_mpa=float(mech_raw.get("tensile_ultimate_strength_mpa", mech_raw.get("ultimate_tensile_strength_mpa", 0.0))),
            elongation_pct=float(mech_raw.get("elongation_at_break_pct", mech_raw.get("elongation_pct", 0.0))),
            youngs_modulus_gpa=float(mech_raw.get("modulus_of_elasticity_gpa", mech_raw.get("youngs_modulus_gpa", 100.0))),
            poissons_ratio=float(mech_raw.get("poissons_ratio", 0.33)),
            hardness_hv=float(mech_raw.get("hardness_vickers", 0.0)) if mech_raw.get("hardness_vickers") else None
        )

        thermo = ThermophysicalProperties(
            thermal_conductivity_w_m_k=float(thermo_raw.get("thermal_conductivity_w_m_k", 20.0)),
            specific_heat_j_kg_k=float(thermo_raw.get("specific_heat_capacity_j_g_c", 0.5)) * 1000.0 if "specific_heat_capacity_j_g_c" in thermo_raw else float(thermo_raw.get("specific_heat_j_kg_k", 500.0)),
            density_kg_m3=float(thermo_raw.get("density_g_cc", 4.5)) * 1000.0 if "density_g_cc" in thermo_raw else float(thermo_raw.get("density_kg_m3", 4500.0)),
            liquidus_temp_k=float(thermo_raw.get("liquidus_temperature_c", 1650.0)) + 273.15 if "liquidus_temperature_c" in thermo_raw else float(thermo_raw.get("liquidus_temp_k", 1928.0)),
            solidus_temp_k=float(thermo_raw.get("solidus_temperature_c", 1600.0)) + 273.15 if "solidus_temperature_c" in thermo_raw else float(thermo_raw.get("solidus_temp_k", 1878.0))
        )

        return PropertyTensor(mechanical=mech, thermophysical=thermo)

    @staticmethod
    def to_evidence_record(matweb_entry: Dict[str, Any]) -> EvidenceRecord:
        matweb_id = matweb_entry.get("matweb_id", matweb_entry.get("material_id", "MATWEB-UNKNOWN"))
        return EvidenceRecord.generate(
            pillar=ProvenancePillar.ALLOY_PROPS,
            tier=DataTier.MATWEB,
            payload=matweb_entry,
            matweb_id=matweb_id,
            metadata={"name": matweb_entry.get("material_name", "MatWeb Material")}
        )
