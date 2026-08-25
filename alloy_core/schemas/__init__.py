"""
Unified schemas for the Alloy Intelligence Suite.
"""

from alloy_core.schemas.composition import MaterialComposition, ATOMIC_WEIGHTS, VALENCE_ELECTRONS
from alloy_core.schemas.manufacturing import (
    ManufacturingRoute,
    ProcessRecipe,
    LPBFParameters,
    DEDParameters,
    PMSinteringParameters,
    CastingParameters,
    ThermalCycleStage,
    HeatTreatmentSchedule
)
from alloy_core.schemas.thermal import ThermalHistoryPoint, ThermalHistoryState
from alloy_core.schemas.microstructure import (
    MicrostructureState,
    PrecipitatePopulation,
    GrainMorphology,
    PhaseConstituent,
    ComplexionState
)
from alloy_core.schemas.properties import (
    PropertyTensor,
    MechanicalProperties,
    ThermophysicalProperties,
    UncertaintyEstimate,
    DistributionType
)
from alloy_core.schemas.evidence import (
    EvidenceRecord,
    DataTier,
    ProvenancePillar
)
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
from alloy_core.schemas.pspp import PSPPState

__all__ = [
    "MaterialComposition",
    "ATOMIC_WEIGHTS",
    "VALENCE_ELECTRONS",
    "ManufacturingRoute",
    "ProcessRecipe",
    "LPBFParameters",
    "DEDParameters",
    "PMSinteringParameters",
    "CastingParameters",
    "ThermalCycleStage",
    "HeatTreatmentSchedule",
    "ThermalHistoryPoint",
    "ThermalHistoryState",
    "MicrostructureState",
    "PrecipitatePopulation",
    "GrainMorphology",
    "PhaseConstituent",
    "ComplexionState",
    "PropertyTensor",
    "MechanicalProperties",
    "ThermophysicalProperties",
    "UncertaintyEstimate",
    "DistributionType",
    "EvidenceRecord",
    "DataTier",
    "ProvenancePillar",
    "DiffusionCouple",
    "DiffusionCoefficientTensor",
    "DiffusionProfile",
    "InterdiffusionFluxState",
    "MeltPoolGeometry",
    "MeltPoolThermalState",
    "PoreDefectMap",
    "MeltPoolCFDResult",
    "InherentStrainTensor",
    "PartMeshState",
    "ResidualStressState",
    "MacroDistortionResult",
    "FatigueSNState",
    "CreepRuptureState",
    "OxidationKineticsState",
    "PerformanceEnvelope",
    "PSPPState"
]
