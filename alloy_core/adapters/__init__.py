"""
Unified adapter registry bridging domain engines to canonical alloy-core contracts.
"""

from .lab_adapter import LabAdapter
from .lit_adapter import LitAdapter
from .props_adapter import PropsAdapter
from .pilot_adapter import PilotAdapter
from .phase_adapter import PhaseAdapter, PhaseEquilibriumResult
from .morph_adapter import MorphAdapter
from .sinter_adapter import SinterAdapter
from .diffuse_adapter import DiffuseAdapter
from .field_adapter import FieldAdapter
from .fluid_adapter import FluidAdapter
from .macro_adapter import MacroAdapter
from .pbf_adapter import PbfAdapter, PbfBuildResult
from .perform_adapter import PerformAdapter

__all__ = [
    "LabAdapter",
    "LitAdapter",
    "PropsAdapter",
    "PilotAdapter",
    "PhaseAdapter",
    "PhaseEquilibriumResult",
    "MorphAdapter",
    "SinterAdapter",
    "DiffuseAdapter",
    "FieldAdapter",
    "FluidAdapter",
    "MacroAdapter",
    "PbfAdapter",
    "PbfBuildResult",
    "PerformAdapter",
]
