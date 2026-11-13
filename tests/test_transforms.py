import numpy as np
import pytest

from ortosetup.core.transforms import (
    Movement6DOF,
    ToothFrame,
    apply_matrix,
    is_rigid,
    world_matrix,
)


def oblique_frame():
    # Sistema local girado 30° sobre z y desplazado: evita que las pruebas
    # pasen solo porque los ejes coinciden con los del mundo.
    a = np.deg2rad(30)
    x = (np.cos(a), np.sin(a), 0.0)
    y = (-np.sin(a), np.cos(a), 0.0)
    z = (0.0, 0.0, 1.0)
    return ToothFrame(origin=(10.0, 5.0, -3.0), axes=(x, y, z), source="test")


def test_identity_movement_gives_identity_matrix():
    m = world_matrix(oblique_frame(), Movement6DOF())
    assert np.allclose(m, np.eye(4), atol=1e-12)


def test_translation_follows_local_axes():
    f = oblique_frame()
    m = world_matrix(f, Movement6DOF(md_mm=2.0))
    moved = apply_matrix(np.array([f.origin]), m)[0]
    expected = np.array(f.origin) + 2.0 * np.array(f.axes[0])
    assert np.allclose(moved, expected, atol=1e-12)


def test_extrusion_is_positive_along_long_axis():
    f = oblique_frame()
    m = world_matrix(f, Movement6DOF(oc_mm=1.5))
    assert np.allclose(m[:3, 3], 1.5 * np.array(f.axes[2]), atol=1e-12)


@pytest.mark.parametrize("field", ["rot_deg", "tip_deg", "torque_deg"])
def test_rotation_pivots_on_frame_origin(field):
    f = oblique_frame()
    m = world_matrix(f, Movement6DOF(**{field: 17.0}))
    assert np.allclose(apply_matrix(np.array([f.origin]), m)[0], f.origin, atol=1e-12)


def test_rotation_axes_follow_convention():
    f = oblique_frame()
    # rot (eje largo z) deja fijo el eje z; tip deja fijo y; torque deja fijo x
    for field, axis_idx in (("rot_deg", 2), ("tip_deg", 1), ("torque_deg", 0)):
        m = world_matrix(f, Movement6DOF(**{field: 25.0}))
        axis = np.array(f.axes[axis_idx])
        assert np.allclose(m[:3, :3] @ axis, axis, atol=1e-12), field


def test_right_hand_rule_for_rotation():
    f = ToothFrame(origin=(0.0, 0.0, 0.0))
    m = world_matrix(f, Movement6DOF(rot_deg=90.0))
    # +90° sobre z lleva x -> y
    assert np.allclose(m[:3, :3] @ [1, 0, 0], [0, 1, 0], atol=1e-12)


def test_composition_order_is_T_Rz_Ry_Rx():
    f = ToothFrame(origin=(0.0, 0.0, 0.0))
    mv = Movement6DOF(md_mm=1, vl_mm=2, oc_mm=3, rot_deg=10, tip_deg=20, torque_deg=30)
    a, b, c = np.deg2rad([10, 20, 30])
    rz = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    ry = np.array([[np.cos(b), 0, np.sin(b)], [0, 1, 0], [-np.sin(b), 0, np.cos(b)]])
    rx = np.array([[1, 0, 0], [0, np.cos(c), -np.sin(c)], [0, np.sin(c), np.cos(c)]])
    m = world_matrix(f, mv)
    assert np.allclose(m[:3, :3], rz @ ry @ rx, atol=1e-12)
    assert np.allclose(m[:3, 3], [1, 2, 3], atol=1e-12)


def test_result_is_rigid_and_preserves_shape():
    rng = np.random.default_rng(0)
    pts = rng.normal(size=(200, 3)) * 5
    m = world_matrix(oblique_frame(), Movement6DOF(2, -1, 0.5, 12, -7, 15))
    assert is_rigid(m)
    moved = apply_matrix(pts, m)
    d0 = np.linalg.norm(pts[:, None] - pts[None], axis=-1)
    d1 = np.linalg.norm(moved[:, None] - moved[None], axis=-1)
    assert np.max(np.abs(d0 - d1)) < 1e-10  # sin deformación


def test_invalid_inputs_are_rejected():
    with pytest.raises(ValueError):
        Movement6DOF(md_mm=float("nan"))
    with pytest.raises(ValueError):
        ToothFrame(origin=(0, 0, 0), axes=((1, 0, 0), (1, 0, 0), (0, 0, 1)))
    with pytest.raises(ValueError):  # sistema levógiro
        ToothFrame(origin=(0, 0, 0), axes=((1, 0, 0), (0, 1, 0), (0, 0, -1)))


def test_dict_roundtrip_is_bit_exact():
    mv = Movement6DOF(0.1, 0.2, 0.30000000000000004, 1 / 3, -2 / 7, 1e-17)
    assert Movement6DOF.from_dict(mv.to_dict()) == mv
    f = oblique_frame()
    assert ToothFrame.from_dict(f.to_dict()) == f
