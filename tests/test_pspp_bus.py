import pytest
import os
import tempfile
from alloy_core.schemas.pspp import PSPPState
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.manufacturing import ProcessRecipe, ManufacturingRoute
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier
from alloy_core.bus.event_bus import PSPPEventBus


def test_pspp_state_and_event_bus():
    comp = MaterialComposition(fractions={"Ti": 0.90, "Al": 0.06, "V": 0.04}, basis="weight")
    recipe = ProcessRecipe(recipe_id="REC-001", route=ManufacturingRoute.LPBF)
    ev = EvidenceRecord.generate(
        pillar=ProvenancePillar.ALLOY_PILOT,
        tier=DataTier.CALPHAD,
        payload={"campaign": "CAM-01"}
    )

    state = PSPPState(
        candidate_id="CAN-001",
        designation="Ti-6Al-4V",
        composition=comp,
        recipe=recipe,
        evidence=ev,
        status="proposed"
    )

    h = state.calculate_state_hash()
    assert len(h) == 64

    # Test Event Bus
    with tempfile.TemporaryDirectory() as tmpdir:
        storage_file = os.path.join(tmpdir, "bus_ledger.json")
        bus = PSPPEventBus(storage_path=storage_file)

        received_events = []
        bus.subscribe("proposed", lambda s: received_events.append(s.candidate_id))

        bus.publish(state)
        assert len(received_events) == 1
        assert received_events[0] == "CAN-001"

        retrieved = bus.get_candidate("CAN-001")
        assert retrieved is not None
        assert retrieved.designation == "Ti-6Al-4V"
        assert os.path.exists(storage_file)
