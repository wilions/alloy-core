"""
Unified CLI for the Alloy Intelligence Suite.
"""

from __future__ import annotations
import argparse
import json
import sys
from typing import Dict, Any

from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.manufacturing import ProcessRecipe, ManufacturingRoute
from alloy_core.digital_twin.runner import DigitalTwinRunner
from alloy_core.discovery.active_learner import (
    DiscoveryCampaignConfig,
    DiscoveryTarget,
    MultiFidelityDiscoveryEngine
)
from alloy_core.discovery.exporter import RecipeReportExporter


def simulate_cmd(args: argparse.Namespace) -> None:
    try:
        fractions = json.loads(args.composition)
    except Exception as e:
        print(f"Error parsing composition JSON: {e}")
        sys.exit(1)

    comp = MaterialComposition(fractions=fractions, basis="weight")
    recipe = ProcessRecipe(
        recipe_id="CLI-RECIPE",
        route=ManufacturingRoute(args.route)
    )
    state = DigitalTwinRunner.run_simulation(comp, recipe)
    print(json.dumps(state.model_dump(mode="json"), indent=2))


def discover_cmd(args: argparse.Namespace) -> None:
    cfg = DiscoveryCampaignConfig(
        campaign_name=args.name,
        base_element=args.base,
        manufacturing_route=ManufacturingRoute(args.route),
        targets=[
            DiscoveryTarget(target_name="High Strength", target_property="yield_strength_mpa", target_value=500.0, weight=2.0),
            DiscoveryTarget(target_name="Ductility", target_property="elongation_pct", target_value=10.0, weight=1.0)
        ],
        tier1_sample_count=args.samples,
        tier2_batch_size=args.batch_size
    )

    engine = MultiFidelityDiscoveryEngine(config=cfg)
    print(f"=== Starting Discovery Campaign: {cfg.campaign_name} ===")
    results = engine.run_discovery_cycle(cycle_index=1)
    print(f"Evaluated {len(results)} high-fidelity digital twin candidates.")
    print("\n--- Top Pareto Candidates ---")
    for i, c in enumerate(engine.pareto_front, 1):
        ys = c.properties.mechanical.yield_strength_mpa if c.properties else 0.0
        el = c.properties.mechanical.elongation_pct if c.properties else 0.0
        print(f"#{i} {c.designation} | Yield: {ys:.1f} MPa | Elongation: {el:.1f}% | Elo: {c.elo_score:.1f}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Alloy Intelligence Suite CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # simulate subcommand
    sim_parser = subparsers.add_parser("simulate", help="Run ICME digital twin simulation")
    sim_parser.add_argument("--composition", "-c", required=True, help="JSON composition dict, e.g. '{\"Al\": 0.965, \"Sc\": 0.007, \"Zr\": 0.003, \"Mg\": 0.025}'")
    sim_parser.add_argument("--route", "-r", default="lpbf", choices=["lpbf", "pm_sintering", "casting"], help="Manufacturing route")
    sim_parser.set_defaults(func=simulate_cmd)

    # discover subcommand
    disc_parser = subparsers.add_parser("discover", help="Run multi-fidelity autonomous discovery campaign")
    disc_parser.add_argument("--name", "-n", default="Alloy Discovery Campaign", help="Campaign title")
    disc_parser.add_argument("--base", "-b", default="Al", help="Base element solvent (e.g. Al, Ti, Ni, Mo)")
    disc_parser.add_argument("--route", "-r", default="lpbf", choices=["lpbf", "pm_sintering", "casting"])
    disc_parser.add_argument("--samples", "-s", type=int, default=200, help="Tier 1 sample count")
    disc_parser.add_argument("--batch-size", type=int, default=5, help="Tier 2 physics batch size")
    disc_parser.set_defaults(func=discover_cmd)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
