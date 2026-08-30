"""
Adapter bridging zotero-mcp bibliographic records and collection hierarchies with canonical EvidenceRecord.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier


class ZoteroCreator(BaseModel):
    first_name: Optional[str] = Field(default=None, description="Creator given name")
    last_name: Optional[str] = Field(default=None, description="Creator surname")
    creator_type: str = Field(default="author", description="Role: author, editor, translator")

    @property
    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.last_name or self.first_name or "Unknown"


class ZoteroItem(BaseModel):
    """Canonical representation of a Zotero library reference item."""
    key: str = Field(..., description="Zotero 8-character unique alphanumeric key")
    item_type: str = Field(default="journalArticle", description="Item type (journalArticle, book, report)")
    title: str = Field(..., description="Publication title")
    creators: List[ZoteroCreator] = Field(default_factory=list, description="Author / creator list")
    publication_title: Optional[str] = Field(default=None, description="Journal / conference name")
    year: Optional[str] = Field(default=None, description="Publication year")
    date: Optional[str] = Field(default=None, description="Full date string")
    doi: Optional[str] = Field(default=None, description="Digital Object Identifier")
    url: Optional[str] = Field(default=None, description="Publication URL")
    abstract_note: Optional[str] = Field(default=None, description="Paper abstract")
    tags: List[str] = Field(default_factory=list, description="Associated subject tags")
    collections: List[str] = Field(default_factory=list, description="Collection keys where item is filed")
    has_pdf: bool = Field(default=False, description="Whether attached full-text PDF is present")


class ZoteroCollection(BaseModel):
    """Representation of a Zotero collection folder."""
    key: str = Field(..., description="Collection key")
    name: str = Field(..., description="Collection display name")
    parent_key: Optional[str] = Field(default=None, description="Parent collection key if nested")


class ZoteroAdapter:
    """Converts zotero-mcp API payloads into canonical ZoteroItem and EvidenceRecord structures."""

    @staticmethod
    def parse_item(raw: Dict[str, Any]) -> ZoteroItem:
        """Parses a raw Zotero JSON item dictionary into typed ZoteroItem."""
        data = raw.get("data", raw)
        creators_raw = data.get("creators", [])
        creators = [
            ZoteroCreator(
                first_name=c.get("firstName"),
                last_name=c.get("lastName") or c.get("name"),
                creator_type=c.get("creatorType", "author")
            )
            for c in creators_raw
        ]
        
        tags_raw = data.get("tags", [])
        tags = [t["tag"] if isinstance(t, dict) else str(t) for t in tags_raw]
        
        date_str = data.get("date", "")
        year = date_str[:4] if date_str and len(date_str) >= 4 and date_str[:4].isdigit() else None

        return ZoteroItem(
            key=data.get("key", raw.get("key", "")),
            item_type=data.get("itemType", "journalArticle"),
            title=data.get("title", "Untitled Document"),
            creators=creators,
            publication_title=data.get("publicationTitle"),
            year=year,
            date=date_str,
            doi=data.get("DOI"),
            url=data.get("url"),
            abstract_note=data.get("abstractNote"),
            tags=tags,
            collections=data.get("collections", []),
            has_pdf=bool(raw.get("has_pdf", raw.get("present", False)))
        )

    @staticmethod
    def to_evidence_record(item: ZoteroItem) -> EvidenceRecord:
        """Converts a ZoteroItem into an immutable EvidenceRecord."""
        author_names = [c.full_name for c in item.creators]
        return EvidenceRecord.generate(
            pillar=ProvenancePillar.ALLOY_LIT,
            tier=DataTier.LITERATURE,
            payload=item.model_dump(),
            doi=item.doi,
            zotero_key=item.key,
            metadata={
                "title": item.title,
                "authors": author_names,
                "journal": item.publication_title,
                "year": item.year,
                "tags": item.tags,
                "has_pdf": item.has_pdf
            }
        )
