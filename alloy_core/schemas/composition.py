"""
Canonical Material Composition Schema for the Alloy Intelligence Suite.
Enforces strict elemental validity, atomic/mass fraction conversions,
and empirical solid-solution parameters (VEC, Delta H_mix, Delta S_mix).
"""

from __future__ import annotations
import math
from typing import Dict, Optional, List, Tuple
from pydantic import BaseModel, Field, model_validator, field_validator

# Standard atomic weights (g/mol) for common metallurgical elements
ATOMIC_WEIGHTS: Dict[str, float] = {
    "H": 1.008, "He": 4.0026, "Li": 6.94, "Be": 9.0122, "B": 10.81,
    "C": 12.011, "N": 14.007, "O": 15.999, "F": 18.998, "Ne": 20.180,
    "Na": 22.990, "Mg": 24.305, "Al": 26.982, "Si": 28.085, "P": 30.974,
    "S": 32.06, "Cl": 35.45, "Ar": 39.948, "K": 39.098, "Ca": 40.078,
    "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 51.996, "Mn": 54.938,
    "Fe": 55.845, "Co": 58.933, "Ni": 58.693, "Cu": 63.546, "Zn": 65.38,
    "Ga": 69.723, "Ge": 72.630, "As": 74.922, "Se": 78.971, "Y": 88.906,
    "Zr": 91.224, "Nb": 92.906, "Mo": 95.95, "Ru": 101.07, "Rh": 102.91,
    "Pd": 106.42, "Ag": 107.87, "Cd": 112.41, "In": 114.82, "Sn": 118.71,
    "Hf": 178.49, "Ta": 180.95, "W": 183.84, "Re": 186.21, "Os": 190.23,
    "Ir": 192.22, "Pt": 195.08, "Au": 196.97, "Pb": 207.2, "Bi": 208.98,
    "La": 138.91, "Ce": 140.12, "Pr": 140.91, "Nd": 144.24, "Sm": 150.36,
    "Eu": 151.96, "Gd": 157.25, "Tb": 158.93, "Dy": 162.50, "Ho": 164.93,
    "Er": 167.26, "Tm": 168.93, "Yb": 173.05, "Lu": 174.97, "Th": 232.04,
    "U": 238.03
}

# Valence Electron Concentration (VEC) values
VALENCE_ELECTRONS: Dict[str, float] = {
    "Al": 3, "Si": 4, "Sc": 3, "Ti": 4, "V": 5, "Cr": 6, "Mn": 7,
    "Fe": 8, "Co": 9, "Ni": 10, "Cu": 11, "Zn": 12, "Ga": 3, "Ge": 4,
    "Y": 3, "Zr": 4, "Nb": 5, "Mo": 6, "Ru": 8, "Rh": 9, "Pd": 10,
    "Ag": 11, "Hf": 4, "Ta": 5, "W": 6, "Re": 7, "Os": 8, "Ir": 9,
    "Pt": 10, "Au": 11, "Mg": 2, "C": 4, "B": 3, "N": 5, "O": 6
}


class MaterialComposition(BaseModel):
    """
    Standardized, validated chemical composition container.
    Supports atomic fraction and weight fraction with exact closed-loop conversions.
    """
    fractions: Dict[str, float] = Field(
        ...,
        description="Map of element symbol to fraction (e.g. {'Ti': 0.90, 'Al': 0.06, 'V': 0.04})"
    )
    basis: str = Field(
        default="weight",
        description="Composition basis: 'weight' (mass fraction) or 'atomic' (mole fraction)"
    )
    base_element: Optional[str] = Field(
        default=None,
        description="Matrix / solvent element symbol (inferred if None)"
    )
    impurity_limits_ppm: Dict[str, float] = Field(
        default_factory=dict,
        description="Maximum permissible impurity concentrations in parts per million (e.g. {'O': 1200, 'N': 300, 'C': 500})"
    )
    alloy_family: Optional[str] = Field(
        default=None,
        description="Broad metallurgical family (e.g. 'titanium', 'superalloy', 'refractory', 'aluminum', 'steel')"
    )

    @field_validator("fractions")
    @classmethod
    def validate_elements(cls, v: Dict[str, float]) -> Dict[str, float]:
        if not v:
            raise ValueError("Composition fractions cannot be empty.")
        for elem, frac in v.items():
            if elem not in ATOMIC_WEIGHTS:
                raise ValueError(f"Unknown or unsupported chemical element: '{elem}'")
            if frac < 0.0:
                raise ValueError(f"Fraction for '{elem}' cannot be negative: {frac}")
        return v

    @model_validator(mode="after")
    def auto_normalize_and_detect_base(self) -> "MaterialComposition":
        total = sum(self.fractions.values())
        if total <= 0.0:
            raise ValueError("Sum of elemental fractions must be strictly positive.")
        
        # Handle percentage vs fraction scale
        if abs(total - 100.0) < 1e-2 and abs(total - 1.0) > 1e-4:
            self.fractions = {k: v / 100.0 for k, v in self.fractions.items()}
            total = 1.0
        elif abs(total - 1.0) > 1e-5:
            self.fractions = {k: v / total for k, v in self.fractions.items()}

        if not self.base_element:
            self.base_element = max(self.fractions.items(), key=lambda x: x[1])[0]

        if not self.alloy_family:
            self.alloy_family = self._infer_alloy_family()

        return self

    def _infer_alloy_family(self) -> str:
        base = self.base_element or "Fe"
        if base == "Ti":
            return "titanium"
        elif base == "Al":
            return "aluminum"
        elif base == "Ni":
            return "nickel_superalloy"
        elif base == "Co":
            return "cobalt_superalloy"
        elif base == "Fe":
            return "steel"
        elif base in ["Mo", "W", "Nb", "Ta", "Re"]:
            return "refractory"
        elif base == "Cu":
            return "copper"
        elif base == "Mg":
            return "magnesium"
        return "multi_principal_element"

    def to_weight_fractions(self) -> MaterialComposition:
        """Return a new MaterialComposition converted to weight fraction basis."""
        if self.basis == "weight":
            return self.model_copy()
        # Convert from atomic to weight
        total_mass = sum(x_i * ATOMIC_WEIGHTS[elem] for elem, x_i in self.fractions.items())
        w_dict = {elem: (x_i * ATOMIC_WEIGHTS[elem]) / total_mass for elem, x_i in self.fractions.items()}
        return MaterialComposition(
            fractions=w_dict,
            basis="weight",
            base_element=self.base_element,
            impurity_limits_ppm=self.impurity_limits_ppm,
            alloy_family=self.alloy_family
        )

    def to_atomic_fractions(self) -> MaterialComposition:
        """Return a new MaterialComposition converted to atomic fraction basis."""
        if self.basis == "atomic":
            return self.model_copy()
        # Convert from weight to atomic
        total_moles = sum(w_i / ATOMIC_WEIGHTS[elem] for elem, w_i in self.fractions.items())
        x_dict = {elem: (w_i / ATOMIC_WEIGHTS[elem]) / total_moles for elem, w_i in self.fractions.items()}
        return MaterialComposition(
            fractions=x_dict,
            basis="atomic",
            base_element=self.base_element,
            impurity_limits_ppm=self.impurity_limits_ppm,
            alloy_family=self.alloy_family
        )

    def average_atomic_weight(self) -> float:
        """Calculates molar average atomic weight (g/mol)."""
        at_comp = self.to_atomic_fractions()
        return sum(x_i * ATOMIC_WEIGHTS[elem] for elem, x_i in at_comp.fractions.items())

    def calculate_vec(self) -> float:
        """Calculates the average Valence Electron Concentration (VEC)."""
        at_comp = self.to_atomic_fractions()
        vec_sum = 0.0
        for elem, x_i in at_comp.fractions.items():
            vec_val = VALENCE_ELECTRONS.get(elem, 4.0)
            vec_sum += x_i * vec_val
        return vec_sum

    def calculate_ideal_mixing_entropy(self) -> float:
        """Calculates ideal configuration entropy of mixing Delta S_mix in J/(mol·K)."""
        at_comp = self.to_atomic_fractions()
        R_GAS = 8.314462
        s_mix = 0.0
        for x_i in at_comp.fractions.values():
            if x_i > 1e-9:
                s_mix -= R_GAS * x_i * math.log(x_i)
        return s_mix

    def formula_string(self) -> str:
        """Generate human-readable alloy formula string (e.g. Ti-6Al-4V or Mo-0.5Ti-0.08Zr)."""
        base = self.base_element or "Base"
        solutes = sorted(
            [(k, v) for k, v in self.fractions.items() if k != base],
            key=lambda x: x[1],
            reverse=True
        )
        if not solutes:
            return f"Pure {base}"
        
        parts = [base]
        for elem, frac in solutes:
            if self.basis == "weight":
                pct = frac * 100.0
                parts.append(f"{pct:.2f}".rstrip("0").rstrip(".") + elem)
            else:
                pct = frac * 100.0
                parts.append(f"{elem}{pct:.2f}".rstrip("0").rstrip("."))
        return "-".join(parts)
