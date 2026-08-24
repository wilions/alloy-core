import pytest
import os
import tempfile
import json
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.manufacturing import ProcessRecipe, ManufacturingRoute
from alloy_core.digital_twin.runner import DigitalTwinRunner
from alloy_core.discovery.exporter import RecipeReportExporter


def test_recipe_and_report_export():
    comp = MaterialComposition(
        fractions={"Al": 0.965, "Sc": 0.007, "Zr": 0.003, "Mg": 0.025},
        basis="weight"
    )
    recipe = ProcessRecipe(
        recipe_id="REC-EXPORT-001",
        route=ManufacturingRoute.LPBF
    )
    state = DigitalTwinRunner.run_simulation(comp, recipe)

    with tempfile.TemporaryDirectory() as tmpdir:
        recipe_file = os.path.join(tmpdir, "recipe.json")
        report_file = os.path.join(tmpdir, "report.md")

        # Export recipe
        out_recipe = RecipeReportExporter.export_digital_recipe(state, recipe_file)
        assert os.path.exists(out_recipe)
        with open(out_recipe, "r") as f:
            data = json.load(f)
            assert data["recipe_id"] == "REC-EXPORT-001"
            assert data["route"] == "lpbf"
            assert "provenance_hash" in data

        # Export report
        out_report = RecipeReportExporter.generate_markdown_report(
            campaign_name="Test Campaign",
            pareto_candidates=[state],
            output_path=report_file
        )
        assert os.path.exists(out_report)
        with open(out_report, "r") as f:
            md_text = f.read()
            assert "# Discovery Campaign Report: Test Campaign" in md_text
            assert "Pareto-Optimal Alloy Candidates" in md_text
            assert state.evidence.provenance_hash[:12] in md_text
