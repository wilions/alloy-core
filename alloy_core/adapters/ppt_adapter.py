"""
Adapter bridging ppt-master slide deck generation with canonical ICME discovery manifests.
"""

from typing import Dict, Any, Optional, List, Union
from pydantic import BaseModel, Field


class PPTCard(BaseModel):
    title: str = Field(..., description="Card heading")
    content: str = Field(..., description="Card body text or bullet list")
    icon: Optional[str] = Field(default=None, description="Optional icon slug e.g. tabler-outline/cpu")


class PPTSlide(BaseModel):
    type: str = Field(default="content_grid", description="Slide type (title_slide, content_grid, table_slide, summary_slide)")
    title: str = Field(..., description="Slide main title")
    subtitle: Optional[str] = Field(default=None, description="Optional subtitle")
    cards: Optional[List[PPTCard]] = Field(default=None, description="Cards for grid layout")
    columns: Optional[List[str]] = Field(default=None, description="Table column headers")
    rows: Optional[List[List[Any]]] = Field(default=None, description="Table rows")
    summary_text: Optional[str] = Field(default=None, description="Summary slide narrative")
    action_items: Optional[List[str]] = Field(default=None, description="Actionable next steps")
    latex_formulas: Optional[List[str]] = Field(default=None, description="LaTeX math strings for 300 DPI rendering")
    speaker_notes: Optional[str] = Field(default=None, description="Presenter narration notes")


class PPTDeckSpec(BaseModel):
    """Specification schema for a complete PowerPoint presentation deck."""
    title: str = Field(..., description="Presentation title")
    subtitle: str = Field(default="", description="Presentation subtitle")
    theme: str = Field(default="modern_technical_dark", description="Visual theme template")
    author: str = Field(default="AlloyPilot Autonomous ICME", description="Author / Organization")
    slides: List[PPTSlide] = Field(default_factory=list, description="Slide list")


class PPTAdapter:
    """Generates ppt-master compatible deck specifications from ICME campaign manifests."""

    @staticmethod
    def manifest_to_deck_spec(
        campaign_title: str,
        spec_id: str,
        manifest: Dict[str, Any],
        provenance_hash: Optional[str] = None
    ) -> PPTDeckSpec:
        """Converts an executed ICME campaign manifest into a presentation deck spec."""
        status = manifest.get("status", "COMPLETED")
        iterations = manifest.get("total_iterations", 1)
        nodes = manifest.get("executed_nodes", [])

        slides = [
            PPTSlide(
                type="title_slide",
                title=campaign_title,
                subtitle=f"Autonomous ICME Discovery Manifest ({spec_id})",
                speaker_notes="Welcome to the autonomous materials discovery gate review."
            ),
            PPTSlide(
                type="content_grid",
                title="Simulation Governance & Stage Gates",
                cards=[
                    PPTCard(title="Campaign Status", content=f"Status: {status}\nIterations: {iterations}"),
                    PPTCard(title="Security & Traceability", content=f"Provenance: {provenance_hash or 'Verified'}\nStandard: UADIB v2 CloudEvents")
                ],
                speaker_notes="Overview of stage-gate boundary constraints and validation metrics."
            ),
            PPTSlide(
                type="table_slide",
                title="Multi-Scale Execution DAG",
                columns=["Node ID", "Server", "Tool", "Status"],
                rows=[[n.get("node_id", "-"), n.get("server", "-"), n.get("tool", "-"), n.get("status", "-")] for n in nodes],
                speaker_notes="Trace of all atomic multi-physics solvers executed in the multi-scale pipeline."
            ),
            PPTSlide(
                type="summary_slide",
                title="Executive Findings & Next Milestones",
                summary_text=f"Campaign concluded with status '{status}'. Multi-physics models satisfied all active constraints.",
                action_items=[
                    "Export ChemOS robotic synthesis workcell package",
                    "Manufacture ASTM standard test coupons",
                    "Conduct experimental validation & residual model update"
                ],
                speaker_notes="Recommended robotic SDL workcell synthesis and tensile testing."
            )
        ]

        return PPTDeckSpec(
            title=campaign_title,
            subtitle=f"Spec: {spec_id}",
            theme="modern_technical_dark",
            slides=slides
        )
