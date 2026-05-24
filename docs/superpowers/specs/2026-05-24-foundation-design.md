# Foundation Design — urdf_validator v0.1

**Date:** 2026-05-24
**Milestone:** Month 1 / v0.1
**Status:** Approved

## Objectives

1. Establish `pyproject.toml` with entry point, core deps, and optional extras so `pip install -e .` makes `urdf_validate` callable.
2. Create the full package directory tree with `__init__.py` and stub files matching the PRD module structure.
3. Wire `Confidence` type into every physics-adjacent dataclass field now — retrofitting it later is harder and it is a hard NFR.

## Package Layout

```
urdf_validator/                        ← repo / project root
├── pyproject.toml
├── urdf_validator_main/               ← Python package
│   ├── __init__.py
│   ├── cli.py
│   ├── parser/
│   │   ├── __init__.py
│   │   ├── urdf_adapter.py
│   │   └── xacro_handler.py
│   ├── checks/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   ├── statics.py
│   │   ├── stability.py
│   │   └── workspace.py
│   ├── physics/
│   │   ├── __init__.py
│   │   ├── geometry_physics.py
│   │   └── chain_walker.py
│   ├── report/
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── formatter.py
│   │   └── json_export.py
│   └── integrations/
│       ├── __init__.py
│       └── mujoco_wrapper.py
└── tests/
    └── sample_urdf/
```

**Why `urdf_validator_main` not `urdf_validator`:** The repo root directory is already named `urdf_validator`. Nesting a same-named Python package inside it creates import ambiguity and confusing tracebacks. `urdf_validator_main` eliminates the collision.

**Why `report/models.py` not `report/dataclasses.py`:** `dataclasses` is a Python stdlib module name. A file named `dataclasses.py` inside the package shadows it, causing `from dataclasses import dataclass` to fail anywhere in the process.

## pyproject.toml

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "urdf-validator"
version = "0.1.0"
requires-python = ">=3.8"
dependencies = [
    "urdf_parser_py",
    "numpy",
    "shapely",
]

[project.optional-dependencies]
full = ["ikpy", "xacro"]
mujoco = ["mujoco"]

[project.scripts]
urdf_validate = "urdf_validator_main.cli:main"
```

`ikpy` and `xacro` are grouped under `[full]` because both are used together for extended analysis. `mujoco` is isolated in its own extra because it has a separate license and must never be a hard import.

## report/models.py — Confidence Type and Dataclass Skeletons

```python
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Literal, Optional

Confidence = Literal["exact", "estimated", "guessed", "missing"]
```

Every value derived from physical measurement or geometry estimation carries a paired `_confidence: Confidence` field defaulting to `"missing"`. Structural fields (names, counts, boolean flags from schema checks) carry no confidence tag.

### Dataclasses

**`LinkPhysicsReport`** — per-link physics data:
- `mass`, `mass_confidence`
- `inertia_tensor` (`[ixx, iyy, izz, ixy, ixz, iyz]`), `inertia_confidence`
- `com_offset` (`[x, y, z]` relative to link frame), `com_confidence`

**`JointStaticsReport`** — per-joint gravity torque result:
- `required_torque_gravity`, `torque_confidence`
- `declared_effort`, `margin`
- `status`: `"PASS" | "WARN" | "FAIL" | "UNKNOWN"`

**`StaticsReport`** — full-body statics:
- `joints: List[JointStaticsReport]`
- `full_body_com`, `com_confidence`
- `total_mass`, `mass_confidence`
- `status`

**`StabilityReport`** — support polygon and COM projection:
- `stable`, `margin_mm`, `tip_direction`
- `com_height_ratio`, `com_height_ratio_confidence`
- `status`

**`WorkspaceReport`** — reach metrics:
- `max_reach`, `reach_confidence`
- `vertical_reach`, `horizontal_reach`
- `status`

**`SchemaReport`** — Phase 1 structural checks:
- `status`
- `critical_issues`, `warnings`, `infos` (all `List[str]`)

**`ValidationReport`** — top-level container:
- Metadata: `urdf_path`, `robot_name`, `robot_type`, `timestamp`, `validator_version`
- Phase reports: `schema`, `links`, `statics`, `stability`, `workspace`
- `overall_status`, `critical_issues`, `warnings`
- `unknowns: List[str]` — things the tool explicitly cannot assess (mimic joints, non-standard geometry, etc.)
- `confidence_level: str` — `"HIGH" | "MEDIUM" | "LOW"` aggregate

## cli.py Stub

```python
import sys

def main() -> None:
    print("urdf_validate: not yet implemented")
    sys.exit(0)
```

Sufficient for `pip install -e .` to register the command and confirm the entry point resolves.

## All Other Stubs

Minimal `pass`-body functions/classes. No logic, no `raise NotImplementedError`, no docstrings. Purpose is to make all imports resolve cleanly before any phase is implemented.

| File | Stub |
|---|---|
| `parser/urdf_adapter.py` | `class URDFAdapter: pass` |
| `parser/xacro_handler.py` | `def preprocess(path: str) -> str: pass` |
| `checks/schema.py` | `def run(report) -> None: pass` |
| `checks/statics.py` | `def run(report) -> None: pass` |
| `checks/stability.py` | `def run(report) -> None: pass` |
| `checks/workspace.py` | `def run(report) -> None: pass` |
| `physics/geometry_physics.py` | `def estimate_inertia(link) -> None: pass` |
| `physics/chain_walker.py` | `def walk(robot) -> None: pass` |
| `report/formatter.py` | `def format_report(report) -> str: pass` |
| `report/json_export.py` | `def export(report, path: str) -> None: pass` |
| `integrations/mujoco_wrapper.py` | `def run_deep(report) -> None: pass` |

All `__init__.py` files are empty.

## Decisions Log

| Decision | Choice | Reason |
|---|---|---|
| Inner package name | `urdf_validator_main` | Avoids name collision with repo root dir |
| Report models file | `report/models.py` | `dataclasses.py` shadows stdlib |
| Confidence type | `Literal["exact","estimated","guessed","missing"]` | Zero runtime overhead, clean JSON serialisation, works 3.8–3.12 |
| CLI stub behaviour | Print message, exit 0 | Enough to verify entry point wiring |
| Stub bodies | `pass` only | No forward scaffolding for future phases |
| Optional extras | `[full]` = ikpy+xacro, `[mujoco]` = mujoco | mujoco isolated per license and lazy-import requirement |
