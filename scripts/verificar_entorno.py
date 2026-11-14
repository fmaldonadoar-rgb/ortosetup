"""Diagnóstico del entorno de OrtoSetup.

Genera reporte_entorno.txt en la raíz del repositorio. Ese archivo es lo que
debe compartirse con un agente de IA o con soporte para diagnosticar problemas.
No envía nada por internet.

Uso:  python scripts/verificar_entorno.py
"""
from __future__ import annotations

import importlib
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACKAGES = ["numpy", "trimesh", "vtk", "pyvista", "pyvistaqt", "PySide6", "pytest",
            "torch", "open3d"]  # torch/open3d: opcionales (Fase 2+)
OPTIONAL = {"torch", "open3d"}


def run(cmd: list[str], timeout: int = 20) -> tuple[int, str]:
    if shutil.which(cmd[0]) is None:
        return -1, f"(no encontrado: {cmd[0]})"
    try:
        p = subprocess.run(cmd, capture_output=True, timeout=timeout)
        raw = p.stdout or p.stderr
        # wsl.exe escribe UTF-16 en algunas versiones de Windows
        text = raw.decode("utf-16-le", "ignore") if b"\x00" in raw[:20] else raw.decode("utf-8", "ignore")
        return p.returncode, text.strip()
    except Exception as exc:  # timeout, permisos, etc.
        return -2, f"(error: {exc})"


def check_paths(lines: list[str], warnings: list[str]) -> None:
    root = str(ROOT)
    lines.append(f"Ruta del repositorio: {root}")
    if "onedrive" in root.lower():
        warnings.append("El repositorio está dentro de OneDrive: puede bloquear archivos o dejarlos "
                        "solo en la nube. Muévalo, p. ej., a C:\\dev\\ortosetup.")
    if not root.isascii():
        warnings.append("La ruta contiene acentos o caracteres no ASCII; algunas herramientas "
                        "(CUDA, compiladores) fallan con esas rutas. Use p. ej. C:\\dev\\ortosetup.")
    if " " in root:
        warnings.append("La ruta contiene espacios; funciona, pero conviene evitarlo.")
    if len(root) > 80:
        warnings.append("Ruta larga: Windows limita rutas a 260 caracteres salvo que se habiliten "
                        "rutas largas. Use una carpeta corta.")


def check_python(lines: list[str], warnings: list[str]) -> None:
    v = sys.version_info
    lines.append(f"Python: {sys.version.split()[0]} ({platform.architecture()[0]}) en {sys.executable}")
    if (v.major, v.minor) != (3, 12):
        warnings.append(f"Python {v.major}.{v.minor}: la versión recomendada en Windows es 3.12.")
    if platform.architecture()[0] != "64bit":
        warnings.append("Python no es de 64 bits: instale la versión de 64 bits.")
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)
    lines.append(f"Entorno virtual activo: {'sí' if in_venv else 'no'}")


def check_packages(lines: list[str], warnings: list[str]) -> None:
    lines.append("Paquetes:")
    for name in PACKAGES:
        try:
            mod = importlib.import_module(name)
            ver = getattr(mod, "__version__", None) or getattr(mod, "VTK_VERSION", "?")
            extra = ""
            if name == "torch":
                cuda = mod.cuda.is_available()
                extra = f" | CUDA disponible: {cuda}"
                if cuda:
                    extra += f" ({mod.cuda.get_device_name(0)})"
            lines.append(f"  {name}: {ver}{extra}")
        except Exception as exc:
            tag = "opcional, no instalado" if name in OPTIONAL else f"FALTA ({exc.__class__.__name__})"
            lines.append(f"  {name}: {tag}")
            if name not in OPTIONAL:
                warnings.append(f"Falta el paquete obligatorio {name}: ejecute INSTALAR.bat.")


def check_gpu_and_wsl(lines: list[str], warnings: list[str]) -> None:
    code, out = run(["nvidia-smi", "--query-gpu=name,driver_version,memory.total",
                     "--format=csv,noheader"])
    lines.append(f"GPU NVIDIA: {out if code == 0 else 'no detectada ' + out}")
    if code != 0:
        warnings.append("nvidia-smi no responde: instale o actualice el driver NVIDIA "
                        "(necesario a partir de la Fase 2).")
    if platform.system() == "Windows":
        code, out = run(["wsl", "--status"])
        lines.append("WSL --status:\n    " + out.replace("\n", "\n    "))
        if wsl_installed(code, out):
            code, out = run(["wsl", "-l", "-v"])
            lines.append("WSL distribuciones:\n    " + out.replace("\n", "\n    "))
        else:
            # Sin WSL, "wsl -l -v" se queda esperando hasta el timeout (defecto O5, AC9).
            lines.append("WSL distribuciones: (omitido: WSL no está instalado; "
                         "solo se necesita a partir de la Fase 2)")


def wsl_installed(code: int, status_output: str) -> bool:
    """Decide si vale la pena consultar las distribuciones de WSL."""
    text = status_output.lower()
    if code != 0:
        return False
    return not any(s in text for s in ("no está instalado", "no esta instalado",
                                       "not installed", "wsl.exe --install"))


def check_render(lines: list[str], warnings: list[str]) -> None:
    try:
        import pyvista as pv

        pl = pv.Plotter(off_screen=True, window_size=(200, 200))
        pl.add_mesh(pv.Sphere())
        img = pl.screenshot(return_img=True)
        pl.close()
        info = "OK" if img.std() > 0 else "imagen vacía"
        lines.append(f"Render VTK offscreen: {info}")
        if img.std() == 0:
            warnings.append("El render VTK produjo una imagen vacía: revise drivers OpenGL.")
    except Exception as exc:
        lines.append(f"Render VTK offscreen: ERROR {exc}")
        warnings.append("No se pudo renderizar con VTK: revise el driver de video / OpenGL.")


def main() -> int:
    # En Windows la consola usa cp1252/cp850: forzamos UTF-8 para que los acentos
    # se vean bien y no fallen los programas que leen esta salida.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    lines: list[str] = [
        "REPORTE DE ENTORNO - OrtoSetup",
        f"Sistema: {platform.platform()} | Máquina: {platform.machine()}",
        f"Procesador: {platform.processor() or '?'} | CPUs: {os.cpu_count()}",
    ]
    warnings: list[str] = []
    for check in (check_paths, check_python, check_packages, check_gpu_and_wsl, check_render):
        try:
            check(lines, warnings)
        except Exception as exc:
            lines.append(f"[{check.__name__}] error inesperado: {exc}")
    lines.append("")
    lines.append("ADVERTENCIAS:" if warnings else "ADVERTENCIAS: ninguna")
    lines += [f"  - {w}" for w in warnings]
    text = "\n".join(lines)
    print(text)
    (ROOT / "reporte_entorno.txt").write_text(text + "\n", encoding="utf-8")
    print(f"\nReporte guardado en {ROOT / 'reporte_entorno.txt'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
