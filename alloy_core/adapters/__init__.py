"""
Adapters bridging the 6 specialized alloy agent packages to canonical alloy-core schemas.
"""

from alloy_core.adapters.morph_adapter import MorphAdapter
from alloy_core.adapters.sinter_adapter import SinterAdapter
from alloy_core.adapters.pilot_adapter import PilotAdapter
from alloy_core.adapters.props_adapter import PropsAdapter
from alloy_core.adapters.lit_adapter import LitAdapter

__all__ = [
    "MorphAdapter",
    "SinterAdapter",
    "PilotAdapter",
    "PropsAdapter",
    "LitAdapter"
]
