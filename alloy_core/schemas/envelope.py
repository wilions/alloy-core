"""
Canonical UADIB Result Envelope & Provenance Contracts.
Standardizes response envelopes, Pint-style physical quantities with SI units,
and W3C PROV-O audit records across the Alloy ICME suite.
"""

from __future__ import annotations
import uuid
import hashlib
import json
from typing import Dict, List, Optional, Literal, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field, ConfigDict


class QuantityValue(BaseModel):
    """SI-traceable physical quantity with value and unit."""
    model_config = ConfigDict(frozen=True)
    value: float = Field(..., description="Numerical value")
    unit: str = Field(..., description="Canonical SI or standardized engineering unit (e.g. 'MPa', 'K', 'um', 'm/s')")


class ProvenanceNode(BaseModel):
    """W3C PROV-O compliant metadata tracking entity derivation and execution agent."""
    activity_id: str = Field(default_factory=lambda: f"ACT-{uuid.uuid4().hex[:8].upper()}")
    agent_name: str = Field(..., description="Worker MCP name or Pilot brain module")
    tool_name: str = Field(..., description="Invoked MCP tool or kernel function")
    started_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    ended_at: Optional[str] = None
    input_hashes: List[str] = Field(default_factory=list)
    code_version_git_sha: str = Field(default="v1.0.0")
    database_version_hash: Optional[str] = None


class ResultEnvelope(BaseModel):
    """Universal UADIB response envelope wrapping all domain worker MCP outputs."""
    campaign_id: str = Field(..., description="Discovery campaign identifier")
    candidate_id: str = Field(..., description="Candidate alloy PSPP identifier")
    tool_name: str = Field(..., description="Invoking tool name")
    fidelity_tier: Literal["T0", "T1", "T2", "T3"] = Field(default="T1")
    execution_status: Literal["SUCCESS", "FAILED", "EARLY_ABORTED"] = Field(default="SUCCESS")
    runtime_seconds: float = Field(default=0.0)
    
    # Typed physical outputs
    outputs: Dict[str, QuantityValue] = Field(default_factory=dict)
    uncertainty: Optional[Dict[str, float]] = Field(default=None, description="Standard deviations sigma")
    validity_flags: List[str] = Field(default_factory=list)
    
    # Zero-copy payload reference (e.g. Zarr / S3 / Arrow on disk)
    payload_array_ref: Optional[str] = Field(default=None, description="URI for large 2D/3D simulation fields")
    
    # Audit & Memoization
    provenance: Optional[ProvenanceNode] = None
    cache_key: Optional[str] = None

    def compute_cache_key(self, input_payload: Dict[str, Any], code_version: str = "v1.0.0") -> str:
        """Generates deterministic SHA-256 content-addressed cache key."""
        raw_inputs = json.dumps(input_payload, sort_keys=True, default=str)
        key_data = f"{self.tool_name}:{self.fidelity_tier}:{code_version}:{raw_inputs}"
        h = hashlib.sha256(key_data.encode("utf-8")).hexdigest()
        self.cache_key = f"uadib:{h}"
        return self.cache_key
