"""
Unified Digital Twin Execution Gateway for the Alloy Intelligence Suite.
Routes and executes multi-scale ICME simulation pipelines across Additive Manufacturing (alloy-morph)
and Solid-State Powder Metallurgy (alloy-sinter) routes, returning canonical PSPPState records.
"""

from __future__ import annotations
import math
from typing import Dict, Optional, Any, List
import numpy as np

from alloy_core.schemas.composition import MaterialComposition, ATOMIC_WEIGHTS
from alloy_core.schemas.manufacturing import (
    ProcessRecipe,
    ManufacturingRoute,
    LPBFParameters,
    PMSinteringParameters
)
from alloy_core.schemas.thermal import ThermalHistoryState
from alloy_core.schemas.microstructure import (
    MicrostructureState,
    GrainMorphology,
    PrecipitatePopulation,
    ComplexionState
)
from alloy_core.schemas.properties import (
    PropertyTensor,
    MechanicalProperties,
    ThermophysicalProperties
)
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier
from alloy_core.schemas.pspp import PSPPState

from alloy_core.physics.kwn import UnifiedKWNEngine
from alloy_core.physics.czm import UnifiedCZMEngine
from alloy_core.physics.solidification import UnifiedSolidificationEngine
from alloy_core.physics.elasticity import UnifiedElasticityEngine


class DigitalTwinRunner:
    """Polymorphic ICME digital twin simulation gateway."""

    @classmethod
    def run_simulation(
        cls,
        composition: MaterialComposition,
        recipe: ProcessRecipe,
        designation: Optional[str] = None
    ) -> PSPPState:
        """
        Executes end-to-end Process -> Structure -> Property simulation pipeline.
        """
        formula = designation or composition.formula_string()

        if recipe.route in [ManufacturingRoute.LPBF, ManufacturingRoute.DED, ManufacturingRoute.CASTING]:
            return cls._run_am_casting_twin(composition, recipe, formula)
        elif recipe.route == ManufacturingRoute.PM_SINTERING:
            return cls._run_pm_sintering_twin(composition, recipe, formula)
        else:
            return cls._run_am_casting_twin(composition, recipe, formula)

    @classmethod
    def _run_am_casting_twin(
        cls,
        composition: MaterialComposition,
        recipe: ProcessRecipe,
        formula: str
    ) -> PSPPState:
        """Simulates melt-based Additive Manufacturing / Casting process path."""
        lpbf_p = recipe.lpbf_params or LPBFParameters(
            laser_power_w=200.0,
            scan_velocity_m_s=1.0,
            hatch_spacing_um=100.0,
            layer_thickness_um=30.0
        )

        # 1. Base thermophysical properties estimation
        base_elem = composition.base_element or "Al"
        if base_elem == "Al":
            k_th, cp, rho = 130.0, 900.0, 2700.0
            T_liq, T_sol = 933.15, 873.15
        elif base_elem == "Ti":
            k_th, cp, rho = 7.0, 520.0, 4430.0
            T_liq, T_sol = 1933.15, 1878.15
        elif base_elem == "Ni":
            k_th, cp, rho = 15.0, 450.0, 8400.0
            T_liq, T_sol = 1628.15, 1573.15
        else:
            k_th, cp, rho = 50.0, 500.0, 7000.0
            T_liq, T_sol = 1800.0, 1700.0

        # 2. Scheil Solidification & Cracking index
        solid_curve = UnifiedSolidificationEngine.calculate_scheil_curve(
            liquidus_temp_k=T_liq,
            solidus_temp_k=T_sol,
            partition_coefficient_k0=0.25
        )

        # 3. 3D Rosenthal thermal history synthesis
        th = ThermalHistoryState(profile_id="melt_pool_center")
        peak_T = T_liq + 800.0 * (lpbf_p.volumetric_energy_density_j_mm3() / 60.0)**0.5
        cooling_rate = (2.0 * math.pi * k_th * (peak_T - lpbf_p.preheat_temp_k)**2) / (lpbf_p.laser_power_w * 0.35 + 1.0)
        cooling_rate = min(max(cooling_rate, 1e4), 1e7)

        times = np.linspace(0.0, 0.005, 50)
        temps = [peak_T * math.exp(-cooling_rate * t / peak_T) + lpbf_p.preheat_temp_k for t in times]
        for t, T in zip(times, temps):
            th.add_point(float(t), float(T), cooling_rate_k_s=-float(cooling_rate))

        # 4. Microstructure: Grain size Hall-Petch scaling & KWN precipitation
        # Grain size d ~ A / sqrt(cooling_rate)
        grain_size_um = max(100.0 / math.sqrt(cooling_rate * 1e-4), 0.5)

        # KWN precipitate kinetics
        precip_state = {}
        if "Sc" in composition.fractions or "Zr" in composition.fractions:
            p_pop = UnifiedKWNEngine.solve(
                phase_name="Al3Sc",
                composition=composition,
                thermal_history=th
            )
            precip_state["Al3Sc"] = p_pop

        rel_density = 0.998 if lpbf_p.volumetric_energy_density_j_mm3() > 40.0 else 0.96

        micro = MicrostructureState(
            grains=GrainMorphology(mean_grain_size_um=round(grain_size_um, 2), morphology_type="cellular"),
            precipitates=precip_state,
            relative_density=rel_density,
            solidified_fraction=1.0,
            cracking_susceptibility_index=solid_curve.cracking_susceptibility_index
        )

        # 5. Mechanical property synthesis: Multi-mechanism yield
        # sigma_y = sigma_0 + k_HP / sqrt(d) + delta_sigma_ss + delta_sigma_precip
        sigma_0 = 50.0 if base_elem == "Al" else 400.0
        k_hp = 68.0 if base_elem == "Al" else 400.0  # MPa * um^0.5
        hp_contrib = k_hp / math.sqrt(max(grain_size_um, 0.1))
        ss_contrib = sum(math.sqrt(frac) * 150.0 for elem, frac in composition.fractions.items() if elem != base_elem)
        p_contrib = 180.0 if "Al3Sc" in precip_state and precip_state["Al3Sc"].volume_fraction > 0 else 0.0
        
        yield_mpa = sigma_0 + hp_contrib + ss_contrib + p_contrib
        uts_mpa = yield_mpa * 1.25
        elongation_pct = max(18.0 - (yield_mpa / 100.0), 3.0)

        # Elastic and fracture properties
        czm_res = UnifiedCZMEngine.evaluate_fracture_toughness(
            youngs_modulus_gpa=72.0 if base_elem == "Al" else 115.0,
            yield_strength_mpa=yield_mpa,
            grain_size_um=grain_size_um,
            porosity_fraction=1.0 - rel_density
        )

        mech = MechanicalProperties(
            yield_strength_mpa=round(yield_mpa, 1),
            ultimate_tensile_strength_mpa=round(uts_mpa, 1),
            elongation_pct=round(elongation_pct, 1),
            youngs_modulus_gpa=72.0 if base_elem == "Al" else 115.0,
            fracture_toughness_kic_mpa_m05=czm_res.fracture_toughness_kic_mpa_m05,
            strengthening_breakdown_mpa={
                "lattice_friction": round(sigma_0, 1),
                "hall_petch": round(hp_contrib, 1),
                "solid_solution": round(ss_contrib, 1),
                "precipitation": round(p_contrib, 1)
            }
        )

        thermo = ThermophysicalProperties(
            thermal_conductivity_w_m_k=k_th,
            specific_heat_j_kg_k=cp,
            density_kg_m3=rho,
            liquidus_temp_k=T_liq,
            solidus_temp_k=T_sol
        )

        props = PropertyTensor(mechanical=mech, thermophysical=thermo)

        ev = EvidenceRecord.generate(
            pillar=ProvenancePillar.ALLOY_MORPH,
            tier=DataTier.CALPHAD,
            payload={"route": recipe.route.value, "micro": micro.model_dump(), "props": props.model_dump()}
        )

        return PSPPState(
            designation=formula,
            composition=composition,
            recipe=recipe,
            thermal_history=th,
            microstructure=micro,
            properties=props,
            evidence=ev,
            status="simulated"
        )

    @classmethod
    def _run_pm_sintering_twin(
        cls,
        composition: MaterialComposition,
        recipe: ProcessRecipe,
        formula: str
    ) -> PSPPState:
        """Simulates solid-state Powder Metallurgy milling, compaction, and sintering path."""
        pm_p = recipe.pm_params or PMSinteringParameters(
            sintering_temp_k=1673.15,
            dwell_time_minutes=15.0
        )

        base_elem = composition.base_element or "Mo"
        rho_theo = 10280.0 if base_elem == "Mo" else 19250.0  # W or Mo
        E_mod = 320.0 if base_elem == "Mo" else 410.0

        # Master Sintering Curve / SOVS densification trajectory
        # Sintering activation energy Q_sint ~ 380 kJ/mol
        theta_sint = (pm_p.sintering_temp_k / 2000.0) * (pm_p.dwell_time_minutes / 30.0)**0.3
        final_rel_density = float(np.clip(0.85 + 0.14 * (1.0 - math.exp(-2.5 * theta_sint)), 0.85, 0.999))

        # Grain growth with Zener solute boundary pinning
        solute_frac = sum(v for k, v in composition.fractions.items() if k != base_elem)
        pinning_factor = 1.0 / (1.0 + 50.0 * solute_frac)
        grain_size_um = max(0.5 + 4.0 * (pm_p.sintering_temp_k / 2200.0) * pinning_factor, 0.2)

        complexion = ComplexionState(
            solute_coverage_fraction=min(solute_frac * 8.0, 0.95),
            grain_boundary_energy_j_m2=0.45
        )

        micro = MicrostructureState(
            grains=GrainMorphology(mean_grain_size_um=round(grain_size_um, 2), morphology_type="equiaxed"),
            complexion=complexion,
            relative_density=round(final_rel_density, 4)
        )

        # Solid-solution and Hall-Petch strength
        sigma_0 = 500.0  # Refractory base
        hp_contrib = 650.0 / math.sqrt(max(grain_size_um, 0.1))
        ss_contrib = solute_frac * 1200.0
        yield_mpa = (sigma_0 + hp_contrib + ss_contrib) * (final_rel_density**2)
        uts_mpa = yield_mpa * 1.18
        elongation_pct = max(10.0 * final_rel_density - (yield_mpa / 250.0), 1.5)

        czm_res = UnifiedCZMEngine.evaluate_fracture_toughness(
            youngs_modulus_gpa=E_mod,
            yield_strength_mpa=yield_mpa,
            grain_size_um=grain_size_um,
            porosity_fraction=1.0 - final_rel_density
        )

        mech = MechanicalProperties(
            yield_strength_mpa=round(yield_mpa, 1),
            ultimate_tensile_strength_mpa=round(uts_mpa, 1),
            elongation_pct=round(elongation_pct, 1),
            youngs_modulus_gpa=E_mod,
            fracture_toughness_kic_mpa_m05=czm_res.fracture_toughness_kic_mpa_m05,
            strengthening_breakdown_mpa={
                "lattice_friction": round(sigma_0, 1),
                "hall_petch": round(hp_contrib, 1),
                "solid_solution": round(ss_contrib, 1)
            }
        )

        thermo = ThermophysicalProperties(
            thermal_conductivity_w_m_k=138.0 if base_elem == "Mo" else 170.0,
            specific_heat_j_kg_k=250.0,
            density_kg_m3=rho_theo * final_rel_density,
            liquidus_temp_k=2896.0 if base_elem == "Mo" else 3695.0,
            solidus_temp_k=2890.0 if base_elem == "Mo" else 3680.0
        )

        props = PropertyTensor(mechanical=mech, thermophysical=thermo)

        ev = EvidenceRecord.generate(
            pillar=ProvenancePillar.ALLOY_SINTER,
            tier=DataTier.CALPHAD,
            payload={"route": recipe.route.value, "micro": micro.model_dump(), "props": props.model_dump()}
        )

        return PSPPState(
            designation=formula,
            composition=composition,
            recipe=recipe,
            microstructure=micro,
            properties=props,
            evidence=ev,
            status="simulated"
        )
