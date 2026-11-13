import numpy as np
import pytest
import trimesh

from ortosetup.core.fdi import arch_of, fdi_from_filename, validate_fdi
from ortosetup.core.mesh_io import MeshImportError, check_geometry, load_mesh


@pytest.mark.parametrize("ext", ["stl", "ply", "obj"])
def test_load_supported_formats_preserves_vertices(tmp_path, ext):
    src = trimesh.creation.icosphere(subdivisions=2, radius=4.0)
    src.apply_translation((12.5, -3.25, 7.0))
    path = tmp_path / f"t.{ext}"
    src.export(path)
    mesh = load_mesh(path)
    # STL repite vértices por triángulo; comparamos la geometría de los triángulos
    a = np.sort(src.triangles.reshape(-1, 3), axis=0)
    b = np.sort(mesh.triangles.reshape(-1, 3), axis=0)
    tol = 1e-5 if ext == "stl" else 1e-9  # STL guarda float32
    assert np.allclose(a, b, atol=tol)


def test_unsupported_and_empty_files(tmp_path):
    bad = tmp_path / "x.dcm"
    bad.write_bytes(b"abc")
    with pytest.raises(MeshImportError):
        load_mesh(bad)
    empty = tmp_path / "e.stl"
    empty.write_bytes(b"")
    with pytest.raises(MeshImportError):
        load_mesh(empty)
    garbage = tmp_path / "g.ply"
    garbage.write_bytes(b"esto no es un ply")
    with pytest.raises(MeshImportError):
        load_mesh(garbage)


def test_scale_warning_for_meters(synthetic_case):
    mesh = load_mesh(synthetic_case / "upper_arch.stl")
    assert not any("METROS" in w for w in check_geometry(mesh).warnings)
    mesh_m = mesh.copy()
    mesh_m.apply_scale(0.001)
    assert any("METROS" in w for w in check_geometry(mesh_m).warnings)


def test_check_does_not_modify_mesh(synthetic_case):
    mesh = load_mesh(synthetic_case / "upper_arch.stl")
    before = mesh.vertices.copy()
    check_geometry(mesh)
    assert np.array_equal(before, mesh.vertices)


def test_non_finite_is_error():
    m = trimesh.creation.box()
    m.vertices[0] = [np.nan, 0, 0]
    rep = check_geometry(m, kind="tooth")
    assert not rep.ok


def test_open_surface_reported(synthetic_case):
    rep = check_geometry(load_mesh(synthetic_case / "upper_arch.stl"))
    assert rep.n_boundary_edges > 0 and not rep.is_watertight


def test_fdi_rules():
    assert validate_fdi(11) == 11 and validate_fdi(85) == 85
    for bad in (10, 19, 56, 91, 9):
        with pytest.raises(ValueError):
            validate_fdi(bad)
    assert arch_of(26) == "upper" and arch_of(46) == "lower" and arch_of(75) == "lower"
    assert fdi_from_filename("diente_36.stl") == 36
    assert fdi_from_filename("11.ply") == 11
    assert fdi_from_filename("scan_2024.stl") is None
    assert fdi_from_filename("11_21.stl") is None  # ambiguo: no adivina
