# AlloyCore (`alloy-core`)

Canonical PSPP Data Contracts, Multi-Engine Adapters, and Event Bus for the **Unified Alloy Intelligence Suite**.

## Architecture

`alloy-core` provides the single source of truth for:
- **Canonical Schemas (`alloy_core.schemas`)**:
  - `MaterialComposition`: Rigorous weight/atomic fraction conversion, normalization, impurity limits, base element solvent detection, and Miedema mixing enthalpy / VEC estimators.
  - `ProcessRecipe`: Typed parameterized schedules for Additive Manufacturing (LPBF/DED), Solid-State Powder Metallurgy (Milling, Compaction, Sintering), and Casting / Heat Treatments.
  - `ThermalHistoryState`: Standardized 3D thermal history point/series ($T(t), \dot{T}, G, R$).
  - `FluidMeltPoolState` (`alloy_core.schemas.fluid`): Melt pool geometry, Marangoni flow velocity, recoil pressure, and porosity defect maps ($d/w$, keyhole risk).
  - `DiffusionProfile` (`alloy_core.schemas.diffusion`): DICTRA-class multicomponent interdiffusion matrix $\tilde{D}_{ij}$, spatial concentration profiles, and Kirkendall marker velocities.
  - `MicrostructureState`: Multi-phase grain size, precipitate population ($r_p, N_v, f_v$), dislocation density, porosity, and complexion states.
  - `MacroDistortionResult` (`alloy_core.schemas.macro`): Inherent-strain tensor ($\mathbf{\varepsilon}^*$), part-scale displacement, and residual stress states.
  - `PropertyTensor`: Complete mechanical, thermophysical, and elastic property sets with explicit uncertainty representations.
  - `PerformanceEnvelope` (`alloy_core.schemas.performance`): Microstructure-sensitive fatigue life ($S-N$, FIP), high-temperature creep rupture (Norton/Monkman-Grant), and environmental oxidation kinetics ($k_p$).
  - `EvidenceRecord`: Cryptographic SHA-256 integrity hashes, data tier tagging, and DOI / MatWeb citations.
  - `CrossSystemInterchangePackage`: The end-to-end unified PSPP candidate ledger.
- **Cross-Engine Adapters (`alloy_core.adapters`)**:
  - `PhaseAdapter`: Interoperability with `alloy-phase` (CALPHAD Gibbs equilibria, Scheil solidification, Kou cracking).
  - `DiffuseAdapter`: Interoperability with `alloy-diffuse` (Multicomponent interdiffusion & homogenization).
  - `FluidAdapter`: Interoperability with `alloy-fluid` (Melt pool CFD, Marangoni flow, defect mapping).
  - `FieldAdapter`: Interoperability with `alloy-field` (KGT dendrite tip growth, Hunt CET, Cellular Automata).
  - `MorphAdapter`: Interoperability with `alloy-morph` (Microstructure-property surrogate mapping).
  - `MacroAdapter`: Interoperability with `alloy-macro` (Inherent strain FEM, cantilever distortion).
  - `PbfAdapter`: Interoperability with `alloy-pbf` (Voxel build simulation, HIP densification, support optimization).
  - `SinterAdapter`: Interoperability with `alloy-sinter` (DEM packing, DP-Cap compaction, SOVS sintering, CZM fracture).
  - `PerformAdapter`: Interoperability with `alloy-perform` (Tanaka-Mura fatigue S-N, Monkman-Grant creep, Wagner oxidation).
  - `PilotAdapter`: Interoperability with `alloy-pilot` (`AlloyForge` orchestrator).
  - `PropsAdapter`: Grounding against MatWeb database in `alloy-props`.
  - `LitAdapter`: Grounding against OKF literature records in `alloy-lit`.
  - `LabExecutionAdapter`: Translation of PSPP recipes into SiLA 2 / OPC UA robotic hardware commands and automated experimental observation ingestion.
- **Ecosystem Data Bus (`alloy_core.bus`)**:
  - `PSPPEventBus`: Event-sourced state ledger with publish/subscribe semantics and deterministic replay.
