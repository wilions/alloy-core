"""
Canonical Thermal History Schemas for the Alloy Intelligence Suite.
Standardizes thermal profiles across 3D Rosenthal / Eagar-Tsai solves,
furnace thermal cycles, and solid-state sintering profiles.
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class ThermalHistoryPoint(BaseModel):
    """Instantaneous thermal and kinematic state at a point in space/time."""
    time_s: float = Field(..., ge=0.0, description="Time in seconds")
    temperature_k: float = Field(..., gt=0.0, description="Temperature in Kelvin")
    cooling_rate_k_s: float = Field(default=0.0, description="dT/dt in K/s (negative for cooling)")
    thermal_gradient_k_m: float = Field(default=0.0, ge=0.0, description="Temperature gradient G = |grad T| in K/m")
    solidification_velocity_m_s: float = Field(default=0.0, ge=0.0, description="Isotherm velocity R in m/s")


class ThermalHistoryState(BaseModel):
    """Consolidated thermal history profile across a full processing cycle."""
    profile_id: str = Field(default="melt_pool_center", description="Location or cycle label")
    time_series_s: List[float] = Field(default_factory=list)
    temperature_series_k: List[float] = Field(default_factory=list)
    cooling_rate_series_k_s: List[float] = Field(default_factory=list)
    peak_temperature_k: float = Field(default=0.0, ge=0.0)
    solidification_cooling_rate_k_s: Optional[float] = Field(
        default=None,
        description="Average cooling rate across liquidus-solidus freezing interval (K/s)"
    )
    total_duration_s: float = Field(default=0.0, ge=0.0)

    def add_point(self, time_s: float, temp_k: float, cooling_rate_k_s: float = 0.0) -> None:
        self.time_series_s.append(time_s)
        self.temperature_series_k.append(temp_k)
        self.cooling_rate_series_k_s.append(cooling_rate_k_s)
        if temp_k > self.peak_temperature_k:
            self.peak_temperature_k = temp_k
        if time_s > self.total_duration_s:
            self.total_duration_s = time_s
