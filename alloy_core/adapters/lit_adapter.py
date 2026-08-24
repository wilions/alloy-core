"""
Adapter for converting alloy-lit OKF literature records into canonical EvidenceRecord.
"""

from typing import Dict, Any, Optional
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier


class LitAdapter:
    """Converts alloy-lit OKF literature metadata into canonical EvidenceRecord."""

    @staticmethod
    def to_evidence_record(lit_metadata: Dict[str, Any]) -> EvidenceRecord:
        """Converts OKF frontmatter metadata or JSON record to EvidenceRecord."""
        doi = lit_metadata.get("doi")
        zotero_key = lit_metadata.get("zotero_key", lit_metadata.get("key"))
        title = lit_metadata.get("title", "Literature Article")
        journal = lit_metadata.get("journal", "Journal")
        year = lit_metadata.get("year")

        return EvidenceRecord.generate(
            pillar=ProvenancePillar.ALLOY_LIT,
            tier=DataTier.LITERATURE,
            payload=lit_metadata,
            doi=doi,
            zotero_key=zotero_key,
            metadata={
                "title": title,
                "journal": journal,
                "year": year,
                "tags": lit_metadata.get("tags", [])
            }
        )
