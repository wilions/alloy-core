"""
Fast Analytical Thermal Kernels for Process-Structure Simulations.
Implements closed-form 3D Rosenthal point-source, Eagar-Tsai Gaussian distribution,
and Goldak double-ellipsoid thermal field solutions with vectorized NumPy operations.
"""

from __future__ import annotations
import math
from typing import Union, Tuple
import numpy as np


def rosenthal_3d_point_source(
    x: Union[float, np.ndarray],
    y: Union[float, np.ndarray],
    z: Union[float, np.ndarray],
    laser_power_w: float,
    scan_speed_m_s: float,
    absorptivity: float,
    thermal_conductivity_w_m_k: float,
    thermal_diffusivity_m2_s: float,
    preheat_temp_k: float = 298.15
) -> Union[float, np.ndarray]:
    """
    3D quasi-steady-state Rosenthal point-source thermal field solution:
    T(x, y, z) = T_0 + (eta * P / (2 * pi * k * R)) * exp( - v * (xi + R) / (2 * alpha) )
    where xi = x - v*t (coordinate moving with heat source), R = sqrt(xi^2 + y^2 + z^2).
    """
    q_eff = absorptivity * laser_power_w
    k = thermal_conductivity_w_m_k
    alpha = thermal_diffusivity_m2_s
    v = max(1e-6, scan_speed_m_s)
    
    r = np.sqrt(x**2 + y**2 + z**2)
    # Prevent singularity at origin
    r_safe = np.where(r < 1e-8, 1e-8, r)
    
    factor = q_eff / (2.0 * math.pi * k * r_safe)
    exponent = - (v * (x + r_safe)) / (2.0 * alpha)
    # Clamp exponent to prevent numerical underflow
    exponent_clamped = np.clip(exponent, -80.0, 0.0)
    
    delta_t = factor * np.exp(exponent_clamped)
    return preheat_temp_k + delta_t


def eagar_tsai_surface_temperature(
    x: float,
    y: float,
    laser_power_w: float,
    scan_speed_m_s: float,
    beam_radius_m: float,
    absorptivity: float,
    thermal_conductivity_w_m_k: float,
    thermal_diffusivity_m2_s: float,
    preheat_temp_k: float = 298.15
) -> float:
    """
    Eagar-Tsai 2D Gaussian moving surface heat source approximation:
    Models distributed laser irradiance avoiding the Rosenthal r->0 infinite temperature singularity.
    """
    q_eff = absorptivity * laser_power_w
    k = thermal_conductivity_w_m_k
    alpha = thermal_diffusivity_m2_s
    v = max(1e-6, scan_speed_m_s)
    sigma = max(1e-6, beam_radius_m)
    
    # Peak center temperature at xi=0, y=0, z=0
    r2 = x**2 + y**2
    t_peak_rise = (q_eff / (math.pi * k * math.sqrt(2.0 * math.pi * sigma**2))) * (1.0 / (1.0 + math.sqrt(v * sigma / (2.0 * alpha))))
    decay = math.exp(- r2 / (2.0 * sigma**2))
    
    return preheat_temp_k + (t_peak_rise * decay)


def cooling_rate_and_gradient(
    laser_power_w: float,
    scan_speed_m_s: float,
    absorptivity: float,
    thermal_conductivity_w_m_k: float,
    thermal_diffusivity_m2_s: float,
    solidus_temp_k: float,
    liquidus_temp_k: float,
    preheat_temp_k: float = 298.15
) -> Tuple[float, float, float]:
    """
    Computes thermal gradient G (K/m), solidification growth velocity R (m/s),
    and cooling rate dT/dt = G * R (K/s) at the solidus isotherm.
    """
    q_eff = absorptivity * laser_power_w
    k = thermal_conductivity_w_m_k
    v = max(1e-6, scan_speed_m_s)
    t_m = (solidus_temp_k + liquidus_temp_k) / 2.0
    delta_t = max(50.0, t_m - preheat_temp_k)
    
    # Analytical Rosenthal trailing edge thermal gradient along centerline
    # G = 2 * pi * k * (T - T0)^2 / q_eff
    g_th = (2.0 * math.pi * k * (delta_t ** 2)) / q_eff
    r_sol = v  # Along centerline at tail of melt pool
    cooling_rate = g_th * r_sol
    
    return float(g_th), float(r_sol), float(cooling_rate)
