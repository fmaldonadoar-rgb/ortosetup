"""Deshacer / rehacer de movimientos dentarios (patrón comando, sin dependencias de UI)."""
from __future__ import annotations

from dataclasses import dataclass

from .project import Project
from .transforms import Movement6DOF


@dataclass(frozen=True)
class MoveCommand:
    fdi: int
    before: Movement6DOF
    after: Movement6DOF


class History:
    def __init__(self, project: Project) -> None:
        self.project = project
        self._undo: list[MoveCommand] = []
        self._redo: list[MoveCommand] = []

    def move(self, fdi: int, movement: Movement6DOF) -> None:
        before = self.project.teeth[fdi].movement
        if before == movement:
            return
        self.project.set_movement(fdi, movement)
        self._undo.append(MoveCommand(fdi, before, movement))
        self._redo.clear()

    def reset(self, fdi: int) -> None:
        self.move(fdi, Movement6DOF())

    def can_undo(self) -> bool:
        return bool(self._undo)

    def can_redo(self) -> bool:
        return bool(self._redo)

    def undo(self) -> int | None:
        if not self._undo:
            return None
        cmd = self._undo.pop()
        self.project.set_movement(cmd.fdi, cmd.before, origin="undo")
        self._redo.append(cmd)
        return cmd.fdi

    def redo(self) -> int | None:
        if not self._redo:
            return None
        cmd = self._redo.pop()
        self.project.set_movement(cmd.fdi, cmd.after, origin="redo")
        self._undo.append(cmd)
        return cmd.fdi
