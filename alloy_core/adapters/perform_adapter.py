"""
Adapter bridging alloy-perform results with canonical alloy-core PerformanceEnvelope contracts.
"""

from typing import Dict, Any, Optional

from alloy_core.schemas.performance import (
    FatigueSNState,
    CreepRuptureState,
    OxidationKineticsState,
    PerformanceEnvelope
)


class PerformAdapter:
    """Converts alloy-perform simulation outcomes into canonical PerformanceEnvelope schemas."""

    @staticmethod
    def to_performance_envelope(
        fatigue_limit_mpa: float,
        r_ratio: float = -1.0,
        basquin_exponent_b: float = -0.10,
        fip_value: float = 1e-4,
        cycles_to_failure: float = 1e6,
        creep_temp_k: float = 973.15,
        applied_stress_mpa: float = 200.0,
        min_creep_rate_1_s: float = 1e-8,
        time_to_rupture_hours: float = 5000.0,
        larson_miller_parameter: float = 24.5,
        ox_temp_k: float = 973.15,
        ox_duration_hours: float = 1000.0,
        parabolic_rate_constant_kp: float = 1e-6,
        mass_gain_mg_cm2: float = 0.5,
        oxide_scale_thickness_um: float = 2.5,
        max_service_temperature_k: float = 1073.15
    ) -> PerformanceEnvelope:
        fatigue_state = FatigueSNState(
            fatigue_limit_mpa=fatigue_limit_mpa,
            r_ratio=r_ratio,
            basquin_exponent_b=basquin_exponent_b,
            fatigue_indicator_parameter_fip=fip_value,
            predicted_cycles_to_initiation=cycles_to_failure
        )

        creep_state = CreepRuptureState(
            test_temperature_k=creep_temp_k,
            applied_stress_mpa=applied_stress_mpa,
            minimum_creep_rate_1_s=min_creep_rate_1_s,
            time_to_rupture_hours=time_to_rupture_hours,
            monkman_grant_product=0.15,
            larson_miller_parameter=larson_miller_parameter
        )

        ox_state = OxidationKineticsState(
            exposure_temperature_k=ox_temp_k,
            duration_hours=ox_duration_hours,
            parabolic_rate_constant_kp_mg2_cm4_s=parabolic_rate_constant_kp,
            mass_gain_mg_cm2=mass_gain_mg_cm2,
            oxide_scale_thickness_um=oxide_scale_thickness_um,
            internal_oxidation_depth_um=0.0,
            spallation_risk=False
        )

        return PerformanceEnvelope(
            fatigue=fatigue_state,
            creep=creep_state,
            oxidation=ox_state,
            max_service_temperature_k=max_service_temperature_k,
            provenance_models={
                "fatigue_solver": "alloy-perform-fatigue-v0.1.0",
                "creep_solver": "alloy-perform-creep-v0.1.0",
                "oxidation_solver": "alloy-perform-oxidation-v0.1.0"
            }
        )
