import pytest
from alloy_core.adapters.morph_adapter import MorphAdapter
from alloy_core.adapters.sinter_adapter import SinterAdapter
from alloy_core.adapters.pilot_adapter import PilotAdapter
from alloy_core.adapters.props_adapter import PropsAdapter
from alloy_core.adapters.lit_adapter import LitAdapter


def test_morph_adapter():
    comp_dict = {"base_element": "Al", "elements": {"Al": 0.965, "Sc": 0.007, "Zr": 0.003, "Mg": 0.025}}
    comp = MorphAdapter.to_canonical_composition(comp_dict)
    assert comp.base_element == "Al"
    assert comp.fractions["Sc"] == 0.007

    micro_dict = {
        "grain_size_um": 2.0,
        "relative_density": 0.997,
        "precipitates": {"Al3Sc": {"phase_name": "Al3Sc", "mean_radius_nm": 3.0, "volume_fraction": 0.01}}
    }
    micro = MorphAdapter.to_canonical_microstructure(micro_dict)
    assert micro.grains.mean_grain_size_um == 2.0
    assert "Al3Sc" in micro.precipitates


def test_sinter_adapter():
    sinter_dict = {"fractions": {"Mo": 0.99, "Ti": 0.008, "Zr": 0.002}, "basis": "atomic_fraction", "base_element": "Mo"}
    comp = SinterAdapter.to_canonical_composition(sinter_dict)
    assert comp.basis == "atomic"
    assert comp.base_element == "Mo"


def test_props_and_lit_adapters():
    matweb_data = {
        "material_name": "Ti-6Al-4V Grade 5",
        "matweb_id": "MAT-12345",
        "tensile_yield_strength_mpa": 880.0,
        "tensile_ultimate_strength_mpa": 950.0,
        "density_g_cc": 4.43,
        "thermal_conductivity_w_m_k": 6.7
    }
    props = PropsAdapter.to_canonical_property_tensor(matweb_data)
    assert props.mechanical.yield_strength_mpa == 880.0
    assert props.thermophysical.density_kg_m3 == 4430.0

    lit_data = {"title": "Additive Manufacturing of Ti-6Al-4V", "doi": "10.1016/j.matdes.2026.01.002"}
    ev = LitAdapter.to_evidence_record(lit_data)
    assert ev.doi == "10.1016/j.matdes.2026.01.002"


def test_pilot_adapter():
    cand_dict = {
        "candidate_id": "CAN-42",
        "name": "Mo-1.2Ti-0.12Zr-0.1C",
        "composition": {"Mo": 0.9858, "Ti": 0.012, "Zr": 0.0012, "C": 0.001},
        "recipe": {"route": "pm_sintering", "recipe_id": "REC-SINTER-01"},
        "elo_score": 1150.0
    }
    pspp = PilotAdapter.candidate_to_pspp_state(cand_dict)
    assert pspp.candidate_id == "CAN-42"
    assert pspp.elo_score == 1150.0
    assert pspp.recipe.route.value == "pm_sintering"


def test_zotero_and_ppt_adapters():
    from alloy_core.adapters.zotero_adapter import ZoteroAdapter
    from alloy_core.adapters.ppt_adapter import PPTAdapter

    raw_zot = {
        "key": "ZOT12345",
        "data": {
            "title": "Solidification Cracking in Additive Manufacturing of Al Alloys",
            "itemType": "journalArticle",
            "creators": [
                {"firstName": "John", "lastName": "Doe", "creatorType": "author"}
            ],
            "publicationTitle": "Acta Materialia",
            "date": "2025-04-12",
            "DOI": "10.1016/j.actamat.2025.101234",
            "tags": [{"tag": "Additive Manufacturing"}, {"tag": "Cracking"}]
        },
        "has_pdf": True
    }

    item = ZoteroAdapter.parse_item(raw_zot)
    assert item.key == "ZOT12345"
    assert item.title == "Solidification Cracking in Additive Manufacturing of Al Alloys"
    assert item.year == "2025"
    assert item.has_pdf is True
    assert len(item.creators) == 1
    assert item.creators[0].full_name == "John Doe"

    ev = ZoteroAdapter.to_evidence_record(item)
    assert ev.doi == "10.1016/j.actamat.2025.101234"
    assert ev.zotero_key == "ZOT12345"
    assert "Additive Manufacturing" in ev.metadata["tags"]

    manifest = {
        "status": "COMPLETED_OPTIMAL",
        "total_iterations": 2,
        "executed_nodes": [
            {"node_id": "NODE-01-CALPHAD", "server": "alloy-phase-mcp", "tool": "pycalphad_equilibrium", "status": "PASSED"},
            {"node_id": "NODE-02-PERFORM", "server": "alloy-perform-mcp", "tool": "perform_evaluate_creep_rupture", "status": "PASSED"}
        ]
    }
    deck = PPTAdapter.manifest_to_deck_spec(
        campaign_title="AlloyForge Discovery Deck",
        spec_id="SPEC-TEST-001",
        manifest=manifest,
        provenance_hash="sha256:abcdef"
    )
    assert deck.title == "AlloyForge Discovery Deck"
    assert len(deck.slides) == 4
    assert deck.slides[0].type == "title_slide"
    assert deck.slides[2].type == "table_slide"
    assert len(deck.slides[2].rows) == 2

