"""Validación de nomenclatura FDI (ISO 3950)."""
from __future__ import annotations

import re
from pathlib import Path

PERMANENT_QUADRANTS = {1: "upper", 2: "upper", 3: "lower", 4: "lower"}
PRIMARY_QUADRANTS = {5: "upper", 6: "upper", 7: "lower", 8: "lower"}


def validate_fdi(code: int) -> int:
    code = int(code)
    q, n = divmod(code, 10)
    if q in PERMANENT_QUADRANTS and 1 <= n <= 8:
        return code
    if q in PRIMARY_QUADRANTS and 1 <= n <= 5:
        return code
    raise ValueError(f"Código FDI inválido: {code}")


def arch_of(code: int) -> str:
    q = validate_fdi(code) // 10
    return {**PERMANENT_QUADRANTS, **PRIMARY_QUADRANTS}[q]


_FDI_IN_NAME = re.compile(r"(?<!\d)([1-8][1-8])(?!\d)")


def fdi_from_filename(path: Path) -> int | None:
    """Extrae un código FDI de nombres como '11.stl', 'diente_36.ply', 'tooth-21.obj'.

    Devuelve None si no hay exactamente un candidato válido (no adivina).
    """
    stem = Path(path).stem
    candidates = []
    for m in _FDI_IN_NAME.finditer(stem):
        try:
            candidates.append(validate_fdi(int(m.group(1))))
        except ValueError:
            pass
    return candidates[0] if len(set(candidates)) == 1 else None
