# AlloyCore (`alloy-core`)

Canonical PSPP Data Contracts, Multi-Engine Adapters, and Event Bus for the **Unified Alloy Intelligence Suite**.

## Architecture

`alloy-core` provides the single source of truth for:
- **Canonical Schemas (`alloy_core.schemas`)**:
  - `MaterialComposition`: Rigorous weight/atomic fraction conversion, normalization, impurity limits, base element solvent detection, and Miedema mixing enthalpy / VEC estimators.
  - `ProcessRecipe`: Typed parameterized schedules for Additive Manufacturing (LPBF/DED), Solid-State Powder Metallurgy (Milling, Compaction, Sintering), and Casting / Heat Treatments.
  - `ThermalHistoryState`: Standardized 3D thermal history point/series ($T(t), \dot{T}, G, R$).
  - `MicrostructureState`: Multi-phase grain size, precipitate population ($r_p, N_v, f_v$), dislocation density, porosity, and complexion states.
  - `PropertyTensor`: Complete mechanical, thermophysical, and elastic property sets with explicit uncertainty representations.
  - `EvidenceRecord`: Cryptographic SHA-256 integrity hashes, data tier tagging, and DOI / MatWeb citations.
  - `CrossSystemInterchangePackage`: The end-to-end unified PSPP candidate ledger.
- **Cross-Engine Adapters (`alloy_core.adapters`)**:
  - `MorphAdapter`: Interoperability with `alloy-morph`.
  - `SinterAdapter`: Interoperability with `alloy-sinter`.
  - `PilotAdapter`: Interoperability with `alloy-pilot` (`AlloyForge`).
  - `PropsAdapter`: Grounding against MatWeb database in `alloy-props`.
  - `LitAdapter`: Grounding against OKF literature records in `alloy-lit`.
- **Ecosystem Data Bus (`alloy_core.bus`)**:
  - `PSPPEventBus`: Event-sourced state ledger with publish/subscribe semantics and deterministic replay.
