"""
Universal PSPP Event Bus and State Ledger for the Alloy Intelligence Suite.
Provides publish-subscribe and event-sourced ledger capabilities across discovery campaigns.
"""

from __future__ import annotations
import json
from typing import Dict, List, Callable, Optional, Any
from datetime import datetime, timezone
from alloy_core.schemas.pspp import PSPPState


class PSPPEventBus:
    """
    In-memory and file-backed event bus coordinating PSPP candidates and execution states.
    """

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path
        self._ledger: Dict[str, PSPPState] = {}
        self._subscribers: Dict[str, List[Callable[[PSPPState], None]]] = {
            "proposed": [],
            "simulated": [],
            "validated": [],
            "rejected": [],
            "all": []
        }

    def subscribe(self, status: str, callback: Callable[[PSPPState], None]) -> None:
        """Register a callback for candidate status events ('proposed', 'simulated', 'validated', 'all')."""
        if status not in self._subscribers:
            self._subscribers[status] = []
        self._subscribers[status].append(callback)

    def publish(self, state: PSPPState) -> str:
        """Publish or update a PSPP state in the ledger and notify subscribers."""
        self._ledger[state.candidate_id] = state

        # Notify specific status subscribers
        if state.status in self._subscribers:
            for cb in self._subscribers[state.status]:
                cb(state)

        # Notify wildcard subscribers
        for cb in self._subscribers["all"]:
            cb(state)

        if self.storage_path:
            self.persist()

        return state.candidate_id

    def get_candidate(self, candidate_id: str) -> Optional[PSPPState]:
        """Retrieve candidate state by ID."""
        return self._ledger.get(candidate_id)

    def list_candidates(self, status: Optional[str] = None) -> List[PSPPState]:
        """List candidates, optionally filtered by status."""
        if not status:
            return list(self._ledger.values())
        return [c for c in self._ledger.values() if c.status == status]

    def persist(self) -> None:
        """Save ledger snapshot to JSON file."""
        if not self.storage_path:
            return
        dump_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "count": len(self._ledger),
            "candidates": {k: v.model_dump(mode="json") for k, v in self._ledger.items()}
        }
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(dump_data, f, indent=2)
