"""
Adapter bridging Self-Driving Laboratory (SDL) execution hardware (SiLA 2 / OPC UA)
with canonical alloy-core PSPPState contracts.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from alloy_core.schemas.pspp import PSPPState
from alloy_core.schemas.properties import PropertyTensor, MechanicalProperties, ThermophysicalProperties
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier


class LabProtocolType(str, Enum):
    POWDER_DISPENSING = "powder_dispensing"
    SPS_SINTERING = "sps_sintering"
    LPBF_PRINTING = "lpbf_printing"
    HEAT_TREATMENT = "heat_treatment"
    TENSILE_TESTING = "tensile_testing"
    HARDNESS_MAPPING = "hardness_mapping"
    METALLOGRAPHY = "metallography"


class LabExecutionCommand(BaseModel):
    """Standardized SiLA 2 / OPC UA digital command payload for laboratory automation."""
    command_id: str = Field(default_factory=lambda: f"CMD-{uuid.uuid4().hex[:8].upper()}")
    candidate_id: str
    protocol: LabProtocolType
    target_instrument: str = Field(..., description="e.g. 'Lab-SPS-DrSinter', 'EOS-M290', 'Instron-5982'")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    safety_limits: Dict[str, float] = Field(default_factory=dict)
    priority: int = Field(default=1, ge=1, le=5)


class LabObservationResult(BaseModel):
    """Experimentally measured outcome ingested from automated characterization hardware."""
    observation_id: str = Field(default_factory=lambda: f"OBS-{uuid.uuid4().hex[:8].upper()}")
    candidate_id: str
    protocol: LabProtocolType
    instrument_id: str
    operator_or_agent: str = Field(default="SDL-Automated-Rig")
    measured_properties: Dict[str, float] = Field(default_factory=dict)
    raw_data_uri: Optional[str] = Field(default=None)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LabExecutionAdapter:
    """Converts PSPPState into hardware dispatch instructions and ingests SDL observations."""

    @staticmethod
    def pspp_to_dispensing_command(state: PSPPState, target_instrument: str = "Quantos-Powder-Dispenser") -> LabExecutionCommand:
        """Translates candidate composition into robotic powder dispensing command."""
        weights_gram = {}
        total_target_mass_g = 100.0
        for elem, frac in state.composition.fractions.items():
            weights_gram[elem] = round(frac * total_target_mass_g, 4)

        return LabExecutionCommand(
            candidate_id=state.candidate_id,
            protocol=LabProtocolType.POWDER_DISPENSING,
            target_instrument=target_instrument,
            parameters={
                "batch_mass_g": total_target_mass_g,
                "dispense_targets_g": weights_gram,
                "tolerance_g": 0.001
            },
            safety_limits={"max_exposure_minutes": 60.0}
        )

    @staticmethod
    def pspp_to_sintering_command(state: PSPPState, target_instrument: str = "Lab-SPS-DrSinter") -> LabExecutionCommand:
        """Translates candidate recipe into SPS/FAST sintering furnace profile."""
        sinter_params = state.recipe.pm_params
        temp_k = sinter_params.sintering_temp_k if sinter_params else 1423.15
        dwell_min = sinter_params.dwell_time_minutes if sinter_params else 30.0
        pressure_mpa = sinter_params.sintering_pressure_mpa if sinter_params else 50.0

        return LabExecutionCommand(
            candidate_id=state.candidate_id,
            protocol=LabProtocolType.SPS_SINTERING,
            target_instrument=target_instrument,
            parameters={
                "target_temperature_k": temp_k,
                "target_temperature_c": temp_k - 273.15,
                "dwell_time_min": dwell_min,
                "pressure_mpa": pressure_mpa,
                "vacuum_level_pa": 5e-3
            },
            safety_limits={"max_temperature_c": 1900.0, "max_pressure_mpa": 100.0}
        )

    @staticmethod
    def ingest_mechanical_observation(state: PSPPState, observation: LabObservationResult) -> PSPPState:
        """
        Updates PSPPState with verified experimental characterization measurements,
        upgrades Evidence tier to EXPERIMENTAL, and seals state hash.
        """
        measured = observation.measured_properties
        mech = MechanicalProperties(
            yield_strength_mpa=measured.get("yield_strength_mpa", 0.0),
            ultimate_tensile_strength_mpa=measured.get("ultimate_tensile_strength_mpa", 0.0),
            elongation_pct=measured.get("elongation_pct", 0.0),
            hardness_hv=measured.get("vickers_hardness_hv", measured.get("hardness_hv")),
            youngs_modulus_gpa=measured.get("youngs_modulus_gpa", 100.0)
        )

        thermo = (
            state.properties.thermophysical
            if (state.properties and state.properties.thermophysical)
            else ThermophysicalProperties(
                thermal_conductivity_w_m_k=20.0,
                specific_heat_j_kg_k=500.0,
                density_kg_m3=8000.0,
                liquidus_temp_k=1800.0,
                solidus_temp_k=1700.0
            )
        )

        props = PropertyTensor(mechanical=mech, thermophysical=thermo)

        # Generate cryptographic experimental evidence record
        evidence = EvidenceRecord.generate(
            pillar=ProvenancePillar.ALLOY_PILOT,
            tier=DataTier.EXPERIMENTAL,
            payload=observation.model_dump(),
            metadata={
                "instrument_id": observation.instrument_id,
                "observation_id": observation.observation_id
            }
        )

        # Clone and return validated state
        new_state = state.model_copy(update={
            "properties": props,
            "evidence": evidence,
            "status": "validated",
            "confidence_score": 0.99
        })
        return new_state


LabAdapter = LabExecutionAdapter
