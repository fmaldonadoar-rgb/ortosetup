"""Lectura de mallas (STL/PLY/OBJ) y comprobaciones geométricas.

Principios:
  * Nunca se modifica el archivo original. Las comprobaciones se hacen sobre
    una copia en memoria.
  * Se carga con process=False para no fusionar ni reordenar vértices: la
    geometría usada es exactamente la del archivo.
  * La unidad interna es el milímetro. El sistema NO reescala automáticamente;
    solo advierte cuando el tamaño es incompatible con un escaneo en mm.
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import trimesh

SUPPORTED_FORMATS = {".stl": "stl", ".ply": "ply", ".obj": "obj"}

# Rangos de plausibilidad de TAMAÑO (no son valores clínicos): sirven solo para
# detectar errores de unidad (metros, centímetros, micras). Editables.
PLAUSIBLE_EXTENT_MM = {
    "arch": (25.0, 150.0),   # extensión máxima de una arcada/modelo
    "tooth": (3.0, 30.0),    # extensión máxima de una corona/diente
}


class MeshImportError(Exception):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def detect_format(path: Path) -> str:
    fmt = SUPPORTED_FORMATS.get(Path(path).suffix.lower())
    if fmt is None:
        raise MeshImportError(
            f"Formato no soportado: {Path(path).suffix!r}. Use STL, PLY u OBJ."
        )
    return fmt


def load_mesh(path: Path) -> trimesh.Trimesh:
    path = Path(path)
    detect_format(path)
    if not path.is_file():
        raise MeshImportError(f"No existe el archivo: {path}")
    if path.stat().st_size == 0:
        raise MeshImportError(f"Archivo vacío: {path.name}")
    try:
        mesh = trimesh.load(path, process=False, force="mesh")
    except Exception as exc:  # trimesh lanza tipos variados
        raise MeshImportError(f"No se pudo leer {path.name}: {exc}") from exc
    if not isinstance(mesh, trimesh.Trimesh) or len(mesh.faces) == 0:
        raise MeshImportError(f"{path.name} no contiene una malla triangular válida")
    return mesh


@dataclass
class GeometryReport:
    n_vertices: int
    n_faces: int
    extents_mm: list[float]
    max_extent_mm: float
    has_non_finite: bool
    n_degenerate_faces: int
    n_boundary_edges: int
    n_nonmanifold_edges: int
    is_watertight: bool
    n_components: int
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def to_dict(self) -> dict:
        d = dict(self.__dict__)
        d["ok"] = self.ok
        return d


def check_geometry(mesh: trimesh.Trimesh, kind: str = "arch") -> GeometryReport:
    """Diagnóstico de integridad y escala. No modifica `mesh`."""
    v = np.asarray(mesh.vertices, dtype=float)
    f = np.asarray(mesh.faces)
    has_non_finite = not np.all(np.isfinite(v))
    errors: list[str] = []
    warnings: list[str] = []

    if has_non_finite:
        errors.append("La malla contiene coordenadas no finitas (NaN/Inf).")
        extents = [float("nan")] * 3
    else:
        extents = (v.max(axis=0) - v.min(axis=0)).tolist()
    max_extent = float(np.nanmax(extents)) if not has_non_finite else float("nan")

    # Análisis topológico sobre una copia con vértices fusionados.
    work = mesh.copy()
    if not has_non_finite:
        work.merge_vertices()
    areas = work.area_faces
    n_degenerate = int(np.sum(~np.isfinite(areas) | (areas <= 1e-12)))
    edges = np.sort(work.edges, axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    n_boundary = int(np.sum(counts == 1))
    n_nonmanifold = int(np.sum(counts > 2))
    try:
        n_components = int(len(work.split(only_watertight=False)))
    except Exception:
        n_components = -1

    if n_degenerate:
        warnings.append(f"{n_degenerate} triángulos degenerados (área ~0).")
    if n_nonmanifold:
        warnings.append(f"{n_nonmanifold} aristas no-manifold (compartidas por >2 caras).")
    if n_boundary:
        warnings.append(
            f"Superficie abierta: {n_boundary} aristas de borde "
            "(habitual en escaneos intraorales; relevante para exportación)."
        )
    if n_components > 1:
        warnings.append(f"La malla tiene {n_components} componentes separados.")

    lo, hi = PLAUSIBLE_EXTENT_MM.get(kind, PLAUSIBLE_EXTENT_MM["arch"])
    if np.isfinite(max_extent):
        if max_extent < 1.0:
            warnings.append(
                f"Extensión máxima {max_extent:.4g}: probablemente en METROS, no mm. "
                "Verifique la unidad de exportación del escáner. No se reescaló."
            )
        elif max_extent < lo:
            warnings.append(
                f"Extensión máxima {max_extent:.4g} mm es menor de lo esperado para "
                f"'{kind}' ({lo}-{hi} mm): posible unidad en cm o modelo incompleto."
            )
        elif max_extent > hi:
            warnings.append(
                f"Extensión máxima {max_extent:.4g} mm es mayor de lo esperado para "
                f"'{kind}' ({lo}-{hi} mm): posible unidad distinta de mm."
            )

    return GeometryReport(
        n_vertices=int(len(v)),
        n_faces=int(len(f)),
        extents_mm=[float(e) for e in extents],
        max_extent_mm=max_extent,
        has_non_finite=has_non_finite,
        n_degenerate_faces=n_degenerate,
        n_boundary_edges=n_boundary,
        n_nonmanifold_edges=n_nonmanifold,
        is_watertight=bool(work.is_watertight),
        n_components=n_components,
        warnings=warnings,
        errors=errors,
    )


def area_weighted_centroid(mesh: trimesh.Trimesh) -> np.ndarray:
    """Centroide de superficie (ponderado por área). Independiente de la densidad de vértices."""
    tri = mesh.triangles
    areas = mesh.area_faces
    if areas.sum() <= 0:
        return np.asarray(mesh.vertices, dtype=float).mean(axis=0)
    centers = tri.mean(axis=1)
    return (centers * areas[:, None]).sum(axis=0) / areas.sum()
