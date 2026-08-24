"""
Canonical Manufacturing and Processing Route Schemas for the Alloy Intelligence Suite.
Enforces typed parameterizations across Additive Manufacturing, Solid-State Powder Metallurgy,
Casting, and Post-Processing Heat Treatments.
"""

from __future__ import annotations
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field, model_validator


class ManufacturingRoute(str, Enum):
    LPBF = "lpbf"
    DED = "ded"
    PM_SINTERING = "pm_sintering"
    CASTING = "casting"
    WROUGHT = "wrought"
    PVD = "pvd"
    HEAT_TREATMENT = "heat_treatment"


class LPBFParameters(BaseModel):
    """Laser Powder Bed Fusion process parameters."""
    laser_power_w: float = Field(..., gt=0.0, description="Laser beam power in Watts")
    scan_velocity_m_s: float = Field(..., gt=0.0, description="Scan speed in meters/second")
    hatch_spacing_um: float = Field(..., gt=0.0, description="Hatch spacing between tracks in micrometers")
    layer_thickness_um: float = Field(..., gt=0.0, description="Powder layer thickness in micrometers")
    beam_diameter_um: float = Field(default=80.0, gt=0.0, description="Laser spot diameter 1/e^2 in micrometers")
    preheat_temp_k: float = Field(default=353.15, description="Build plate preheat temperature in Kelvin (default 80°C)")
    atmosphere: str = Field(default="Ar", description="Chamber shielding atmosphere ('Ar', 'N2', 'He')")
    oxygen_content_ppm: float = Field(default=50.0, description="Residual chamber oxygen in ppm")

    def volumetric_energy_density_j_mm3(self) -> float:
        """Calculate Volumetric Energy Density (VED) = P / (v * h * t) in J/mm³."""
        v_mm_s = self.scan_velocity_m_s * 1e3
        h_mm = self.hatch_spacing_um * 1e-3
        t_mm = self.layer_thickness_um * 1e-3
        return self.laser_power_w / (v_mm_s * h_mm * t_mm)


class DEDParameters(BaseModel):
    """Directed Energy Deposition process parameters."""
    laser_power_w: float = Field(..., gt=0.0, description="Laser power in Watts")
    travel_velocity_mm_s: float = Field(..., gt=0.0, description="Cladding travel speed in mm/s")
    powder_feed_rate_g_min: float = Field(..., gt=0.0, description="Powder mass flow rate in g/min")
    spot_diameter_mm: float = Field(default=2.0, gt=0.0, description="Laser beam diameter in mm")
    shielding_gas_flow_l_min: float = Field(default=15.0, description="Shielding gas flow rate in L/min")


class PMSinteringParameters(BaseModel):
    """Solid-State Powder Metallurgy (Milling + Compaction + Sintering) parameters."""
    milling_time_hours: float = Field(default=10.0, ge=0.0, description="High-energy ball milling duration in hours")
    ball_to_powder_ratio: float = Field(default=10.0, gt=0.0, description="BPR mass ratio (e.g. 10:1)")
    milling_speed_rpm: float = Field(default=400.0, gt=0.0, description="Planetary mill rotation speed in RPM")
    compaction_pressure_mpa: float = Field(default=600.0, ge=0.0, description="Cold / Die compaction pressure in MPa")
    sintering_mode: str = Field(default="SPS", description="Sintering modality: 'SPS', 'HIP', 'Vacuum', 'Hydrogen'")
    sintering_temp_k: float = Field(..., gt=300.0, description="Peak sintering temperature in Kelvin")
    sintering_pressure_mpa: float = Field(default=50.0, ge=0.0, description="Applied pressure during sintering in MPa (for SPS/HIP)")
    dwell_time_minutes: float = Field(..., gt=0.0, description="Dwell time at peak sintering temperature in minutes")
    heating_rate_k_min: float = Field(default=100.0, gt=0.0, description="Ramp heating rate in K/min")


class CastingParameters(BaseModel):
    """Vacuum Induction Melting / Die Casting process parameters."""
    pouring_temp_k: float = Field(..., gt=300.0, description="Melt pouring temperature in Kelvin")
    mold_temp_k: float = Field(default=298.15, description="Mold preheat temperature in Kelvin")
    mold_material: str = Field(default="graphite", description="Mold material ('copper', 'graphite', 'ceramic')")
    cooling_mode: str = Field(default="water_cooled", description="Cooling modality ('air', 'water_cooled', 'furnace')")


class ThermalCycleStage(BaseModel):
    """Single stage of a thermal post-processing cycle."""
    stage_name: str = Field(..., description="E.g. 'Solution_Treatment', 'Quench', 'Aging_1', 'Stress_Relief'")
    start_temp_k: float = Field(..., gt=0.0)
    target_temp_k: float = Field(..., gt=0.0)
    ramp_rate_k_s: float = Field(default=1.0, gt=0.0, description="Heating/cooling rate in K/s")
    dwell_time_seconds: float = Field(default=0.0, ge=0.0, description="Hold duration in seconds")
    atmosphere: str = Field(default="Argon", description="'Vacuum', 'Argon', 'Air', 'Water_Quench'")


class HeatTreatmentSchedule(BaseModel):
    """Multi-stage heat treatment schedule."""
    schedule_name: str = Field(default="standard_aging", description="Heat treatment designation (e.g. 'T6', 'Direct_Aging')")
    stages: List[ThermalCycleStage] = Field(default_factory=list)

    def total_duration_seconds(self) -> float:
        total = 0.0
        for s in self.stages:
            delta_t = abs(s.target_temp_k - s.start_temp_k)
            ramp_time = delta_t / s.ramp_rate_k_s if s.ramp_rate_k_s > 0 else 0.0
            total += ramp_time + s.dwell_time_seconds
        return total


class ProcessRecipe(BaseModel):
    """
    Consolidated Process Recipe linking manufacturing route, route-specific parameters,
    and post-processing heat treatment schedules.
    """
    recipe_id: str = Field(..., description="Unique recipe identifier or hash")
    route: ManufacturingRoute
    lpbf_params: Optional[LPBFParameters] = None
    ded_params: Optional[DEDParameters] = None
    pm_params: Optional[PMSinteringParameters] = None
    casting_params: Optional[CastingParameters] = None
    heat_treatment: Optional[HeatTreatmentSchedule] = None
    target_part_geometry: Optional[str] = Field(default=None, description="CAD file path or geometry descriptor")
    notes: Dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_route_parameters(self) -> "ProcessRecipe":
        if self.route == ManufacturingRoute.LPBF and not self.lpbf_params:
            # Provide sensible defaults if not explicitly provided
            self.lpbf_params = LPBFParameters(
                laser_power_w=200.0,
                scan_velocity_m_s=1.0,
                hatch_spacing_um=100.0,
                layer_thickness_um=30.0
            )
        elif self.route == ManufacturingRoute.PM_SINTERING and not self.pm_params:
            self.pm_params = PMSinteringParameters(
                sintering_temp_k=1673.15,
                dwell_time_minutes=15.0
            )
        return self
