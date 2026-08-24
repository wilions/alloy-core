"""
Unified Solidification & Solidification Cracking Metrics Engine.
Computes Scheil-Gulliver solidification curves, liquidus/solidus freezing intervals,
and terminal cracking susceptibility index |dT / d(f_s^0.5)| (Kou criterion).
"""

from __future__ import annotations
import math
from typing import Dict, List, Tuple, Optional
import numpy as np
from pydantic import BaseModel, Field


class SolidificationCurve(BaseModel):
    """Solidification trajectory with temperature and solid fraction."""
    liquidus_temp_k: float = Field(..., gt=0.0)
    solidus_temp_k: float = Field(..., gt=0.0)
    freezing_range_k: float = Field(..., ge=0.0)
    temperatures_k: List[float] = Field(default_factory=list)
    solid_fractions: List[float] = Field(default_factory=list)
    cracking_susceptibility_index: float = Field(default=0.0, ge=0.0, description="|dT / d(f_s^0.5)| at terminal solidification")
    crack_susceptibility_category: str = Field(default="low", description="'low', 'medium', 'high', 'severe'")


class UnifiedSolidificationEngine:
    """Consolidated Scheil-Gulliver and Kou cracking susceptibility solver."""

    @classmethod
    def calculate_scheil_curve(
        cls,
        liquidus_temp_k: float,
        solidus_temp_k: float,
        partition_coefficient_k0: float = 0.85,
        num_points: int = 100
    ) -> SolidificationCurve:
        """
        Computes non-equilibrium Scheil solidification profile:
        T(f_s) = T_L - (T_L - T_S) * ( (1 - (1-fs)^k0) / (1 - (1-0.999)^k0) ) or power law
        and evaluates Kou's cracking susceptibility index |dT / d(f_s^0.5)| in the terminal vulnerable regime.
        """
        T_L = liquidus_temp_k
        T_S = solidus_temp_k
        delta_T = max(T_L - T_S, 1.0)

        fs_eval = np.linspace(0.0, 1.0, num_points)
        k0 = max(min(partition_coefficient_k0, 0.99), 0.05)

        # Continuous Scheil temperature trajectory spanning T_L down to T_S at fs=1.0
        # T(fs) = T_L - delta_T * ( (1 - (1 - fs * 0.999)**k0) / (1 - (1 - 0.999)**k0) )
        norm_factor = 1.0 - (1.0 - 0.999) ** k0
        t_vals = []
        for fs in fs_eval:
            if fs <= 0.0:
                T_curr = T_L
            elif fs >= 1.0:
                T_curr = T_S
            else:
                frac_drop = (1.0 - (1.0 - fs * 0.999) ** k0) / norm_factor
                T_curr = T_L - delta_T * frac_drop
            t_vals.append(T_curr)

        t_arr = np.array(t_vals)
        sqrt_fs = np.sqrt(fs_eval)

        # Kou cracking index: |dT / d(sqrt(f_s))| evaluated between sqrt(f_s) = 0.80 and 0.98
        vulnerable_mask = (fs_eval >= 0.70) & (fs_eval <= 0.98)
        if np.sum(vulnerable_mask) >= 3:
            grad_t = np.gradient(t_arr[vulnerable_mask], sqrt_fs[vulnerable_mask])
            cracking_index = float(np.max(np.abs(grad_t)))
        else:
            cracking_index = float(delta_T / max(1.0 - k0, 0.01))

        category = "low"
        if cracking_index > 250.0:
            category = "severe"
        elif cracking_index > 120.0:
            category = "high"
        elif cracking_index > 50.0:
            category = "medium"

        return SolidificationCurve(
            liquidus_temp_k=round(T_L, 2),
            solidus_temp_k=round(T_S, 2),
            freezing_range_k=round(delta_T, 2),
            temperatures_k=[round(float(t), 2) for t in t_vals],
            solid_fractions=[round(float(f), 4) for f in fs_eval],
            cracking_susceptibility_index=round(cracking_index, 2),
            crack_susceptibility_category=category
        )
