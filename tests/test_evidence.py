import pytest
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier


def test_evidence_generation():
    payload = {"alloy": "Scalmalloy", "ys": 520.0}
    rec1 = EvidenceRecord.generate(
        pillar=ProvenancePillar.ALLOY_LIT,
        tier=DataTier.LITERATURE,
        payload=payload,
        doi="10.1016/j.actamat.2026.01.001"
    )
    rec2 = EvidenceRecord.generate(
        pillar=ProvenancePillar.ALLOY_LIT,
        tier=DataTier.LITERATURE,
        payload=payload,
        doi="10.1016/j.actamat.2026.01.001"
    )
    # Deterministic SHA-256 hash match
    assert rec1.provenance_hash == rec2.provenance_hash
    assert len(rec1.provenance_hash) == 64
    assert rec1.origin_pillar == ProvenancePillar.ALLOY_LIT
    assert rec1.data_tier == DataTier.LITERATURE
