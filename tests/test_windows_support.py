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
                       capture_output=True, text=True, encoding="utf-8", timeout=120)
    assert r.returncode == 0, r.stderr
    report = (ROOT / "reporte_entorno.txt").read_text(encoding="utf-8")
    assert "Python:" in report and "ADVERTENCIAS" in report


def test_windows_scripts_are_ascii():
    # PowerShell 5.1 interpreta mal UTF-8 sin BOM; cmd.exe tampoco maneja bien acentos.
    for f in list(ROOT.glob("*.bat")) + list((ROOT / "scripts" / "windows").glob("*.ps1")):
        f.read_bytes().decode("ascii")
