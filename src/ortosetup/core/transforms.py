"""Transformaciones rígidas de 6 grados de libertad para dientes.

CONVENCIÓN (fuente de verdad; ver docs/CONVENCIONES_EJES.md)
------------------------------------------------------------
Cada diente tiene un sistema de referencia local (ToothFrame):
  - origen  : pivote de las rotaciones (Fase 1: centroide de la corona, provisional).
  - eje x   : mesiodistal        (+ hacia mesial)
  - eje y   : vestibulolingual   (+ hacia vestibular)
  - eje z   : eje largo          (+ hacia oclusal/incisal)
Los ejes se guardan como columnas de una matriz 3x3 ortonormal, en coordenadas
del escaneo original (milímetros).

Un movimiento (Movement6DOF) se expresa en ese sistema local:
  - md_mm  : traslación sobre x
  - vl_mm  : traslación sobre y
  - oc_mm  : traslación sobre z  (+ extrusión, - intrusión)
  - rot_deg    : rotación sobre z (eje largo)
  - tip_deg    : rotación sobre y (angulación mesiodistal)
  - torque_deg : rotación sobre x (inclinación vestibulolingual)
Signos de rotación: regla de la mano derecha sobre el eje correspondiente.
La traducción a signos clínicos por cuadrante (p. ej. "torque radicular
vestibular positivo") NO se resuelve aquí: es tarea de la Fase 3 (landmarks).

Orden de composición (fijo, documentado y probado):
    L = T(md, vl, oc) · Rz(rot) · Ry(tip) · Rx(torque)
    W = F · L · F⁻¹
donde F es la matriz 4x4 del sistema local en coordenadas del escaneo.
El movimiento es ABSOLUTO respecto de la posición inicial (no acumulativo),
de modo que reabrir un proyecto reproduce exactamente la misma matriz.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Iterable

import numpy as np

ORTHONORMAL_TOL = 1e-9


def _rx(deg: float) -> np.ndarray:
    a = np.deg2rad(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=float)


def _ry(deg: float) -> np.ndarray:
    a = np.deg2rad(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=float)


def _rz(deg: float) -> np.ndarray:
    a = np.deg2rad(deg)
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=float)


@dataclass(frozen=True)
class Movement6DOF:
    md_mm: float = 0.0
    vl_mm: float = 0.0
    oc_mm: float = 0.0
    rot_deg: float = 0.0
    tip_deg: float = 0.0
    torque_deg: float = 0.0

    def __post_init__(self) -> None:
        for name, value in asdict(self).items():
            if not np.isfinite(value):
                raise ValueError(f"Movimiento inválido: {name}={value!r}")

    def is_identity(self) -> bool:
        return all(v == 0.0 for v in asdict(self).values())

    def to_dict(self) -> dict:
        return {k: float(v) for k, v in asdict(self).items()}

    @classmethod
    def from_dict(cls, d: dict) -> "Movement6DOF":
        return cls(**{k: float(d[k]) for k in cls.__dataclass_fields__})

    def local_matrix(self) -> np.ndarray:
        m = np.eye(4)
        m[:3, :3] = _rz(self.rot_deg) @ _ry(self.tip_deg) @ _rx(self.torque_deg)
        m[:3, 3] = (self.md_mm, self.vl_mm, self.oc_mm)
        return m


@dataclass(frozen=True)
class ToothFrame:
    origin: tuple[float, float, float]
    # columnas = ejes x (MD), y (VL), z (eje largo), en coordenadas del escaneo
    axes: tuple[tuple[float, float, float], ...] = (
        (1.0, 0.0, 0.0),
        (0.0, 1.0, 0.0),
        (0.0, 0.0, 1.0),
    )
    source: str = "provisional_world_axes"

    def __post_init__(self) -> None:
        a = self.axes_matrix()
        if a.shape != (3, 3):
            raise ValueError("axes debe ser 3x3")
        if not np.allclose(a.T @ a, np.eye(3), atol=ORTHONORMAL_TOL):
            raise ValueError("Los ejes del diente no son ortonormales")
        if np.linalg.det(a) < 0:
            raise ValueError("Los ejes del diente no forman un sistema dextrógiro")

    def axes_matrix(self) -> np.ndarray:
        """Matriz 3x3 cuyas COLUMNAS son los ejes x, y, z."""
        return np.array(self.axes, dtype=float).T

    def matrix(self) -> np.ndarray:
        f = np.eye(4)
        f[:3, :3] = self.axes_matrix()
        f[:3, 3] = self.origin
        return f

    def to_dict(self) -> dict:
        return {
            "origin": [float(v) for v in self.origin],
            "axes": [[float(v) for v in ax] for ax in self.axes],
            "source": self.source,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ToothFrame":
        return cls(
            origin=tuple(float(v) for v in d["origin"]),
            axes=tuple(tuple(float(v) for v in ax) for ax in d["axes"]),
            source=str(d["source"]),
        )


def world_matrix(frame: ToothFrame, movement: Movement6DOF) -> np.ndarray:
    """Matriz 4x4 en coordenadas del escaneo que lleva la malla original a su nueva posición."""
    f = frame.matrix()
    return f @ movement.local_matrix() @ np.linalg.inv(f)


def apply_matrix(points: np.ndarray, m: np.ndarray) -> np.ndarray:
    pts = np.asarray(points, dtype=float)
    return pts @ m[:3, :3].T + m[:3, 3]


def is_rigid(m: np.ndarray, tol: float = 1e-9) -> bool:
    r = m[:3, :3]
    return bool(
        np.allclose(r.T @ r, np.eye(3), atol=tol)
        and abs(np.linalg.det(r) - 1.0) < tol
        and np.allclose(m[3], [0, 0, 0, 1])
    )
