"""
Unified Cross-MCP Pipeline: LPBF Melt-Pool Fluid Dynamics -> Solidification Field ->
Diffusion Homogenization -> Part-Scale Macro Inherent Strain -> Durability Performance.
"""

from typing import Dict, Any, Optional
import math
from pydantic import BaseModel, Field

from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.manufacturing import LPBFParameters
from alloy_core.schemas.pspp import PSPPState
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier


class AMDurabilityResult(BaseModel):
    """Complete multi-scale result of the coupled AM Melt-Pool to Durability pipeline."""
    alloy_designation: str
    composition: Dict[str, float]
    process_parameters: Dict[str, Any]
    
    # 1. Fluid CFD
    melt_pool_dimensions_um: Dict[str, float]
    melt_pool_peak_temp_k: float
    marangoni_velocity_m_s: float
    recoil_pressure_pa: float
    cooling_rate_k_s: float
    defect_regime: str
    predicted_relative_density: float
    
    # 2. Field Solidification
    dendrite_arm_spacings_um: Dict[str, float]
    cet_solidification_regime: str
    mean_grain_size_um: float
    texture_intensity_index_j: float
    
    # 3. Diffusion Homogenization
    rate_limiting_solute: str
    recommended_soak_hours: float
    homogenization_soak_temp_k: float
    
    # 4. Macro Part-Scale Inherent Strain & Distortion
    anisotropic_inherent_strain: Dict[str, float]
    max_part_displacement_mm: float
    tip_z_warpage_mm: float
    recoater_interference_risk: bool
    peak_residual_stress_von_mises_mpa: float
    substrate_delamination_risk: float
    
    # 5. Performance Durability
    fatigue_limit_mpa: float
    cycles_to_failure_at_target_stress: float
    tanaka_mura_fip: float
    creep_time_to_rupture_hours: float
    oxide_scale_thickness_1000h_um: float
    safe_operational_envelope: bool
    limiting_failure_mode: str


class AMDurabilityPipeline:
    """Executes the coupled multi-physics AM pipeline across the 5 specialized engines."""

    @classmethod
    def run(
        cls,
        alloy_name: str,
        composition: Dict[str, float],
        base_element: str = "Ni",
        laser_power_w: float = 200.0,
        scan_speed_m_s: float = 1.0,
        hatch_spacing_um: float = 100.0,
        layer_thickness_um: float = 30.0,
        preheat_temp_k: float = 353.15,
        target_cyclic_stress_mpa: float = 350.0,
        service_temp_k: float = 973.15,
        cantilever_length_mm: float = 50.0
    ) -> AMDurabilityResult:
        # Import engine modules dynamically
        from alloy_fluid.core.cfd_solver import MeltPoolCFDSolver
        from alloy_field.core.kgt_kinetics import KGTDendriteKinetics
        from alloy_field.core.cet_solver import CETSolver
        from alloy_field.core.cellular_automata import CellularAutomataSolidificationSolver
        from alloy_field.core.texture import TextureAnalyzer
        from alloy_diffuse.core.homogenization import HomogenizationOptimizer
        from alloy_macro.core.inherent_strain import InherentStrainCalibrator
        from alloy_macro.core.fem_mesh import CantileverMeshBuilder
        from alloy_macro.core.distortion_solver import InherentStrainFEMSolver
        from alloy_perform.core.fatigue import FatigueEngine
        from alloy_perform.core.creep import CreepRuptureEngine
        from alloy_perform.core.oxidation import OxidationKineticsEngine
        from alloy_perform.core.service_envelope import ServiceEnvelopeEvaluator

        # 1. Fluid CFD
        cfd_solver = MeltPoolCFDSolver()
        cfd_res = cfd_solver.solve(
            laser_power_w=laser_power_w,
            scan_speed_m_s=scan_speed_m_s,
            hatch_spacing_um=hatch_spacing_um,
            layer_thickness_um=layer_thickness_um
        )

        # 2. Field Solidification & Texture
        g_val = float(cfd_res.peak_temperature_k / max(cfd_res.depth_um * 1e-6, 1e-6))
        r_val = float(scan_speed_m_s * 0.707)
        
        kgt = KGTDendriteKinetics()
        solute_pct = sum(v * 100.0 if v < 1.0 else v for k, v in composition.items() if k != base_element)
        dendrite_res = kgt.calculate_dendrite_spacings(
            thermal_gradient_k_m=g_val,
            solidification_velocity_m_s=r_val,
            solute_content_wt_pct=solute_pct
        )

        cet = CETSolver()
        cet_res = cet.predict_regime(g_val, r_val)

        ca = CellularAutomataSolidificationSolver(nx=40, ny=40, dx_um=1.0)
        ca_res = ca.simulate(thermal_gradient_k_m=g_val, cooling_rate_k_s=cfd_res.max_cooling_rate_k_s)
        j_index = TextureAnalyzer.calculate_texture_index(ca_res.euler_angles_deg)

        # 3. Diffusion Homogenization
        solutes = [k for k in composition.keys() if k != base_element] or ["Cr", "Al"]
        sdas = dendrite_res.secondary_arm_spacing_um
        diff_opt = HomogenizationOptimizer(solvent=base_element)
        homo_res = diff_opt.multi_element_soaking_window(
            elements=solutes,
            sdas_um=sdas,
            temperature_k=service_temp_k + 300.0,
            target_residual_index=0.05
        )
        max_soak_hours = max((r.time_to_target_homogeneity_hours for r in homo_res.values()), default=4.0)
        limiting_elem = max(homo_res.keys(), key=lambda k: homo_res[k].time_to_target_homogeneity_hours) if homo_res else solutes[0]

        # 4. Macro Part-Scale Inherent Strain & Residual Stress FEM
        # Estimate base mechanical properties
        e_gpa = 180.0 if base_element == "Ni" else (115.0 if base_element == "Ti" else 70.0)
        yield_nominal = 600.0 + 300.0 / math.sqrt(max(ca_res.mean_grain_size_um, 0.5))

        calibrator = InherentStrainCalibrator(youngs_modulus_gpa=e_gpa, yield_strength_mpa=yield_nominal)
        inh = calibrator.calibrate_from_process(laser_power_w=laser_power_w, scan_speed_m_s=scan_speed_m_s)

        mesh = CantileverMeshBuilder.build_cantilever_mesh(length_mm=cantilever_length_mm, height_mm=12.0)
        fem = InherentStrainFEMSolver(youngs_modulus_gpa=e_gpa, yield_strength_mpa=yield_nominal)
        fem_res = fem.solve_mesh_distortion(mesh, inh, is_substrate_released=True)

        # 5. Durability & Performance Life
        fatigue = FatigueEngine(
            yield_strength_mpa=yield_nominal,
            ultimate_tensile_strength_mpa=yield_nominal * 1.3,
            grain_size_um=ca_res.mean_grain_size_um
        )
        fat_res = fatigue.evaluate_life(stress_amplitude_mpa=target_cyclic_stress_mpa)

        creep = CreepRuptureEngine()
        creep_res = creep.evaluate_creep(temperature_k=service_temp_k, applied_stress_mpa=target_cyclic_stress_mpa * 0.7)

        ox_fam = "superalloy_chromia" if "Cr" in composition else ("titanium" if base_element == "Ti" else "steel")
        ox = OxidationKineticsEngine(base_alloy_family=ox_fam)
        ox_res = ox.evaluate_oxidation(temperature_k=service_temp_k, duration_hours=1000.0)

        envelope = ServiceEnvelopeEvaluator(yield_strength_mpa=yield_nominal, ultimate_tensile_strength_mpa=yield_nominal * 1.3)
        env_res = envelope.evaluate_service_condition(
            service_temperature_k=service_temp_k,
            cyclic_stress_amplitude_mpa=target_cyclic_stress_mpa,
            static_stress_mpa=fem_res.stress_summary.peak_von_mises_mpa * 0.4,
            service_life_target_hours=3000.0
        )

        return AMDurabilityResult(
            alloy_designation=alloy_name,
            composition=composition,
            process_parameters={
                "laser_power_w": laser_power_w,
                "scan_speed_m_s": scan_speed_m_s,
                "hatch_spacing_um": hatch_spacing_um,
                "layer_thickness_um": layer_thickness_um
            },
            melt_pool_dimensions_um={
                "length_um": cfd_res.length_um,
                "width_um": cfd_res.width_um,
                "depth_um": cfd_res.depth_um,
                "aspect_ratio_d_w": cfd_res.aspect_ratio_d_w
            },
            melt_pool_peak_temp_k=cfd_res.peak_temperature_k,
            marangoni_velocity_m_s=cfd_res.marangoni_velocity_m_s,
            recoil_pressure_pa=cfd_res.recoil_pressure_pa,
            cooling_rate_k_s=cfd_res.max_cooling_rate_k_s,
            defect_regime=cfd_res.defect_assessment.regime,
            predicted_relative_density=cfd_res.defect_assessment.predicted_relative_density,
            dendrite_arm_spacings_um={
                "primary_arm_spacing_lambda1_um": dendrite_res.primary_arm_spacing_um,
                "secondary_arm_spacing_lambda2_um": dendrite_res.secondary_arm_spacing_um
            },
            cet_solidification_regime=cet_res.regime.value,
            mean_grain_size_um=ca_res.mean_grain_size_um,
            texture_intensity_index_j=j_index,
            rate_limiting_solute=limiting_elem,
            recommended_soak_hours=round(max_soak_hours, 2),
            homogenization_soak_temp_k=service_temp_k + 300.0,
            anisotropic_inherent_strain={
                "eps_xx": inh.eps_xx,
                "eps_yy": inh.eps_yy,
                "eps_zz": inh.eps_zz,
                "volumetric": inh.volumetric_strain
            },
            max_part_displacement_mm=fem_res.max_displacement_mm,
            tip_z_warpage_mm=fem_res.tip_deflection_mm,
            recoater_interference_risk=fem_res.recoater_interference_risk,
            peak_residual_stress_von_mises_mpa=fem_res.stress_summary.peak_von_mises_mpa,
            substrate_delamination_risk=fem_res.stress_summary.delamination_risk,
            fatigue_limit_mpa=fat_res.fatigue_limit_mpa,
            cycles_to_failure_at_target_stress=fat_res.cycles_to_failure_nf,
            tanaka_mura_fip=fat_res.fip_value,
            creep_time_to_rupture_hours=creep_res.time_to_rupture_hours,
            oxide_scale_thickness_1000h_um=ox_res.oxide_scale_thickness_um,
            safe_operational_envelope=env_res.safe_operational_envelope,
            limiting_failure_mode=env_res.limiting_failure_mode
        )
