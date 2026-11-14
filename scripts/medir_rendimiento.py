"""Medición de rendimiento de OrtoSetup (AC10, prompt maestro §9.5).

Mide, para una malla (escaneo de una arcada) o para una malla sintética de
tamaño equivalente:
  - tamaño del archivo, vértices y triángulos;
  - tiempo de lectura (el mismo lector que usa el programa) y de diagnóstico;
  - tiempo de preparación para visualizar (conversión + normales suavizadas);
  - FPS al rotar la cámara 360° con render offscreen en la GPU;
  - memoria máxima del proceso;
  - qué GPU usa realmente VTK (en notebooks puede usar la integrada).

El reporte (rendimiento_ac10.txt) NO incluye el nombre ni la ruta del archivo
ni el texto de la cabecera STL, para que pueda compartirse sin datos
identificables (§18). La cabecera solo se muestra en pantalla si se pide con
--mostrar-cabecera.

Uso:
  python scripts/medir_rendimiento.py "C:\\ruta\\escaneo.stl"
  python scripts/medir_rendimiento.py --sintetico 500000
"""
from __future__ import annotations

import argparse
import os
import platform
import statistics
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Metas iniciales del §9.5 (editables; se ajustan con las mediciones).
META_FPS = 30.0
META_CARGA_S = 10.0


# --------------------------------------------------------------------- cabecera
@dataclass
class CabeceraSTL:
    tipo: str                 # "binario", "ascii" o "no_stl"
    texto: str = ""           # texto legible encontrado (solo para mostrar en pantalla)

    @property
    def tiene_texto(self) -> bool:
        return bool(self.texto.strip())


def inspeccionar_cabecera_stl(path: Path) -> CabeceraSTL:
    """Lee la cabecera de un STL sin cargar la malla.

    Un STL binario tiene 80 bytes libres al inicio que algunos escáneres llenan
    con texto (software, fecha y a veces el nombre del paciente). Un STL ASCII
    empieza con "solid <nombre>".
    """
    path = Path(path)
    if path.suffix.lower() != ".stl":
        return CabeceraSTL("no_stl")
    with open(path, "rb") as f:
        head = f.read(84)
    size = path.stat().st_size
    if len(head) >= 84:
        n_tri = int.from_bytes(head[80:84], "little")
        if 84 + 50 * n_tri == size:
            legible = bytes(b if 32 <= b < 127 else 32 for b in head[:80]).decode("ascii")
            return CabeceraSTL("binario", " ".join(legible.split()))
    if head[:5].lower() == b"solid":
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            primera = f.readline()
        return CabeceraSTL("ascii", primera[5:].strip())
    return CabeceraSTL("binario", "")


# --------------------------------------------------------------------- memoria
def memoria_maxima_mb() -> float | None:
    """Memoria máxima usada por este proceso (MB), sin dependencias nuevas."""
    try:
        if platform.system() == "Windows":
            import ctypes
            from ctypes import wintypes

            class PMC(ctypes.Structure):
                _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                            ("PeakWorkingSetSize", ctypes.c_size_t),
                            ("WorkingSetSize", ctypes.c_size_t),
                            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                            ("PagefileUsage", ctypes.c_size_t),
                            ("PeakPagefileUsage", ctypes.c_size_t)]

            pmc = PMC()
            pmc.cb = ctypes.sizeof(PMC)
            k32 = ctypes.WinDLL("kernel32", use_last_error=True)
            k32.GetCurrentProcess.restype = wintypes.HANDLE
            psapi = ctypes.WinDLL("psapi", use_last_error=True)
            ok = psapi.GetProcessMemoryInfo(k32.GetCurrentProcess(), ctypes.byref(pmc),
                                            pmc.cb)
            return pmc.PeakWorkingSetSize / 2**20 if ok else None
        import resource
        kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return kb / 1024 if platform.system() != "Darwin" else kb / 2**20
    except Exception:
        return None


# --------------------------------------------------------------------- sintético
def malla_sintetica(n_triangulos: int):
    """Superficie en forma de arcada (medio toro ondulado) con ~n triángulos.

    Solo sirve para medir rendimiento: no representa anatomía.
    """
    import trimesh

    nv = max(8, int(round(np.sqrt(n_triangulos / 2 / 3))))      # alrededor del tubo
    nu = max(8, int(round(n_triangulos / 2 / nv)))              # a lo largo de la arcada
    u = np.linspace(0, np.pi, nu + 1)
    v = np.linspace(0, 2 * np.pi, nv, endpoint=False)
    uu, vv = np.meshgrid(u, v, indexing="ij")
    R, r = 25.0, 6.0 + 0.4 * np.sin(14 * uu)                    # mm, escala de arcada
    x = (R + r * np.cos(vv)) * np.cos(uu)
    y = (R + r * np.cos(vv)) * np.sin(uu)
    z = r * np.sin(vv) + 0.3 * np.sin(40 * uu) * np.cos(3 * vv)
    verts = np.column_stack([x.ravel(), y.ravel(), z.ravel()])
    idx = np.arange((nu + 1) * nv).reshape(nu + 1, nv)
    a = idx[:-1, :]
    b = idx[1:, :]
    c = np.roll(idx, -1, axis=1)[1:, :]
    d = np.roll(idx, -1, axis=1)[:-1, :]
    faces = np.vstack([np.column_stack([a.ravel(), b.ravel(), c.ravel()]),
                       np.column_stack([a.ravel(), c.ravel(), d.ravel()])])
    return trimesh.Trimesh(verts, faces, process=False)


# --------------------------------------------------------------------- medición
@dataclass
class Resultado:
    lineas: list[str] = field(default_factory=list)
    fps: float | None = None
    render_valido: bool = False
    carga_s: float | None = None

    def add(self, texto: str) -> None:
        self.lineas.append(texto)


def _esperar_gpu(pl) -> None:
    """Espera a que la GPU termine el cuadro (si no, render() mide solo el envío)."""
    rw = pl.ren_win
    if hasattr(rw, "WaitForCompletion"):
        rw.WaitForCompletion()
    else:  # lectura mínima: obliga a sincronizar
        rw.GetZbufferDataAtPoint(0, 0)


def medir(mesh, res: Resultado, frames: int, ancho: int, alto: int) -> None:
    import pyvista as pv
    from ortosetup.app.scene import _to_polydata

    res.add(f"Vertices: {len(mesh.vertices):,}".replace(",", "."))
    res.add(f"Triangulos: {len(mesh.faces):,}".replace(",", "."))

    t0 = time.perf_counter()
    poly = _to_polydata(mesh)
    pl = pv.Plotter(off_screen=True, window_size=(ancho, alto))
    pl.add_mesh(poly, color=(0.91, 0.76, 0.72), smooth_shading=True)
    pl.reset_camera()
    t1 = time.perf_counter()
    img = pl.screenshot(return_img=True)   # primer dibujo real (render() no dibuja antes)
    t2 = time.perf_counter()
    res.add(f"Preparacion para visualizar (conversion + normales): {t1 - t0:.2f} s")
    res.add(f"Primer dibujo: {t2 - t1:.2f} s")

    try:
        info = pl.ren_win.ReportCapabilities()
        gpu = next((ln.split(":", 1)[1].strip() for ln in info.splitlines()
                    if "renderer string" in ln.lower()), "desconocida")
    except Exception:
        gpu = "desconocida"
    res.add(f"GPU usada por VTK: {gpu}")

    res.render_valido = bool(img is not None and img.size and float(np.std(img)) > 0)
    if not res.render_valido:
        res.add("ADVERTENCIA: el render no produjo imagen; la medicion de FPS NO es valida.")

    tiempos = []
    for _ in range(frames):
        pl.camera.Azimuth(360.0 / frames)  # método VTK (incremental)
        a = time.perf_counter()
        pl.render()
        _esperar_gpu(pl)
        tiempos.append(time.perf_counter() - a)
    pl.close()
    mediana = statistics.median(tiempos)
    p95 = sorted(tiempos)[int(0.95 * (len(tiempos) - 1))]
    res.fps = 1.0 / mediana if mediana > 0 else float("inf")
    res.add(f"Rotacion 360 grados en {frames} cuadros a {ancho}x{alto} (offscreen):")
    res.add(f"  FPS (mediana): {res.fps:.1f}   | cuadro lento p95: {p95 * 1000:.1f} ms "
            f"(= {1 / p95 if p95 > 0 else float('inf'):.1f} FPS)")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("archivo", nargs="?", help="Malla STL/PLY/OBJ de una arcada")
    ap.add_argument("--sintetico", type=int, metavar="TRIANGULOS",
                    help="Medir con una malla sintética de este tamaño")
    ap.add_argument("--cuadros", type=int, default=180)
    ap.add_argument("--ancho", type=int, default=1600)
    ap.add_argument("--alto", type=int, default=1000)
    ap.add_argument("--mostrar-cabecera", action="store_true",
                    help="Mostrar en pantalla (no en el reporte) el texto de la cabecera STL")
    ap.add_argument("--salida", type=Path, default=ROOT / "rendimiento_ac10.txt")
    args = ap.parse_args(argv)
    if not args.archivo and not args.sintetico:
        ap.error("indique un archivo o --sintetico N")

    from ortosetup.core.mesh_io import check_geometry, load_mesh

    res = Resultado()
    res.add("MEDICION DE RENDIMIENTO - OrtoSetup (AC10)")
    res.add(f"Fecha: {time.strftime('%d-%m-%Y %H:%M')}")
    res.add(f"Sistema: {platform.platform()} | CPUs: {os.cpu_count()}")

    if args.archivo:
        path = Path(args.archivo)
        cab = inspeccionar_cabecera_stl(path)
        res.add(f"Origen: archivo {path.suffix.lower()} de {path.stat().st_size / 2**20:.1f} MB "
                "(nombre y ruta omitidos a proposito)")
        if cab.tipo != "no_stl":
            res.add(f"Cabecera STL ({cab.tipo}): "
                    + ("CONTIENE TEXTO (revisar desidentificacion)" if cab.tiene_texto
                       else "sin texto"))
        t0 = time.perf_counter()
        mesh = load_mesh(path)
        t1 = time.perf_counter()
        rep = check_geometry(mesh, "arch")
        t2 = time.perf_counter()
        res.carga_s = t1 - t0
        res.add(f"Lectura del archivo: {t1 - t0:.2f} s | diagnostico geometrico: {t2 - t1:.2f} s")
        n_adv = len(rep.warnings) if hasattr(rep, "warnings") else len(rep.get("warnings", []))
        res.add(f"Advertencias geometricas: {n_adv}")
    else:
        mesh = malla_sintetica(args.sintetico)
        res.add(f"Origen: malla sintetica (~{args.sintetico:,} triangulos pedidos)".replace(",", "."))

    medir(mesh, res, args.cuadros, args.ancho, args.alto)
    mem = memoria_maxima_mb()
    res.add(f"Memoria maxima del proceso: {mem:.0f} MB" if mem else "Memoria maxima: no disponible")

    res.add("")
    if res.render_valido:
        res.add(f"Meta FPS >= {META_FPS:.0f}: " + ("CUMPLE" if res.fps >= META_FPS else "NO CUMPLE"))
    else:
        res.add(f"Meta FPS >= {META_FPS:.0f}: NO EVALUABLE (render sin imagen)")
    if res.carga_s is not None:
        res.add(f"Meta carga < {META_CARGA_S:.0f} s por arcada: "
                + ("CUMPLE" if res.carga_s < META_CARGA_S else "NO CUMPLE"))
    res.add("Nota: el FPS offscreen es una medida objetiva y repetible; la fluidez en la "
            "ventana interactiva debe confirmarse a ojo.")

    texto = "\n".join(res.lineas)
    print(texto)
    if args.archivo and args.mostrar_cabecera and cab.tiene_texto:
        print(f"\n[Solo en pantalla] Texto de la cabecera STL: {cab.texto!r}")
    args.salida.write_text(texto + "\n", encoding="utf-8")
    print(f"\nReporte guardado en {args.salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
