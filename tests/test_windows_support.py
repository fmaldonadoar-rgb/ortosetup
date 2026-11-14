"""Pruebas de soporte de plataforma (corren en Linux y Windows)."""
import subprocess
import sys
from pathlib import Path

import pytest

from ortosetup.core import project as project_mod
from ortosetup.core.project import Project
from ortosetup.core.transforms import Movement6DOF

ROOT = Path(__file__).resolve().parents[1]


def test_paths_with_spaces_and_accents(tmp_path, synthetic_case):
    root = tmp_path / "Caso clínico Peñaloza"
    p = Project.create(root)
    p.import_tooth(synthetic_case / "teeth" / "11.stl", 11)
    p.set_movement(11, Movement6DOF(md_mm=0.5))
    p.save()
    assert Project.load(root).teeth[11].movement.md_mm == 0.5


def test_save_retries_when_file_is_locked(tmp_path, monkeypatch):
    p = Project.create(tmp_path / "C")
    real = project_mod.os.replace
    calls = {"n": 0}

    def flaky(src, dst):
        calls["n"] += 1
        if calls["n"] < 3:
            raise PermissionError("bloqueado")
        return real(src, dst)

    monkeypatch.setattr(project_mod.os, "replace", flaky)
    monkeypatch.setattr(project_mod.time, "sleep", lambda s: None)
    p.save()
    assert calls["n"] == 3


def test_save_gives_clear_error_when_permanently_locked(tmp_path, monkeypatch):
    p = Project.create(tmp_path / "C")

    def always_locked(src, dst):
        raise PermissionError("bloqueado")

    monkeypatch.setattr(project_mod.os, "replace", always_locked)
    monkeypatch.setattr(project_mod.time, "sleep", lambda s: None)
    with pytest.raises(PermissionError, match="otro programa"):
        p.save()
    assert not list(p.root.glob(".project.*.tmp"))  # sin temporales huérfanos


def test_environment_report_runs(tmp_path):
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "verificar_entorno.py")],
                       capture_output=True, text=True, encoding="utf-8", errors="strict", timeout=120)
    assert r.returncode == 0, r.stderr
    report = (ROOT / "reporte_entorno.txt").read_text(encoding="utf-8")
    assert "Python:" in report and "ADVERTENCIAS" in report


def test_windows_scripts_are_ascii():
    # PowerShell 5.1 interpreta mal UTF-8 sin BOM; cmd.exe tampoco maneja bien acentos.
    for f in list(ROOT.glob("*.bat")) + list((ROOT / "scripts" / "windows").glob("*.ps1")):
        f.read_bytes().decode("ascii")


def _load_verificar_entorno():
    import importlib.util
    spec = importlib.util.spec_from_file_location("verificar_entorno",
                                                  ROOT / "scripts" / "verificar_entorno.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_wsl_not_installed_skips_distribution_query():
    """Defecto O5 (AC9): sin WSL no se consulta 'wsl -l -v' (esperaba 20 s)."""
    ve = _load_verificar_entorno()
    msg_es = ('El Subsistema de Windows para Linux no está instalado. '
              'Para instalar, ejecute "wsl.exe --install".')
    assert not ve.wsl_installed(0, msg_es)
    assert not ve.wsl_installed(1, msg_es)
    assert not ve.wsl_installed(-1, "(no encontrado: wsl)")
    assert ve.wsl_installed(0, "Distribución predeterminada: Ubuntu\nVersión predeterminada: 2")


def _load_medir():
    import importlib.util
    spec = importlib.util.spec_from_file_location("medir_rendimiento",
                                                  ROOT / "scripts" / "medir_rendimiento.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # necesario para los dataclasses del script
    spec.loader.exec_module(mod)
    return mod


def test_stl_header_inspection_detects_text(tmp_path):
    """AC10: la cabecera de un STL binario puede traer texto (p. ej., un nombre)."""
    m = _load_medir()
    tri = b"\x00" * 50
    con_texto = tmp_path / "a.stl"
    con_texto.write_bytes(b"Paciente Ejemplo Escaner X".ljust(80, b"\x00")
                          + (1).to_bytes(4, "little") + tri)
    sin_texto = tmp_path / "b.stl"
    sin_texto.write_bytes(b"\x00" * 80 + (1).to_bytes(4, "little") + tri)
    ascii_stl = tmp_path / "c.stl"
    ascii_stl.write_text("solid NombrePaciente\nendsolid\n", encoding="utf-8")
    assert m.inspeccionar_cabecera_stl(con_texto).tipo == "binario"
    assert "Paciente Ejemplo" in m.inspeccionar_cabecera_stl(con_texto).texto
    assert not m.inspeccionar_cabecera_stl(sin_texto).tiene_texto
    c = m.inspeccionar_cabecera_stl(ascii_stl)
    assert c.tipo == "ascii" and c.texto == "NombrePaciente"


def test_performance_report_has_no_identifying_data(tmp_path):
    """AC10 / §18: el reporte no incluye nombre, ruta ni texto de la cabecera."""
    pytest.importorskip("pyvista")
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    m = _load_medir()
    mesh = m.malla_sintetica(5000)
    assert 4000 < len(mesh.faces) < 6000
    secreto = tmp_path / "Juan Perez Rut 12345678.stl"
    mesh.export(secreto)
    data = bytearray(secreto.read_bytes())
    data[:80] = b"Juan Perez".ljust(80, b" ")
    secreto.write_bytes(bytes(data))
    salida = tmp_path / "reporte.txt"
    assert m.main([str(secreto), "--cuadros", "4", "--ancho", "320", "--alto", "240",
                   "--mostrar-cabecera", "--salida", str(salida)]) == 0
    texto = salida.read_text(encoding="utf-8")
    assert "Juan" not in texto and "Perez" not in texto and "12345678" not in texto
    assert str(tmp_path) not in texto
    assert "CONTIENE TEXTO" in texto and "Triangulos:" in texto and "FPS" in texto
