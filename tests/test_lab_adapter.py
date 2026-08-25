"""
Unit tests for LabExecutionAdapter (SiLA 2 / OPC UA dispatch & characterization ingestion).
"""

import pytest
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.manufacturing import ProcessRecipe, ManufacturingRoute, PMSinteringParameters
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier
from alloy_core.schemas.pspp import PSPPState
from alloy_core.adapters.lab_adapter import (
    LabExecutionAdapter,
    LabProtocolType,
    LabExecutionCommand,
    LabObservationResult
)


@pytest.fixture
def sample_pspp():
    comp = MaterialComposition(fractions={"W": 0.85, "Mo": 0.10, "Ti": 0.05}, basis="weight")
    recipe = ProcessRecipe(
        recipe_id="REC-W-MO-TI",
        route=ManufacturingRoute.PM_SINTERING,
        pm_params=PMSinteringParameters(
            milling_time_hours=8.0,
            sintering_temp_k=1723.15,
            dwell_time_minutes=45.0,
            sintering_pressure_mpa=60.0
        )
    )
    evidence = EvidenceRecord.generate(pillar=ProvenancePillar.ALLOY_SINTER, tier=DataTier.SURROGATE, payload={})
    return PSPPState(
        designation="W-10Mo-5Ti",
        composition=comp,
        recipe=recipe,
        evidence=evidence
    )


def test_dispensing_command_generation(sample_pspp):
    cmd = LabExecutionAdapter.pspp_to_dispensing_command(sample_pspp)
    assert cmd.protocol == LabProtocolType.POWDER_DISPENSING
    assert cmd.candidate_id == sample_pspp.candidate_id
    assert cmd.parameters["dispense_targets_g"]["W"] == 85.0
    assert cmd.parameters["dispense_targets_g"]["Mo"] == 10.0
    assert cmd.parameters["dispense_targets_g"]["Ti"] == 5.0


def test_sintering_command_generation(sample_pspp):
    cmd = LabExecutionAdapter.pspp_to_sintering_command(sample_pspp)
    assert cmd.protocol == LabProtocolType.SPS_SINTERING
    assert cmd.parameters["target_temperature_k"] == 1723.15
    assert cmd.parameters["dwell_time_min"] == 45.0
    assert cmd.parameters["pressure_mpa"] == 60.0


def test_observation_ingestion(sample_pspp):
    obs = LabObservationResult(
        candidate_id=sample_pspp.candidate_id,
        protocol=LabProtocolType.TENSILE_TESTING,
        instrument_id="Instron-5982-CellA",
        measured_properties={
            "yield_strength_mpa": 1180.0,
            "ultimate_tensile_strength_mpa": 1340.0,
            "elongation_pct": 12.5,
            "vickers_hardness_hv": 410.0
        }
    )

    updated_state = LabExecutionAdapter.ingest_mechanical_observation(sample_pspp, obs)
    assert updated_state.status == "validated"
    assert updated_state.confidence_score == 0.99
    assert updated_state.properties.mechanical.yield_strength_mpa == 1180.0
    assert updated_state.properties.mechanical.hardness_hv == 410.0
    assert updated_state.evidence.data_tier == DataTier.EXPERIMENTAL
    assert updated_state.evidence.provenance_hash is not None
