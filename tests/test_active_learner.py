import pytest
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.manufacturing import ManufacturingRoute
from alloy_core.discovery.active_learner import (
    DiscoveryCampaignConfig,
    DiscoveryTarget,
    MultiFidelityDiscoveryEngine
)


def test_active_learning_discovery_cycle():
    cfg = DiscoveryCampaignConfig(
        campaign_name="Test Scalmalloy Variant Search",
        base_element="Al",
        allowed_solutes=["Sc", "Zr", "Mg"],
        manufacturing_route=ManufacturingRoute.LPBF,
        targets=[
            DiscoveryTarget(
                target_name="High Yield Strength",
                target_property="yield_strength_mpa",
                objective_type="maximize",
                target_value=450.0,
                weight=2.0
            ),
            DiscoveryTarget(
                target_name="Good Ductility",
                target_property="elongation_pct",
                objective_type="maximize",
                target_value=12.0,
                weight=1.0
            )
        ],
        tier1_sample_count=100,
        tier2_batch_size=4
    )

    engine = MultiFidelityDiscoveryEngine(config=cfg)
    results = engine.run_discovery_cycle(cycle_index=1)

    assert len(results) == 4
    for r in results:
        assert r.status == "simulated"
        assert r.properties is not None
        assert r.properties.mechanical.yield_strength_mpa > 150.0
        assert r.elo_score >= 1000.0

    assert len(engine.pareto_front) > 0
    top_cand = engine.pareto_front[0]
    assert top_cand.composition.base_element == "Al"
