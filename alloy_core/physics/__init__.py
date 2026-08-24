"""
Unified Physics Microkernels for the Alloy Intelligence Suite.
"""

from alloy_core.physics.kwn import UnifiedKWNEngine, PrecipitateThermodynamicParams, SYSTEM_PRECIPITATE_DB
from alloy_core.physics.czm import UnifiedCZMEngine, CZMResult
from alloy_core.physics.solidification import UnifiedSolidificationEngine, SolidificationCurve
from alloy_core.physics.elasticity import UnifiedElasticityEngine, ElasticConstants

__all__ = [
    "UnifiedKWNEngine",
    "PrecipitateThermodynamicParams",
    "SYSTEM_PRECIPITATE_DB",
    "UnifiedCZMEngine",
    "CZMResult",
    "UnifiedSolidificationEngine",
    "SolidificationCurve",
    "UnifiedElasticityEngine",
    "ElasticConstants"
]
