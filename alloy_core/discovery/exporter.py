"""
Digital Recipe Compiler and Publication-Grade Discovery Report Exporter.
Exports machine-executable recipes (LPBF, SPS/HIP, OpenSCAD) and markdown audit reports with SHA-256 integrity.
"""

from __future__ import annotations
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from alloy_core.schemas.pspp import PSPPState
from alloy_core.schemas.manufacturing import ManufacturingRoute


class RecipeReportExporter:
    """Compiles and exports digital discovery packages."""

    @classmethod
    def export_digital_recipe(cls, state: PSPPState, output_path: str) -> str:
        """Exports machine-readable execution recipe in JSON format."""
        recipe_dict = {
            "recipe_id": state.recipe.recipe_id,
            "alloy_designation": state.designation,
            "composition": state.composition.model_dump(),
            "route": state.recipe.route.value,
            "parameters": state.recipe.model_dump(),
            "target_properties": state.properties.model_dump() if state.properties else {},
            "provenance_hash": state.evidence.provenance_hash,
            "export_timestamp": datetime.now(timezone.utc).isoformat()
        }

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(recipe_dict, f, indent=2)

        return output_path

    @classmethod
    def generate_markdown_report(
        cls,
        campaign_name: str,
        pareto_candidates: List[PSPPState],
        output_path: str
    ) -> str:
        """Generates comprehensive discovery markdown report."""
        lines = [
            f"# Discovery Campaign Report: {campaign_name}",
            f"**Generated UTC:** {datetime.now(timezone.utc).isoformat()}",
            f"**Top Pareto-Optimal Candidates:** {len(pareto_candidates)}",
            "",
            "## 🏆 Pareto-Optimal Alloy Candidates",
            "",
            "| Rank | Designation | Route | Yield (MPa) | UTS (MPa) | Elongation (%) | $K_{IC}$ (MPa·m⁰·⁵) | Provenance SHA-256 |",
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |"
        ]

        for rank, cand in enumerate(pareto_candidates, 1):
            mech = cand.properties.mechanical if cand.properties else None
            ys = f"{mech.yield_strength_mpa:.1f}" if mech else "N/A"
            uts = f"{mech.ultimate_tensile_strength_mpa:.1f}" if mech else "N/A"
            el = f"{mech.elongation_pct:.1f}%" if mech else "N/A"
            kic = f"{mech.fracture_toughness_kic_mpa_m05:.1f}" if (mech and mech.fracture_toughness_kic_mpa_m05) else "N/A"
            prov = cand.evidence.provenance_hash[:12] + "..."

            lines.append(f"| #{rank} | **{cand.designation}** | `{cand.recipe.route.value}` | {ys} | {uts} | {el} | {kic} | `{prov}` |")

        lines.extend([
            "",
            "## 🔬 Microstructural and Process Lineage",
            ""
        ])

        for rank, cand in enumerate(pareto_candidates, 1):
            lines.extend([
                f"### Candidate #{rank}: {cand.designation}",
                f"- **Composition (wt%)**: `{cand.composition.formula_string()}`",
                f"- **Route**: `{cand.recipe.route.value}`",
                f"- **Mean Grain Size**: `{cand.microstructure.grains.mean_grain_size_um if cand.microstructure else 'N/A'} μm`",
                f"- **Relative Density**: `{cand.microstructure.relative_density if cand.microstructure else 'N/A'}`",
                f"- **Cracking Susceptibility Index**: `{cand.microstructure.cracking_susceptibility_index if cand.microstructure else 'N/A'}`",
                f"- **Cryptographic Provenance Hash**: `{cand.evidence.provenance_hash}`",
                ""
            ])

        report_content = "\n".join(lines)
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(report_content)

        return output_path
