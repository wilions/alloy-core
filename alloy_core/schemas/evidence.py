"""
Canonical Evidence, Provenance, and IP Governance Schemas for the Alloy Intelligence Suite.
Enforces SHA-256 cryptographic provenance, data tiering, and bibliographic tracing.
"""

from __future__ import annotations
import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class DataTier(str, Enum):
    EXPERIMENTAL = "experimental"      # Ground-truth laboratory measurement
    CALPHAD = "calphad"                # Rigorous thermodynamic CALPHAD calculation
    SURROGATE = "surrogate"            # ML / Gaussian Process surrogate prediction
    LITERATURE = "literature"          # Extracted from peer-reviewed paper (alloy-lit)
    MATWEB = "matweb"                  # Extracted from MatWeb database (alloy-props)
    HEURISTIC = "heuristic"            # Empirical rule of thumb / screening estimation


class ProvenancePillar(str, Enum):
    ALLOY_LIT = "alloy-lit"
    ALLOY_PROPS = "alloy-props"
    ALLOY_PHASE = "alloy-phase"
    ALLOY_SINTER = "alloy-sinter"
    ALLOY_MORPH = "alloy-morph"
    ALLOY_PILOT = "alloy-pilot"


class EvidenceRecord(BaseModel):
    """
    Cryptographic and bibliographic audit trail ensuring 100% provenance and IP compliance.
    """
    record_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:12])
    provenance_hash: str = Field(..., description="Deterministic SHA-256 checksum of payload and inputs")
    origin_pillar: ProvenancePillar
    data_tier: DataTier
    doi: Optional[str] = Field(default=None, description="Digital Object Identifier (DOI) for literature evidence")
    zotero_key: Optional[str] = Field(default=None, description="Zotero bibliographic key in alloy-lit")
    matweb_id: Optional[str] = Field(default=None, description="MatWeb record ID in alloy-props")
    timestamp_utc: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    model_or_solver_version: Optional[str] = Field(default=None, description="e.g. 'PyCalphad-0.10.3', 'DAMASK-3.0'")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def generate(
        cls,
        pillar: ProvenancePillar,
        tier: DataTier,
        payload: Any,
        doi: Optional[str] = None,
        zotero_key: Optional[str] = None,
        matweb_id: Optional[str] = None,
        solver_version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> "EvidenceRecord":
        """Generate an EvidenceRecord with an automated SHA-256 fingerprint."""
        raw_str = json.dumps(
            {
                "pillar": pillar.value,
                "tier": tier.value,
                "data": payload if isinstance(payload, (dict, list, str, int, float, bool)) else str(payload),
                "doi": doi,
                "matweb_id": matweb_id,
            },
            sort_keys=True,
            default=str
        )
        h = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()
        return cls(
            provenance_hash=h,
            origin_pillar=pillar,
            data_tier=tier,
            doi=doi,
            zotero_key=zotero_key,
            matweb_id=matweb_id,
            model_or_solver_version=solver_version,
            metadata=metadata or {}
        )
