"""Puente entre el Project (núcleo) y un plotter de PyVista.

No contiene lógica clínica: solo traduce el estado del proyecto a actores VTK.
La geometría cargada nunca se modifica; la posición de cada diente se aplica
como user_matrix del actor (la misma matriz 4x4 que calcula el núcleo).
Funciona tanto con pyvistaqt.QtInteractor como con pv.Plotter(off_screen=True),
lo que permite probarla sin interfaz gráfica.
"""
from __future__ import annotations

import colorsys

import numpy as np
import pyvista as pv

from ..core.mesh_io import load_mesh
from ..core.project import Project

ARCH_COLOR = {"upper": "#e8c4b8", "lower": "#d9b3a6"}


def tooth_color(fdi: int) -> tuple[float, float, float]:
    """Color determinista y distinguible por diente."""
    q, n = divmod(fdi, 10)
    hue = ((q - 1) % 4 * 0.25 + (n - 1) * 0.031) % 1.0
    return colorsys.hsv_to_rgb(hue, 0.45, 0.95)


def _to_polydata(mesh) -> pv.PolyData:
    faces = np.hstack([np.full((len(mesh.faces), 1), 3), mesh.faces]).astype(np.int64)
    return pv.PolyData(np.asarray(mesh.vertices, dtype=float), faces.ravel())


class Scene:
    def __init__(self, plotter) -> None:
        self.plotter = plotter
        self.project: Project | None = None
        self.arch_actors: dict[str, object] = {}
        self.tooth_actors: dict[int, object] = {}
        self.ghost_actors: dict[int, object] = {}
        self.show_initial = False
        self.selected: int | None = None

    # ------------------------------------------------------------------ carga
    def load_project(self, project: Project) -> None:
        self.clear()
        self.project = project
        for arch_id in project.arches:
            self.add_arch(arch_id)
        for fdi in sorted(project.teeth):
            self.add_tooth(fdi)
        self.plotter.reset_camera()

    def clear(self) -> None:
        self.plotter.clear()
        # plotter.clear() también elimina las luces: sin ellas la malla se ve como
        # una silueta plana, sin relieve (defecto detectado con un escaneo real en
        # AC10). Se restaura la iluminación estándar de PyVista.
        if len(self.plotter.renderer.lights) == 0:
            self.plotter.enable_lightkit()
        self.arch_actors.clear()
        self.tooth_actors.clear()
        self.ghost_actors.clear()
        self.selected = None

    def add_arch(self, arch_id: str) -> None:
        a = self.project.arches[arch_id]
        poly = _to_polydata(load_mesh(self.project.path_of(a.original)))
        self.arch_actors[arch_id] = self.plotter.add_mesh(
            poly, color=ARCH_COLOR[arch_id], smooth_shading=True,
            name=f"arch_{arch_id}", pickable=False,
        )

    def add_tooth(self, fdi: int) -> None:
        t = self.project.teeth[fdi]
        poly = _to_polydata(load_mesh(self.project.path_of(t.original)))
        actor = self.plotter.add_mesh(
            poly, color=tooth_color(fdi), smooth_shading=True, name=f"tooth_{fdi}",
        )
        self.tooth_actors[fdi] = actor
        ghost = self.plotter.add_mesh(
            poly.copy(), color="white", style="wireframe", opacity=0.25,
            name=f"ghost_{fdi}", pickable=False,
        )
        self.ghost_actors[fdi] = ghost
        self.update_tooth(fdi)

    # ------------------------------------------------------------------ estado
    def update_tooth(self, fdi: int) -> None:
        t = self.project.teeth[fdi]
        self.tooth_actors[fdi].user_matrix = t.matrix()
        self.ghost_actors[fdi].SetVisibility(
            bool(self.show_initial and not t.movement.is_identity()
                 and self.tooth_actors[fdi].GetVisibility())
        )

    def update_all(self) -> None:
        for fdi in self.tooth_actors:
            self.update_tooth(fdi)

    def set_show_initial(self, on: bool) -> None:
        self.show_initial = bool(on)
        self.update_all()

    def set_visible(self, key: str | int, visible: bool) -> None:
        actor = self._actor(key)
        actor.SetVisibility(bool(visible))
        if isinstance(key, int):
            self.update_tooth(key)

    def set_opacity(self, key: str | int, opacity: float) -> None:
        self._actor(key).GetProperty().SetOpacity(float(np.clip(opacity, 0.0, 1.0)))

    def select(self, fdi: int | None) -> None:
        if self.selected in self.tooth_actors:
            p = self.tooth_actors[self.selected].GetProperty()
            p.SetColor(tooth_color(self.selected))
            p.SetAmbient(0.0)
        self.selected = fdi
        if fdi in self.tooth_actors:
            p = self.tooth_actors[fdi].GetProperty()
            p.SetColor(1.0, 0.85, 0.2)
            p.SetAmbient(0.25)

    def _actor(self, key: str | int):
        return self.tooth_actors[key] if isinstance(key, int) else self.arch_actors[key]

    # ------------------------------------------------------------------ vistas
    # Las vistas son RELATIVAS A LOS EJES DEL ARCHIVO. Sin landmarks (Fase 3)
    # el programa no conoce la orientación anatómica del escaneo.
    def view(self, name: str) -> None:
        p = self.plotter
        {"oclusal": p.view_xy, "frontal": p.view_xz, "lateral": p.view_yz,
         "perspectiva": p.view_isometric}[name]()
        p.reset_camera()
