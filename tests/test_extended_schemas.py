"""
Unit tests for the new Phase 0 physics & performance schemas (diffusion, fluid, macro, performance).
"""

import pytest
from alloy_core.schemas.composition import MaterialComposition
from alloy_core.schemas.manufacturing import ProcessRecipe, ManufacturingRoute, LPBFParameters
from alloy_core.schemas.evidence import EvidenceRecord, ProvenancePillar, DataTier
from alloy_core.schemas.pspp import PSPPState
from alloy_core.schemas.diffusion import (
    DiffusionCouple,
    DiffusionCoefficientTensor,
    DiffusionProfile,
    InterdiffusionFluxState
)
from alloy_core.schemas.fluid import (
    MeltPoolGeometry,
    MeltPoolThermalState,
    PoreDefectMap,
    MeltPoolCFDResult
)
from alloy_core.schemas.macro import (
    InherentStrainTensor,
    PartMeshState,
    ResidualStressState,
    MacroDistortionResult
)
from alloy_core.schemas.performance import (
    FatigueSNState,
    CreepRuptureState,
    OxidationKineticsState,
    PerformanceEnvelope
)


def test_diffusion_schemas():
    couple = DiffusionCouple(
        left_composition={"Ni": 0.8, "Cr": 0.2},
        right_composition={"Ni": 0.5, "Cr": 0.5},
        temperature_k=1373.15,
        time_s=36000.0,
        geometry="planar"
    )
    assert couple.temperature_k == 1373.15
    assert couple.geometry == "planar"

    tensor = DiffusionCoefficientTensor(
        solvent="Ni",
        solutes=["Cr", "Al"],
        temperature_k=1373.15,
        matrix_d=[[1e-14, 2e-15], [3e-16, 5e-15]],
        provenance_tdb="NIMOBS"
    )
    assert tensor.solvent == "Ni"
    assert len(tensor.matrix_d) == 2

    profile = DiffusionProfile(
        grid_x_um=[0.0, 10.0, 20.0, 30.0],
        time_s=3600.0,
        concentrations={"Cr": [0.2, 0.25, 0.35, 0.5]},
        homogenization_index=0.85
    )
    assert profile.homogenization_index == 0.85
    assert len(profile.concentrations["Cr"]) == 4


def test_fluid_cfd_schemas():
    geom = MeltPoolGeometry(
        length_um=220.0,
        width_um=110.0,
        depth_um=65.0,
        aspect_ratio_d_w=0.59,
        keyhole_depth_um=15.0
    )
    assert geom.aspect_ratio_d_w == 0.59

    thermal = MeltPoolThermalState(
        peak_temperature_k=2650.0,
        max_cooling_rate_k_s=1.2e6,
        max_thermal_gradient_k_m=4.5e6,
        solidification_velocity_m_s=0.8,
        marangoni_velocity_m_s=3.2,
        recoil_pressure_pa=125000.0
    )
    assert thermal.peak_temperature_k == 2650.0

    defect = PoreDefectMap(
        regime="transition",
        keyhole_pore_risk=0.05,
        lack_of_fusion_risk=0.01,
        spatter_risk_index=0.15,
        predicted_relative_density=0.998
    )
    assert defect.predicted_relative_density == 0.998

    cfd_res = MeltPoolCFDResult(
        geometry=geom,
        thermal_state=thermal,
        defect_map=defect
    )
    assert cfd_res.provenance_solver == "alloy-fluid-lbm"


def test_macro_schemas():
    strain = InherentStrainTensor(
        eps_xx=-0.0045,
        eps_yy=-0.0022,
        eps_zz=0.0010,
        gamma_xy=0.0
    )
    assert strain.eps_xx == -0.0045

    mesh = PartMeshState(
        node_count=12000,
        element_count=45000,
        bounding_box_x_mm=50.0,
        bounding_box_y_mm=50.0,
        bounding_box_z_mm=80.0
    )
    stress = ResidualStressState(
        peak_von_mises_mpa=480.0,
        peak_tensile_mpa=550.0,
        peak_compressive_mpa=-320.0
    )
    distortion = MacroDistortionResult(
        mesh_summary=mesh,
        max_displacement_mm=0.12,
        z_warpage_mm=0.09,
        residual_stress=stress
    )
    assert distortion.max_displacement_mm == 0.12
    assert distortion.residual_stress.peak_von_mises_mpa == 480.0


def test_performance_schemas():
    fatigue = FatigueSNState(
        fatigue_limit_mpa=450.0,
        r_ratio=-1.0,
        basquin_exponent_b=-0.085,
        fatigue_indicator_parameter_fip=0.002
    )
    creep = CreepRuptureState(
        test_temperature_k=1123.15,
        applied_stress_mpa=250.0,
        minimum_creep_rate_1_s=1.2e-8,
        time_to_rupture_hours=2400.0,
        larson_miller_parameter=26.2
    )
    oxidation = OxidationKineticsState(
        exposure_temperature_k=1273.15,
        duration_hours=500.0,
        parabolic_rate_constant_kp_mg2_cm4_s=1.5e-6,
        mass_gain_mg_cm2=0.55,
        oxide_scale_thickness_um=4.2
    )
    envelope = PerformanceEnvelope(
        fatigue=fatigue,
        creep=creep,
        oxidation=oxidation,
        max_service_temperature_k=1173.15
    )
    assert envelope.max_service_temperature_k == 1173.15
    assert envelope.fatigue.fatigue_limit_mpa == 450.0


def test_pspp_integration_with_extended_schemas():
    comp = MaterialComposition(fractions={"Ti": 0.9, "Al": 0.06, "V": 0.04}, basis="weight")
    recipe = ProcessRecipe(
        recipe_id="REC-TI64",
        route=ManufacturingRoute.LPBF,
        lpbf=LPBFParameters(laser_power_w=200.0, scan_velocity_m_s=1.0, hatch_spacing_um=100.0, layer_thickness_um=30.0)
    )
    evidence = EvidenceRecord.generate(pillar=ProvenancePillar.ALLOY_MORPH, tier=DataTier.SURROGATE, payload={})
    
    pspp = PSPPState(
        designation="Ti-6Al-4V",
        composition=comp,
        recipe=recipe,
        evidence=evidence,
        fluid_cfd=MeltPoolCFDResult(
            geometry=MeltPoolGeometry(length_um=200.0, width_um=100.0, depth_um=50.0, aspect_ratio_d_w=0.5),
            thermal_state=MeltPoolThermalState(peak_temperature_k=2400.0, max_cooling_rate_k_s=1e6, max_thermal_gradient_k_m=3e6, solidification_velocity_m_s=0.5),
            defect_map=PoreDefectMap(regime="conduction", predicted_relative_density=0.999)
        ),
        performance=PerformanceEnvelope(
            max_service_temperature_k=673.15
        )
    )

    assert pspp.fluid_cfd is not None
    assert pspp.fluid_cfd.geometry.aspect_ratio_d_w == 0.5
    assert pspp.performance.max_service_temperature_k == 673.15
    assert len(pspp.calculate_state_hash()) == 64
