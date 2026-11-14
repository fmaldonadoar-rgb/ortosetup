"""Pruebas de la capa visual (sin pantalla: render offscreen)."""
import os

import numpy as np
import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pv = pytest.importorskip("pyvista")

from ortosetup.app.scene import Scene  # noqa: E402
from ortosetup.core.project import Project  # noqa: E402
from ortosetup.core.transforms import Movement6DOF  # noqa: E402


@pytest.fixture
def project(tmp_path, synthetic_case):
    p = Project.create(tmp_path / "C")
    p.import_arch(synthetic_case / "upper_arch.stl", "upper")
    for f in sorted((synthetic_case / "teeth").glob("1*.stl")):
        p.import_tooth(f, int(f.stem))
    p.save()
    return p


def test_scene_actor_matrix_matches_core(project):
    pl = pv.Plotter(off_screen=True)
    sc = Scene(pl)
    sc.load_project(project)
    assert set(sc.tooth_actors) == set(project.teeth)
    project.set_movement(11, Movement6DOF(1.0, 0.5, -0.2, 10, 3, -4))
    sc.update_tooth(11)
    assert np.allclose(np.array(sc.tooth_actors[11].user_matrix), project.teeth[11].matrix())
    img = pl.screenshot(return_img=True)
    assert img.shape[0] > 0 and img.std() > 0  # algo se dibujó
    pl.close()


def test_scene_visibility_opacity_and_ghost(project):
    pl = pv.Plotter(off_screen=True)
    sc = Scene(pl)
    sc.load_project(project)
    sc.set_opacity("upper", 0.3)
    assert sc.arch_actors["upper"].GetProperty().GetOpacity() == pytest.approx(0.3)
    sc.set_visible(12, False)
    assert not sc.tooth_actors[12].GetVisibility()
    project.set_movement(13, Movement6DOF(md_mm=1))
    sc.set_show_initial(True)
    assert sc.ghost_actors[13].GetVisibility()        # movido -> muestra inicial
    assert not sc.ghost_actors[14].GetVisibility()    # no movido -> sin fantasma
    for v in ("oclusal", "frontal", "lateral", "perspectiva"):
        sc.view(v)
    pl.close()


def test_main_window_end_to_end(project):
    qt = pytest.importorskip("PySide6.QtWidgets")
    app = qt.QApplication.instance() or qt.QApplication([])
    from ortosetup.app.main_window import MainWindow

    w = MainWindow(plotter_factory=lambda parent: pv.Plotter(off_screen=True))
    # QtInteractor no está disponible sin OpenGL; usamos un plotter offscreen
    # embebido mediante un contenedor mínimo.
    w.open_project(str(project.root))
    assert w.project is not None and len(w.scene.tooth_actors) == len(project.teeth)
    # seleccionar diente 11 en el árbol
    teeth_root = w.tree.topLevelItem(w.tree.topLevelItemCount() - 1)
    item = next(teeth_root.child(i) for i in range(teeth_root.childCount())
                if teeth_root.child(i).text(0) == "11")
    w.tree.setCurrentItem(item)
    assert w.current_fdi() == 11
    w.spins["md_mm"].setValue(0.75)
    w.spins["torque_deg"].setValue(-6.5)
    w.apply_movement()
    assert w.project.teeth[11].movement.md_mm == 0.75
    w.undo()
    assert w.project.teeth[11].movement.is_identity()
    w.redo()
    w.save_project()
    reopened = Project.load(project.root)
    assert reopened.teeth[11].movement == Movement6DOF(md_mm=0.75, torque_deg=-6.5)
    w.dirty = False
    w.close()


CLINICAL_TERMS = ("torque", "angulaci", "tip", "rotación eje", "rotación axial",
                  "mesiodistal", "vestibulolingual", "inclinaci", "extrusi", "intrusi")


def test_movement_labels_are_cartesian_while_axes_are_provisional():
    """Defecto O2 (AC9) y prompt maestro §8.3: sin ejes aprobados no hay nombres clínicos."""
    pytest.importorskip("PySide6.QtWidgets")
    from ortosetup.app import main_window as mw

    texts = [label for _, label, *_ in mw.MOVE_FIELDS] + [mw.MOVE_GROUP_TITLE]
    for text in texts:
        low = text.lower()
        assert not any(term in low for term in CLINICAL_TERMS), text
    assert "movimiento cartesiano (ejes del archivo)" in mw.MOVE_GROUP_TITLE.lower()
    # las claves internas (formato del proyecto, esquema 1) no cambian
    assert [k for k, *_ in mw.MOVE_FIELDS] == ["md_mm", "vl_mm", "oc_mm",
                                               "rot_deg", "tip_deg", "torque_deg"]


def test_frame_source_shown_in_plain_language():
    """Defecto O4 (AC9): no mostrar identificadores internos al usuario."""
    pytest.importorskip("PySide6.QtWidgets")
    from ortosetup.app.main_window import frame_source_label

    label = frame_source_label("provisional_world_axes_centroid")
    assert "_" not in label and "provisional" in label
    assert frame_source_label("otro_origen") == "otro_origen"


def test_tree_name_column_stretches_for_hidpi(project):
    """Defecto O1 (AC9): el FDI no debe truncarse a '...' con escalado de pantalla."""
    qt = pytest.importorskip("PySide6.QtWidgets")
    app = qt.QApplication.instance() or qt.QApplication([])
    from PySide6.QtCore import Qt
    from ortosetup.app.main_window import MainWindow

    w = MainWindow(plotter_factory=lambda parent: pv.Plotter(off_screen=True))
    header = w.tree.header()
    assert header.sectionResizeMode(0) == qt.QHeaderView.Stretch
    assert header.sectionResizeMode(1) == qt.QHeaderView.ResizeToContents
    assert not header.stretchLastSection()
    assert w.tree.textElideMode() == Qt.ElideNone
    w.open_project(str(project.root))
    w.resize(1400, 850)
    w.show()
    app.processEvents()
    teeth_root = w.tree.topLevelItem(w.tree.topLevelItemCount() - 1)
    needed = max(w.tree.sizeHintForColumn(0), 1)
    assert w.tree.columnWidth(0) >= needed
    assert teeth_root.childCount() == len(project.teeth)
    w.dirty = False
    w.close()
