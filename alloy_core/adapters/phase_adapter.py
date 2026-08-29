"""
Adapter bridging alloy-phase (pycalphad) calculations with canonical alloy-core contracts.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class PhaseEquilibriumResult(BaseModel):
    """Canonical representation of CALPHAD phase equilibria and solidification."""
    liquidus_temperature_k: float = Field(..., description="Liquidus temperature in Kelvin")
    solidus_temperature_k: float = Field(..., description="Solidus temperature in Kelvin")
    freezing_range_k: float = Field(..., description="Solidification freezing range (T_L - T_S) in Kelvin")
    latent_heat_of_fusion_j_kg: float = Field(default=270000.0, description="Latent heat of fusion in J/kg")
    kou_cracking_index: float = Field(default=0.0, description="Kou solidification hot cracking metric |dT/d(f_s^0.5)|")
    stable_phases: List[str] = Field(default_factory=list, description="List of stable phases at equilibrium")
    phase_fractions: Dict[str, float] = Field(default_factory=dict, description="Phase volume/mole fractions")
    solver_name: str = Field(default="alloy-phase-calphad-v0.1.0", description="Thermodynamic solver designation")


class PhaseAdapter:
    """Converts alloy-phase CALPHAD simulation results into canonical schema representations."""

    @staticmethod
    def to_phase_result(
        liquidus_k: float,
        solidus_k: float,
        kou_index: float = 0.0,
        latent_heat_j_kg: float = 270000.0,
        stable_phases: Optional[List[str]] = None,
        phase_fractions: Optional[Dict[str, float]] = None,
        solver_name: str = "alloy-phase-pycalphad-v0.1.0"
    ) -> PhaseEquilibriumResult:
        return PhaseEquilibriumResult(
            liquidus_temperature_k=liquidus_k,
            solidus_temperature_k=solidus_k,
            freezing_range_k=max(0.0, liquidus_k - solidus_k),
            latent_heat_of_fusion_j_kg=latent_heat_j_kg,
            kou_cracking_index=kou_index,
            stable_phases=stable_phases or [],
            phase_fractions=phase_fractions or {},
            solver_name=solver_name
        )
