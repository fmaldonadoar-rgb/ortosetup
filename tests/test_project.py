"""Pruebas de aceptación de la Fase 1 (núcleo, sin interfaz)."""
import json

import numpy as np
import pytest

from ortosetup.core.history import History
from ortosetup.core.mesh_io import load_mesh, sha256_file
from ortosetup.core.project import Project, ProjectIntegrityError
from ortosetup.core.transforms import Movement6DOF, apply_matrix


def build(tmp_path, case):
    p = Project.create(tmp_path / "Caso")
    p.import_arch(case / "upper_arch.stl", "upper")
    p.import_arch(case / "lower_arch.stl", "lower")
    for f in sorted((case / "teeth").glob("*.stl")):
        p.import_tooth(f, int(f.stem))
    p.save()
    return p


def test_AC1_import_preserves_originals_byte_exact(tmp_path, synthetic_case):
    p = build(tmp_path, synthetic_case)
    assert set(p.arches) == {"upper", "lower"} and len(p.teeth) == 28
    for arch_id, name in (("upper", "upper_arch.stl"), ("lower", "lower_arch.stl")):
        stored = p.path_of(p.arches[arch_id].original)
        assert stored.read_bytes() == (synthetic_case / name).read_bytes()
    assert (synthetic_case / "upper_arch.stl").exists()  # la fuente no se toca


def test_AC2_movement_roundtrip_is_bit_exact(tmp_path, synthetic_case):
    p = build(tmp_path, synthetic_case)
    mv = Movement6DOF(0.25, -0.1, 0.3, 7.5, -3.0, 4.2)
    p.set_movement(11, mv)
    m_before = p.teeth[11].matrix()
    p.save()
    q = Project.load(p.root)
    assert q.teeth[11].movement == mv
    assert np.array_equal(q.teeth[11].matrix(), m_before)  # igualdad bit a bit
    assert q.teeth[21].movement.is_identity()


def test_AC3_moved_tooth_keeps_its_shape(tmp_path, synthetic_case):
    p = build(tmp_path, synthetic_case)
    p.set_movement(36, Movement6DOF(1, 1, -0.5, 20, 5, -10))
    mesh = load_mesh(p.path_of(p.teeth[36].original))
    v0 = mesh.vertices[:300]
    v1 = apply_matrix(v0, p.teeth[36].matrix())
    d0 = np.linalg.norm(v0[:, None] - v0[None], axis=-1)
    d1 = np.linalg.norm(v1[:, None] - v1[None], axis=-1)
    assert np.max(np.abs(d0 - d1)) < 1e-9
    # el archivo original sigue intacto
    assert sha256_file(p.path_of(p.teeth[36].original)) == p.teeth[36].original.sha256


def test_AC4_tampered_original_is_detected(tmp_path, synthetic_case):
    p = build(tmp_path, synthetic_case)
    target = p.path_of(p.teeth[11].original)
    data = bytearray(target.read_bytes())
    data[-5] ^= 0xFF
    target.write_bytes(bytes(data))
    with pytest.raises(ProjectIntegrityError):
        Project.load(p.root)


def test_AC5_missing_original_is_detected(tmp_path, synthetic_case):
    p = build(tmp_path, synthetic_case)
    p.path_of(p.arches["lower"].original).unlink()
    with pytest.raises(ProjectIntegrityError):
        Project.load(p.root)


def test_duplicate_and_invalid_teeth_rejected(tmp_path, synthetic_case):
    p = build(tmp_path, synthetic_case)
    with pytest.raises(ValueError):
        p.import_tooth(synthetic_case / "teeth" / "11.stl", 11)
    with pytest.raises(ValueError):
        p.import_tooth(synthetic_case / "teeth" / "11.stl", 19)
    with pytest.raises(ValueError):
        p.import_arch(synthetic_case / "upper_arch.stl", "upper")


def test_locked_tooth_cannot_move(tmp_path, synthetic_case):
    p = build(tmp_path, synthetic_case)
    p.set_locked(16, True)
    with pytest.raises(PermissionError):
        p.set_movement(16, Movement6DOF(md_mm=1))
    p.save()
    assert Project.load(p.root).teeth[16].locked


def test_undo_redo(tmp_path, synthetic_case):
    p = build(tmp_path, synthetic_case)
    h = History(p)
    a, b = Movement6DOF(md_mm=1), Movement6DOF(md_mm=1, rot_deg=5)
    h.move(12, a)
    h.move(12, b)
    assert h.undo() == 12 and p.teeth[12].movement == a
    assert h.undo() == 12 and p.teeth[12].movement.is_identity()
    assert h.undo() is None
    assert h.redo() == 12 and p.teeth[12].movement == a
    h.move(13, Movement6DOF(vl_mm=0.5))
    assert not h.can_redo()  # una acción nueva invalida el rehacer


def test_audit_log_records_actions(tmp_path, synthetic_case):
    p = build(tmp_path, synthetic_case)
    p.set_movement(11, Movement6DOF(md_mm=0.5))
    actions = [e["action"] for e in p.read_audit()]
    assert actions[0] == "project_created"
    assert actions.count("import_tooth") == 28 and "set_movement" in actions
    assert all("software_version" in e for e in p.read_audit())


def test_project_json_is_readable_and_versioned(tmp_path, synthetic_case):
    p = build(tmp_path, synthetic_case)
    d = json.loads((p.root / "project.json").read_text(encoding="utf-8"))
    assert d["schema_version"] == 1 and d["units"] == "mm"
    assert d["bite_registered"] is False
    assert d["teeth"]["11"]["frame"]["source"].startswith("provisional")


def test_import_rejects_bad_file_without_copying(tmp_path):
    p = Project.create(tmp_path / "C")
    bad = tmp_path / "roto.stl"
    bad.write_bytes(b"solid x\nendsolid x\n")
    with pytest.raises(Exception):
        p.import_arch(bad, "upper")
    assert not list((p.root / "originals").glob("upper__*"))
