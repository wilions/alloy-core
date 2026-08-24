"""
Canonical Process-Structure-Property-Performance (PSPP) Candidate & Interchange Schemas.
Unifies all stages of discovery and simulation into a single immutable ledger.
"""

from __future__ import annotations
import hashlib
import json
import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.manufacturing import ProcessRecipe
from alloy_core.schemas.thermal import ThermalHistoryState
from alloy_core.schemas.microstructure import MicrostructureState
from alloy_core.schemas.properties import PropertyTensor
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier


class PSPPState(BaseModel):
    """
    Complete Process-Structure-Property-Performance (PSPP) digital state container.
    """
    candidate_id: str = Field(default_factory=lambda: f"CAN-{uuid.uuid4().hex[:8].upper()}")
    designation: str = Field(..., description="Alloy formula name or batch code")
    composition: MaterialComposition
    recipe: ProcessRecipe
    thermal_history: Optional[ThermalHistoryState] = None
    microstructure: Optional[MicrostructureState] = None
    properties: Optional[PropertyTensor] = None
    evidence: EvidenceRecord
    campaign_id: Optional[str] = Field(default=None, description="Campaign ID in alloy-pilot")
    elo_score: float = Field(default=1000.0, description="Tournament Elo score")
    confidence_score: float = Field(default=0.5, ge=0.0, le=1.0)
    status: str = Field(default="proposed", description="'proposed', 'simulated', 'validated', 'rejected'")
    tags: List[str] = Field(default_factory=list)

    def calculate_state_hash(self) -> str:
        """Compute holistic deterministic state checksum."""
        summary = {
            "id": self.candidate_id,
            "comp": self.composition.fractions,
            "recipe_id": self.recipe.recipe_id,
            "route": self.recipe.route.value,
            "micro": self.microstructure.model_dump() if self.microstructure else {},
            "props": self.properties.model_dump() if self.properties else {},
        }
        raw = json.dumps(summary, sort_keys=True, default=str)
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()
