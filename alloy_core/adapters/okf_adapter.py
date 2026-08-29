"""
Unified OKF Knowledge Client & Adapter.
Unifies literature extraction (alloy-lit) and property databases (alloy-props)
into a single authoritative Open Knowledge Framework interface.
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from alloy_core.schemas.properties import PropertyTensor
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier
from alloy_core.adapters.lit_adapter import LitAdapter
from alloy_core.adapters.props_adapter import PropsAdapter


class OKFQueryResult(BaseModel):
    """Consolidated OKF query response containing literature evidence and property tensors."""
    alloy_designation: str
    property_tensor: Optional[PropertyTensor] = None
    literature_citations: List[EvidenceRecord] = Field(default_factory=list)
    confidence_score: float = Field(default=0.85, ge=0.0, le=1.0)
    provenance_hash: Optional[str] = None


class UnifiedOKFAdapter:
    """Unified facade bridging literature and handbook properties."""

    @classmethod
    def compile_knowledge_profile(
        cls,
        alloy_name: str,
        matweb_entry: Optional[Dict[str, Any]] = None,
        literature_records: Optional[List[Dict[str, Any]]] = None
    ) -> OKFQueryResult:
        props = PropsAdapter.to_canonical_property_tensor(matweb_entry) if matweb_entry else None
        
        lit_evidence = []
        if literature_records:
            for rec in literature_records:
                lit_evidence.append(LitAdapter.to_evidence_record(rec))
        elif matweb_entry:
            lit_evidence.append(PropsAdapter.to_evidence_record(matweb_entry))

        # Confidence calculation based on evidence density
        confidence = 0.90 if (props and lit_evidence) else (0.75 if props or lit_evidence else 0.50)

        return OKFQueryResult(
            alloy_designation=alloy_name,
            property_tensor=props,
            literature_citations=lit_evidence,
            confidence_score=confidence
        )
