"""Modelo de datos y persistencia de proyectos.

Formato en disco (carpeta de proyecto):

    MiCaso/
      project.json        <- estado completo (JSON legible, versionado por schema_version)
      audit.jsonl         <- registro de auditoría append-only (una línea JSON por acción)
      originals/          <- copias byte a byte de los archivos importados (nunca se modifican)
        upper__<archivo original>
        lower__<archivo original>
        teeth/11__<archivo original> ...

La geometría nunca se reescribe: la posición de cada diente se guarda como un
movimiento de 6 GDL (ver transforms.py) aplicado sobre la malla original.
Al abrir un proyecto se verifica el SHA-256 de cada original.
"""
from __future__ import annotations

import json
import os
import shutil
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

from .. import __version__
from .fdi import arch_of, validate_fdi
from .mesh_io import (
    area_weighted_centroid,
    check_geometry,
    detect_format,
    load_mesh,
    sha256_file,
)
from .transforms import Movement6DOF, ToothFrame, world_matrix

SCHEMA_VERSION = 1
PROJECT_FILE = "project.json"
AUDIT_FILE = "audit.jsonl"
ARCH_IDS = ("upper", "lower")


class ProjectIntegrityError(Exception):
    pass


def _replace_with_retry(src: Path, dest: Path, attempts: int = 10, delay_s: float = 0.2) -> None:
    """os.replace con reintentos: en Windows el antivirus, OneDrive o un visor
    pueden tener el archivo abierto un instante y provocar PermissionError."""
    for i in range(attempts):
        try:
            os.replace(src, dest)
            return
        except PermissionError:
            if i == attempts - 1:
                raise PermissionError(
                    f"No se pudo escribir {dest.name}: otro programa lo tiene abierto "
                    "(antivirus, OneDrive, editor). Ciérrelo e intente de nuevo."
                ) from None
            time.sleep(delay_s)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


@dataclass
class OriginalFile:
    rel_path: str
    sha256: str
    format: str
    size_bytes: int
    source_name: str

    def to_dict(self) -> dict:
        return dict(self.__dict__)

    @classmethod
    def from_dict(cls, d: dict) -> "OriginalFile":
        return cls(**d)


@dataclass
class ArchModel:
    arch_id: str
    original: OriginalFile
    geometry_report: dict
    imported_at: str

    def to_dict(self) -> dict:
        return {
            "arch_id": self.arch_id,
            "original": self.original.to_dict(),
            "geometry_report": self.geometry_report,
            "imported_at": self.imported_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ArchModel":
        return cls(
            arch_id=d["arch_id"],
            original=OriginalFile.from_dict(d["original"]),
            geometry_report=d["geometry_report"],
            imported_at=d["imported_at"],
        )


@dataclass
class Tooth:
    fdi: int
    arch_id: str
    original: OriginalFile
    frame: ToothFrame
    movement: Movement6DOF = field(default_factory=Movement6DOF)
    locked: bool = False
    geometry_report: dict = field(default_factory=dict)

    def matrix(self):
        return world_matrix(self.frame, self.movement)

    def to_dict(self) -> dict:
        return {
            "fdi": self.fdi,
            "arch_id": self.arch_id,
            "original": self.original.to_dict(),
            "frame": self.frame.to_dict(),
            "movement": self.movement.to_dict(),
            "locked": self.locked,
            "geometry_report": self.geometry_report,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Tooth":
        return cls(
            fdi=validate_fdi(d["fdi"]),
            arch_id=d["arch_id"],
            original=OriginalFile.from_dict(d["original"]),
            frame=ToothFrame.from_dict(d["frame"]),
            movement=Movement6DOF.from_dict(d["movement"]),
            locked=bool(d.get("locked", False)),
            geometry_report=d.get("geometry_report", {}),
        )


@dataclass
class Project:
    root: Path
    name: str
    created_at: str
    units: str = "mm"
    arches: dict[str, ArchModel] = field(default_factory=dict)
    teeth: dict[int, Tooth] = field(default_factory=dict)
    bite_registered: bool = False  # Fase 1: nunca se asume oclusión registrada
    notes: str = ""

    # ------------------------------------------------------------------ creación
    @classmethod
    def create(cls, root: Path, name: str | None = None) -> "Project":
        root = Path(root)
        if (root / PROJECT_FILE).exists():
            raise FileExistsError(f"Ya existe un proyecto en {root}")
        (root / "originals" / "teeth").mkdir(parents=True, exist_ok=True)
        p = cls(root=root, name=name or root.name, created_at=_now())
        p.audit("project_created", {"name": p.name})
        p.save()
        return p

    # ------------------------------------------------------------------ auditoría
    def audit(self, action: str, details: dict | None = None) -> None:
        entry = {
            "ts": _now(),
            "software_version": __version__,
            "schema_version": SCHEMA_VERSION,
            "action": action,
            "details": details or {},
        }
        self.root.mkdir(parents=True, exist_ok=True)
        with open(self.root / AUDIT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def read_audit(self) -> list[dict]:
        path = self.root / AUDIT_FILE
        if not path.exists():
            return []
        with open(path, encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]

    # ------------------------------------------------------------------ importación
    def _store_original(self, src: Path, rel_dir: str, prefix: str) -> OriginalFile:
        src = Path(src)
        fmt = detect_format(src)
        dest_rel = Path(rel_dir) / f"{prefix}__{src.name}"
        dest = self.root / dest_rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        src_hash = sha256_file(src)
        shutil.copyfile(src, dest)
        if sha256_file(dest) != src_hash:
            dest.unlink(missing_ok=True)
            raise ProjectIntegrityError(f"La copia de {src.name} no coincide con el original")
        return OriginalFile(
            rel_path=dest_rel.as_posix(),
            sha256=src_hash,
            format=fmt,
            size_bytes=dest.stat().st_size,
            source_name=src.name,
        )

    def import_arch(self, src: Path, arch_id: str, replace: bool = False) -> ArchModel:
        if arch_id not in ARCH_IDS:
            raise ValueError(f"arch_id debe ser uno de {ARCH_IDS}")
        if arch_id in self.arches and not replace:
            raise ValueError(f"La arcada '{arch_id}' ya fue importada")
        mesh = load_mesh(src)  # valida legibilidad ANTES de copiar
        report = check_geometry(mesh, kind="arch")
        if not report.ok:
            raise ValueError(f"Malla rechazada: {'; '.join(report.errors)}")
        original = self._store_original(src, "originals", arch_id)
        arch = ArchModel(arch_id, original, report.to_dict(), _now())
        self.arches[arch_id] = arch
        self.audit("import_arch", {"arch_id": arch_id, "source": original.source_name,
                                   "sha256": original.sha256,
                                   "warnings": report.warnings})
        return arch

    def import_tooth(self, src: Path, fdi: int, frame: ToothFrame | None = None) -> Tooth:
        fdi = validate_fdi(fdi)
        if fdi in self.teeth:
            raise ValueError(f"El diente {fdi} ya existe en el proyecto")
        mesh = load_mesh(src)
        report = check_geometry(mesh, kind="tooth")
        if not report.ok:
            raise ValueError(f"Malla rechazada: {'; '.join(report.errors)}")
        if frame is None:
            c = area_weighted_centroid(mesh)
            frame = ToothFrame(origin=tuple(float(x) for x in c),
                               source="provisional_world_axes_centroid")
        original = self._store_original(src, "originals/teeth", str(fdi))
        tooth = Tooth(fdi=fdi, arch_id=arch_of(fdi), original=original,
                      frame=frame, geometry_report=report.to_dict())
        self.teeth[fdi] = tooth
        self.audit("import_tooth", {"fdi": fdi, "source": original.source_name,
                                    "sha256": original.sha256,
                                    "frame_source": frame.source,
                                    "warnings": report.warnings})
        return tooth

    # ------------------------------------------------------------------ movimientos
    def set_movement(self, fdi: int, movement: Movement6DOF, origin: str = "manual") -> None:
        tooth = self.teeth[validate_fdi(fdi)]
        if tooth.locked:
            raise PermissionError(f"El diente {fdi} está bloqueado")
        old = tooth.movement
        tooth.movement = movement
        self.audit("set_movement", {"fdi": fdi, "origin": origin,
                                    "from": old.to_dict(), "to": movement.to_dict()})

    def set_locked(self, fdi: int, locked: bool) -> None:
        self.teeth[validate_fdi(fdi)].locked = bool(locked)
        self.audit("set_locked", {"fdi": fdi, "locked": bool(locked)})

    def path_of(self, original: OriginalFile) -> Path:
        return self.root / original.rel_path

    # ------------------------------------------------------------------ persistencia
    def to_dict(self) -> dict:
        return {
            "schema_version": SCHEMA_VERSION,
            "software_version": __version__,
            "name": self.name,
            "created_at": self.created_at,
            "saved_at": _now(),
            "units": self.units,
            "bite_registered": self.bite_registered,
            "notes": self.notes,
            "arches": {k: a.to_dict() for k, a in self.arches.items()},
            "teeth": {str(k): t.to_dict() for k, t in sorted(self.teeth.items())},
        }

    def save(self) -> Path:
        """Escritura atómica: se escribe a un temporal y se reemplaza."""
        data = json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
        fd, tmp = tempfile.mkstemp(dir=self.root, prefix=".project.", suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            _replace_with_retry(Path(tmp), self.root / PROJECT_FILE)
        except BaseException:
            Path(tmp).unlink(missing_ok=True)
            raise
        self.audit("project_saved", {"n_teeth": len(self.teeth),
                                     "arches": sorted(self.arches)})
        return self.root / PROJECT_FILE

    @classmethod
    def load(cls, root: Path, verify: bool = True) -> "Project":
        root = Path(root)
        with open(root / PROJECT_FILE, encoding="utf-8") as f:
            d = json.load(f)
        if d.get("schema_version") != SCHEMA_VERSION:
            raise ProjectIntegrityError(
                f"schema_version {d.get('schema_version')} no soportada (esperada {SCHEMA_VERSION})"
            )
        if d.get("units") != "mm":
            raise ProjectIntegrityError(f"Unidad no soportada: {d.get('units')}")
        p = cls(
            root=root,
            name=d["name"],
            created_at=d["created_at"],
            units=d["units"],
            bite_registered=bool(d.get("bite_registered", False)),
            notes=d.get("notes", ""),
            arches={k: ArchModel.from_dict(v) for k, v in d["arches"].items()},
            teeth={int(k): Tooth.from_dict(v) for k, v in d["teeth"].items()},
        )
        if verify:
            p.verify_originals()
        p.audit("project_opened", {"software_version_saved": d.get("software_version")})
        return p

    def verify_originals(self) -> None:
        originals = [a.original for a in self.arches.values()] + [
            t.original for t in self.teeth.values()
        ]
        problems = []
        for o in originals:
            path = self.path_of(o)
            if not path.exists():
                problems.append(f"falta {o.rel_path}")
            elif sha256_file(path) != o.sha256:
                problems.append(f"{o.rel_path} fue modificado (SHA-256 distinto)")
        if problems:
            raise ProjectIntegrityError("Integridad comprometida: " + "; ".join(problems))
