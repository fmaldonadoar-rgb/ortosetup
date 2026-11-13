"""Ventana principal (Fase 1). Solo expone funciones implementadas."""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDoubleSpinBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPlainTextEdit,
    QPushButton,
    QSlider,
    QSplitter,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from .. import __version__
from ..core.fdi import fdi_from_filename, validate_fdi
from ..core.history import History
from ..core.project import Project
from ..core.transforms import Movement6DOF
from .scene import Scene

MESH_FILTER = "Mallas 3D (*.stl *.ply *.obj)"
ARCH_LABEL = {"upper": "Arcada superior", "lower": "Arcada inferior"}

# (campo, etiqueta, unidad, rango, paso)
MOVE_FIELDS = [
    ("md_mm", "Mesiodistal (x, + mesial)", " mm", 20.0, 0.1),
    ("vl_mm", "Vestibulolingual (y, + vestibular)", " mm", 20.0, 0.1),
    ("oc_mm", "Extrusión(+)/intrusión(−) (z)", " mm", 20.0, 0.1),
    ("rot_deg", "Rotación eje largo (z)", " °", 180.0, 0.5),
    ("tip_deg", "Angulación (sobre y)", " °", 180.0, 0.5),
    ("torque_deg", "Torque/inclinación (sobre x)", " °", 180.0, 0.5),
]


class MainWindow(QMainWindow):
    def __init__(self, plotter_factory=None) -> None:
        super().__init__()
        self.setWindowTitle(f"OrtoSetup {__version__} — EXPERIMENTAL, no apto para uso clínico")
        self.resize(1400, 850)
        self.project: Project | None = None
        self.history: History | None = None
        self.dirty = False

        if plotter_factory is None:
            from pyvistaqt import QtInteractor
            plotter_factory = QtInteractor
        self.plotter = plotter_factory(self)
        self.scene = Scene(self.plotter)
        self._build_ui()
        self._refresh_enabled()

    # ================================================================== UI
    def _build_ui(self) -> None:
        tb = QToolBar("Principal")
        self.addToolBar(tb)

        def act(text, slot, shortcut=None):
            a = QAction(text, self)
            a.triggered.connect(slot)
            if shortcut:
                a.setShortcut(QKeySequence(shortcut))
            tb.addAction(a)
            return a

        act("Nuevo proyecto", self.new_project, "Ctrl+N")
        act("Abrir", self.open_project, "Ctrl+O")
        self.a_save = act("Guardar", self.save_project, "Ctrl+S")
        tb.addSeparator()
        self.a_up = act("Importar arcada sup.", lambda: self.import_arch("upper"))
        self.a_lo = act("Importar arcada inf.", lambda: self.import_arch("lower"))
        self.a_teeth = act("Importar dientes segmentados", self.import_teeth)
        tb.addSeparator()
        self.a_undo = act("Deshacer", self.undo, "Ctrl+Z")
        self.a_redo = act("Rehacer", self.redo, "Ctrl+Y")
        tb.addSeparator()
        for v in ("oclusal", "frontal", "lateral", "perspectiva"):
            act(v.capitalize(), lambda _=False, v=v: self.scene.view(v))

        # ---------------- panel izquierdo: estructura
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Modelo", "Bloq."])
        self.tree.itemChanged.connect(self._on_item_changed)
        self.tree.currentItemChanged.connect(self._on_current_changed)
        self.opacity = QSlider(Qt.Horizontal)
        self.opacity.setRange(0, 100)
        self.opacity.setValue(100)
        self.opacity.valueChanged.connect(self._on_opacity)
        left = QWidget()
        lv = QVBoxLayout(left)
        lv.addWidget(QLabel("Arcadas y dientes (casilla = visible)"))
        lv.addWidget(self.tree)
        lv.addWidget(QLabel("Transparencia del elemento seleccionado"))
        lv.addWidget(self.opacity)
        self.cb_initial = QCheckBox("Mostrar posición inicial (malla de alambre)")
        self.cb_initial.toggled.connect(self.scene.set_show_initial)
        self.cb_initial.toggled.connect(lambda _: self.plotter.render())
        lv.addWidget(self.cb_initial)

        # ---------------- panel derecho: movimiento numérico
        right = QWidget()
        rv = QVBoxLayout(right)
        self.lbl_tooth = QLabel("Seleccione un diente")
        self.lbl_tooth.setStyleSheet("font-weight: bold; font-size: 14px")
        rv.addWidget(self.lbl_tooth)
        box = QGroupBox("Movimiento respecto de la posición inicial (6 GDL)")
        form = QFormLayout(box)
        self.spins: dict[str, QDoubleSpinBox] = {}
        for key, label, unit, rng, step in MOVE_FIELDS:
            s = QDoubleSpinBox()
            s.setRange(-rng, rng)
            s.setDecimals(3)
            s.setSingleStep(step)
            s.setSuffix(unit)
            s.setKeyboardTracking(False)
            form.addRow(label, s)
            self.spins[key] = s
        rv.addWidget(box)
        row = QHBoxLayout()
        self.b_apply = QPushButton("Aplicar")
        self.b_apply.clicked.connect(self.apply_movement)
        self.b_reset = QPushButton("Restaurar posición inicial")
        self.b_reset.clicked.connect(self.reset_tooth)
        row.addWidget(self.b_apply)
        row.addWidget(self.b_reset)
        rv.addLayout(row)
        self.lbl_frame = QLabel()
        self.lbl_frame.setWordWrap(True)
        self.lbl_frame.setStyleSheet("color: #b36b00")
        rv.addWidget(self.lbl_frame)
        note = QLabel(
            "<b>Ejes provisionales (Fase 1):</b> pivote = centroide de la malla del diente; "
            "ejes = ejes del archivo. Los nombres clínicos solo son correctos si el "
            "escaneo está orientado según esa convención. Ver docs/CONVENCIONES_EJES.md.<br>"
            "<i>No disponibles aún:</i> segmentación IA, análisis, setup automático, staging, "
            "exportación, manipuladores 3D por arrastre."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #666")
        rv.addWidget(note)
        rv.addStretch()

        # ---------------- panel inferior: registro
        self.log = QPlainTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumBlockCount(2000)

        center = QSplitter(Qt.Horizontal)
        center.addWidget(left)
        # En pruebas sin pantalla el plotter no es un QWidget: se usa un marcador.
        viewport = self.plotter if isinstance(self.plotter, QWidget) else QLabel("(render offscreen)")
        center.addWidget(viewport)
        center.addWidget(right)
        center.setSizes([280, 800, 340])
        vsplit = QSplitter(Qt.Vertical)
        vsplit.addWidget(center)
        vsplit.addWidget(self.log)
        vsplit.setSizes([700, 140])
        banner = QLabel("  SOFTWARE EXPERIMENTAL DE INVESTIGACIÓN — NO APTO PARA PLANIFICACIÓN "
                        "NI FABRICACIÓN CLÍNICA  ")
        banner.setStyleSheet("background:#7a1f1f;color:white;font-weight:bold;padding:4px")
        banner.setAlignment(Qt.AlignCenter)
        root = QWidget()
        lay = QVBoxLayout(root)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(banner)
        lay.addWidget(vsplit)
        self.setCentralWidget(root)

    # ================================================================== helpers
    def info(self, msg: str) -> None:
        self.log.appendPlainText(msg)
        self.statusBar().showMessage(msg, 6000)

    def error(self, msg: str) -> None:
        self.log.appendPlainText("ERROR: " + msg)
        QMessageBox.critical(self, "Error", msg)

    def _refresh_enabled(self) -> None:
        has = self.project is not None
        for a in (self.a_save, self.a_up, self.a_lo, self.a_teeth):
            a.setEnabled(has)
        self.a_undo.setEnabled(bool(self.history and self.history.can_undo()))
        self.a_redo.setEnabled(bool(self.history and self.history.can_redo()))
        fdi = self.current_fdi()
        movable = fdi is not None and not self.project.teeth[fdi].locked
        for w in [*self.spins.values(), self.b_apply, self.b_reset]:
            w.setEnabled(movable)

    def current_fdi(self) -> int | None:
        item = self.tree.currentItem()
        key = item.data(0, Qt.UserRole) if item else None
        return key if isinstance(key, int) and self.project and key in self.project.teeth else None

    def _rebuild_tree(self) -> None:
        self.tree.blockSignals(True)
        self.tree.clear()
        for arch_id in ("upper", "lower"):
            if arch_id in self.project.arches:
                it = QTreeWidgetItem([ARCH_LABEL[arch_id], ""])
                it.setData(0, Qt.UserRole, arch_id)
                it.setCheckState(0, Qt.Checked)
                self.tree.addTopLevelItem(it)
        teeth_root = QTreeWidgetItem(["Dientes", ""])
        self.tree.addTopLevelItem(teeth_root)
        for fdi in sorted(self.project.teeth):
            t = self.project.teeth[fdi]
            it = QTreeWidgetItem([f"{fdi}", ""])
            it.setData(0, Qt.UserRole, fdi)
            it.setCheckState(0, Qt.Checked)
            it.setCheckState(1, Qt.Checked if t.locked else Qt.Unchecked)
            teeth_root.addChild(it)
        teeth_root.setExpanded(True)
        self.tree.blockSignals(False)

    def _load_into_ui(self, project: Project) -> None:
        self.project = project
        self.history = History(project)
        self.scene.load_project(project)
        self.scene.set_show_initial(self.cb_initial.isChecked())
        self._rebuild_tree()
        self.dirty = False
        self._refresh_enabled()
        self.plotter.render()

    def _show_report_warnings(self, label: str, report: dict) -> None:
        for w in report.get("warnings", []):
            self.info(f"[{label}] Advertencia: {w}")

    # ================================================================== acciones
    def _confirm_discard(self) -> bool:
        if not self.dirty:
            return True
        r = QMessageBox.question(self, "Cambios sin guardar",
                                 "Hay cambios sin guardar. ¿Descartarlos?")
        return r == QMessageBox.Yes

    def new_project(self) -> None:
        if not self._confirm_discard():
            return
        d = QFileDialog.getExistingDirectory(self, "Carpeta vacía para el nuevo proyecto")
        if not d:
            return
        try:
            self._load_into_ui(Project.create(Path(d)))
            self.info(f"Proyecto creado en {d}")
        except Exception as e:
            self.error(str(e))

    def open_project(self, path: str | None = None) -> None:
        if not self._confirm_discard():
            return
        d = path or QFileDialog.getExistingDirectory(self, "Carpeta del proyecto")
        if not d:
            return
        try:
            self._load_into_ui(Project.load(Path(d)))
            self.info(f"Proyecto abierto y verificado (SHA-256): {d}")
        except Exception as e:
            self.error(f"No se pudo abrir el proyecto: {e}")

    def save_project(self) -> None:
        if self.project:
            self.project.save()
            self.dirty = False
            self.info("Proyecto guardado.")

    def import_arch(self, arch_id: str) -> None:
        f, _ = QFileDialog.getOpenFileName(self, ARCH_LABEL[arch_id], "", MESH_FILTER)
        if not f:
            return
        try:
            replace = False
            if arch_id in self.project.arches:
                if QMessageBox.question(self, "Reemplazar", "¿Reemplazar la arcada existente?") \
                        != QMessageBox.Yes:
                    return
                replace = True
            a = self.project.import_arch(Path(f), arch_id, replace=replace)
            self._show_report_warnings(ARCH_LABEL[arch_id], a.geometry_report)
            self.project.save()
            self._load_into_ui(self.project)
            self.info(f"{ARCH_LABEL[arch_id]} importada: {Path(f).name}")
        except Exception as e:
            self.error(str(e))

    def import_teeth(self) -> None:
        files, _ = QFileDialog.getOpenFileNames(
            self, "Mallas de dientes (nombre con código FDI, p. ej. 11.stl)", "", MESH_FILTER)
        if not files:
            return
        added = 0
        for f in files:
            fdi = fdi_from_filename(Path(f))
            if fdi is None:
                code, ok = QInputDialog.getInt(
                    self, "Código FDI", f"No se pudo deducir el FDI de {Path(f).name}.\n"
                    "Ingrese el código FDI:", 11, 11, 85)
                if not ok:
                    continue
                fdi = code
            try:
                validate_fdi(fdi)
                t = self.project.import_tooth(Path(f), fdi)
                self._show_report_warnings(f"Diente {fdi}", t.geometry_report)
                added += 1
            except Exception as e:
                self.info(f"ERROR al importar {Path(f).name}: {e}")
        if added:
            self.project.save()
            self._load_into_ui(self.project)
        self.info(f"{added} diente(s) importado(s).")

    def apply_movement(self) -> None:
        fdi = self.current_fdi()
        if fdi is None:
            return
        mv = Movement6DOF(**{k: s.value() for k, s in self.spins.items()})
        try:
            self.history.move(fdi, mv)
        except PermissionError as e:
            self.error(str(e))
            return
        self._after_move(fdi)

    def reset_tooth(self) -> None:
        fdi = self.current_fdi()
        if fdi is not None:
            self.history.reset(fdi)
            self._after_move(fdi)

    def undo(self) -> None:
        if self.history and (fdi := self.history.undo()) is not None:
            self._after_move(fdi)

    def redo(self) -> None:
        if self.history and (fdi := self.history.redo()) is not None:
            self._after_move(fdi)

    def _after_move(self, fdi: int) -> None:
        self.dirty = True
        self.scene.update_tooth(fdi)
        if fdi == self.current_fdi():
            self._fill_spins(fdi)
        self._refresh_enabled()
        self.plotter.render()
        m = self.project.teeth[fdi].movement
        self.info(f"Diente {fdi}: " + ", ".join(f"{k}={v:g}" for k, v in m.to_dict().items()))

    def _fill_spins(self, fdi: int) -> None:
        d = self.project.teeth[fdi].movement.to_dict()
        for k, s in self.spins.items():
            s.blockSignals(True)
            s.setValue(d[k])
            s.blockSignals(False)

    # ================================================================== señales
    def _on_current_changed(self, cur, _prev) -> None:
        fdi = self.current_fdi()
        self.scene.select(fdi)
        if fdi is not None:
            t = self.project.teeth[fdi]
            self.lbl_tooth.setText(f"Diente {fdi} ({'bloqueado' if t.locked else 'editable'})")
            self._fill_spins(fdi)
            self.lbl_frame.setText(f"Referencia: {t.frame.source}. Pivote (mm): "
                                   + ", ".join(f"{v:.2f}" for v in t.frame.origin))
            key = fdi
        else:
            self.lbl_tooth.setText("Seleccione un diente")
            self.lbl_frame.setText("")
            key = cur.data(0, Qt.UserRole) if cur else None
        if key is not None:
            actor = self.scene._actor(key)
            self.opacity.blockSignals(True)
            self.opacity.setValue(int(round(actor.GetProperty().GetOpacity() * 100)))
            self.opacity.blockSignals(False)
        self._refresh_enabled()
        self.plotter.render()

    def _on_item_changed(self, item, column) -> None:
        key = item.data(0, Qt.UserRole)
        if key is None:
            return
        if column == 0:
            self.scene.set_visible(key, item.checkState(0) == Qt.Checked)
        elif column == 1 and isinstance(key, int):
            self.project.set_locked(key, item.checkState(1) == Qt.Checked)
            self.dirty = True
            self._on_current_changed(self.tree.currentItem(), None)
        self.plotter.render()

    def _on_opacity(self, value: int) -> None:
        item = self.tree.currentItem()
        key = item.data(0, Qt.UserRole) if item else None
        if key is not None:
            self.scene.set_opacity(key, value / 100)
            self.plotter.render()

    def closeEvent(self, event) -> None:
        if self._confirm_discard():
            self.plotter.close()
            event.accept()
        else:
            event.ignore()


def main(argv=None) -> int:
    argv = sys.argv if argv is None else argv
    app = QApplication(argv)
    w = MainWindow()
    w.show()
    if len(argv) > 1:
        w.open_project(argv[1])
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
