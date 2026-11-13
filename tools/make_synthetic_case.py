"""Genera un caso dental SINTÉTICO (sin datos de pacientes) para pruebas.

Produce, en milímetros:
  <out>/upper_arch.stl, <out>/lower_arch.stl         (encía simplificada + dientes)
  <out>/teeth/11.stl ... 17.stl, 21..27, 31..37, 41..47 (una malla por diente)

Las formas son elipsoides sobre una parábola: NO representan anatomía real.
Sirven solo para probar importación, transformaciones y persistencia.

Uso:  python tools/make_synthetic_case.py salida/
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import trimesh

# Tamaños aproximados (mm) para que las proporciones sean verosímiles en pantalla.
# Valores ilustrativos de una malla sintética, no datos clínicos.
CROWN_SIZE = {1: (8.5, 7.0, 10.0), 2: (6.5, 6.0, 9.0), 3: (7.5, 8.0, 10.0),
              4: (7.0, 9.0, 8.0), 5: (6.5, 9.0, 7.5), 6: (10.0, 11.0, 7.0),
              7: (9.0, 10.5, 6.5)}


def _arch_curve(t: np.ndarray, half_width: float, depth: float) -> np.ndarray:
    # t en [-1, 1]; 0 = línea media
    x = half_width * t
    y = depth * (1 - t ** 2)
    return np.stack([x, y], axis=1)


def make_tooth(center, tangent, size, upper: bool, seed: int) -> trimesh.Trimesh:
    md, vl, h = size
    m = trimesh.creation.icosphere(subdivisions=3, radius=1.0)
    m.apply_scale((md / 2, vl / 2, h / 2))
    rng = np.random.default_rng(seed)
    m.vertices += rng.normal(scale=0.05, size=m.vertices.shape)  # textura leve
    ang = np.arctan2(tangent[1], tangent[0])
    rot = trimesh.transformations.rotation_matrix(ang, (0, 0, 1))
    m.apply_transform(rot)
    z = -h / 2 if upper else h / 2
    m.apply_translation((center[0], center[1], z))
    return m


def _tube(curve: np.ndarray, rx: float, rz: float, k: int = 12) -> trimesh.Trimesh:
    """Tubo elíptico abierto a lo largo de una curva 3D (sin dependencias extra)."""
    tan = np.gradient(curve, axis=0)
    tan /= np.linalg.norm(tan, axis=1, keepdims=True)
    up = np.array([0.0, 0.0, 1.0])
    side = np.cross(tan, up)
    side /= np.linalg.norm(side, axis=1, keepdims=True)
    ang = np.linspace(0, 2 * np.pi, k, endpoint=False)
    verts = (curve[:, None, :]
             + rx * np.cos(ang)[None, :, None] * side[:, None, :]
             + rz * np.sin(ang)[None, :, None] * up[None, None, :]).reshape(-1, 3)
    faces = []
    for i in range(len(curve) - 1):
        for j in range(k):
            a, b = i * k + j, i * k + (j + 1) % k
            c, d = a + k, b + k
            faces += [(a, b, d), (a, d, c)]
    return trimesh.Trimesh(verts, np.array(faces), process=False)


def make_case(out: Path) -> dict:
    out = Path(out)
    (out / "teeth").mkdir(parents=True, exist_ok=True)
    result = {}
    for upper, quads, zsign in ((True, (1, 2), 1.0), (False, (4, 3), -1.0)):
        parts = []
        hw, depth = (27.0, 28.0) if upper else (24.0, 25.0)
        ts = np.linspace(-0.95, 0.95, 14)
        pts = _arch_curve(ts, hw, depth)
        tans = np.gradient(pts, axis=0)
        order = [(quads[0], n) for n in range(7, 0, -1)] + [(quads[1], n) for n in range(1, 8)]
        for i, (q, n) in enumerate(order):
            fdi = q * 10 + n
            tooth = make_tooth(pts[i], tans[i], CROWN_SIZE[n], upper, seed=fdi)
            tooth.export(out / "teeth" / f"{fdi}.stl")
            parts.append(tooth)
        # encía: tubo aplanado a lo largo de la curva
        curve = np.column_stack([_arch_curve(np.linspace(-1, 1, 60), hw, depth),
                                 np.full(60, zsign * 3.0)])
        gum = _tube(curve, rx=5.0, rz=3.0)
        arch = trimesh.util.concatenate(parts + [gum])
        name = "upper_arch.stl" if upper else "lower_arch.stl"
        arch.export(out / name)
        result["upper" if upper else "lower"] = out / name
    return result


if __name__ == "__main__":
    target = Path(sys.argv[1] if len(sys.argv) > 1 else "caso_sintetico")
    files = make_case(target)
    print(f"Caso sintético generado en {target.resolve()}")
