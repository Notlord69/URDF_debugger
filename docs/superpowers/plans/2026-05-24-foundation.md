# Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
>
> **CLAUDE.md constraint:** Maximum 3 subagents per session. Group tasks accordingly.

**Goal:** Stand up the `urdf_validator_main` Python package with `pyproject.toml`, full directory tree, stub modules, and `report/models.py` dataclasses — confirmed installable and importable.

**Architecture:** Single `urdf_validator_main` package at repo root with five sub-packages (`parser`, `checks`, `physics`, `report`, `integrations`). All modules are stubs with `pass`-body functions/classes except `report/models.py` which fully defines all dataclasses with `Confidence` fields, and `cli.py` which prints a message and exits 0.

**Tech Stack:** Python 3.8+, setuptools >=68, pytest (dev), urdf_parser_py, numpy, shapely (declared, not yet used)

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `pyproject.toml` | Package metadata, entry point, deps |
| Create | `urdf_validator_main/__init__.py` | Top-level package marker |
| Create | `urdf_validator_main/cli.py` | Entry point for `urdf_validate` command |
| Create | `urdf_validator_main/parser/__init__.py` | Sub-package marker |
| Create | `urdf_validator_main/parser/urdf_adapter.py` | Stub: `class URDFAdapter` |
| Create | `urdf_validator_main/parser/xacro_handler.py` | Stub: `def preprocess` |
| Create | `urdf_validator_main/checks/__init__.py` | Sub-package marker |
| Create | `urdf_validator_main/checks/schema.py` | Stub: `def run` |
| Create | `urdf_validator_main/checks/statics.py` | Stub: `def run` |
| Create | `urdf_validator_main/checks/stability.py` | Stub: `def run` |
| Create | `urdf_validator_main/checks/workspace.py` | Stub: `def run` |
| Create | `urdf_validator_main/physics/__init__.py` | Sub-package marker |
| Create | `urdf_validator_main/physics/geometry_physics.py` | Stub: `def estimate_inertia` |
| Create | `urdf_validator_main/physics/chain_walker.py` | Stub: `def walk` |
| Create | `urdf_validator_main/report/__init__.py` | Sub-package marker |
| Create | `urdf_validator_main/report/models.py` | All dataclasses + `Confidence` type |
| Create | `urdf_validator_main/report/formatter.py` | Stub: `def format_report` |
| Create | `urdf_validator_main/report/json_export.py` | Stub: `def export` |
| Create | `urdf_validator_main/integrations/__init__.py` | Sub-package marker |
| Create | `urdf_validator_main/integrations/mujoco_wrapper.py` | Stub: `def run_deep` |
| Create | `tests/__init__.py` | Test package marker |
| Create | `tests/test_cli.py` | CLI entry point test |
| Create | `tests/test_imports.py` | Import-surface test for all stubs |
| Create | `tests/test_models.py` | Dataclass defaults + Confidence field test |
| Create | `tests/test_install.py` | Subprocess: `urdf_validate` exits 0 |

---

### Task 1: Create `pyproject.toml` and install the package

**Files:**
- Create: `pyproject.toml`

- [ ] **Step 1: Write the failing install test**

Create `tests/__init__.py` (empty) and `tests/test_install.py`:

```python
import subprocess

def test_urdf_validate_command_exits_zero():
    result = subprocess.run(
        ["urdf_validate"], capture_output=True, text=True
    )
    assert result.returncode == 0, (
        f"urdf_validate exited {result.returncode}\n"
        f"stdout: {result.stdout}\n"
        f"stderr: {result.stderr}"
    )

def test_urdf_validate_prints_something():
    result = subprocess.run(
        ["urdf_validate"], capture_output=True, text=True
    )
    assert result.stdout.strip() != ""
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
cd /home/notlord/ros2_ws/urdf_validator
pip install pytest --quiet
pytest tests/test_install.py -v
```

Expected: `FAILED` — `urdf_validate: command not found` or `FileNotFoundError`.

- [ ] **Step 3: Create `pyproject.toml`**

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
dev = ["pytest"]

[project.scripts]
urdf_validate = "urdf_validator_main.cli:main"

[tool.setuptools.packages.find]
where = ["."]
include = ["urdf_validator_main*"]
```

- [ ] **Step 4: Create the minimal package and cli needed for install to succeed**

Create `urdf_validator_main/__init__.py` (empty file).

Create `urdf_validator_main/cli.py`:

```python
import sys


def main() -> None:
    print("urdf_validate: not yet implemented")
    sys.exit(0)
```

- [ ] **Step 5: Install the package in editable mode**

```bash
pip install -e ".[dev]" --quiet
```

Expected: `Successfully installed urdf-validator-0.1.0`

- [ ] **Step 6: Run test to confirm it passes**

```bash
pytest tests/test_install.py -v
```

Expected:
```
PASSED tests/test_install.py::test_urdf_validate_command_exits_zero
PASSED tests/test_install.py::test_urdf_validate_prints_something
```

- [ ] **Step 7: Commit**

```bash
git add pyproject.toml urdf_validator_main/__init__.py urdf_validator_main/cli.py tests/__init__.py tests/test_install.py
git commit -m "feat: add pyproject.toml and cli stub — urdf_validate command wired"
```

---

### Task 2: Create the CLI unit test and verify `cli.main()` directly

**Files:**
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write the failing CLI unit test**

Create `tests/test_cli.py`:

```python
import pytest
from urdf_validator_main.cli import main


def test_main_exits_zero(capsys):
    with pytest.raises(SystemExit) as exc_info:
        main()
    assert exc_info.value.code == 0


def test_main_prints_not_implemented(capsys):
    with pytest.raises(SystemExit):
        main()
    captured = capsys.readouterr()
    assert "urdf_validate" in captured.out
```

- [ ] **Step 2: Run test to confirm it passes immediately** (cli.py already exists from Task 1)

```bash
pytest tests/test_cli.py -v
```

Expected:
```
PASSED tests/test_cli.py::test_main_exits_zero
PASSED tests/test_cli.py::test_main_prints_not_implemented
```

- [ ] **Step 3: Commit**

```bash
git add tests/test_cli.py
git commit -m "test: add CLI unit test"
```

---

### Task 3: Create all sub-package `__init__.py` files and write import tests

**Files:**
- Create: `urdf_validator_main/parser/__init__.py`
- Create: `urdf_validator_main/checks/__init__.py`
- Create: `urdf_validator_main/physics/__init__.py`
- Create: `urdf_validator_main/report/__init__.py`
- Create: `urdf_validator_main/integrations/__init__.py`
- Create: `tests/test_imports.py`

- [ ] **Step 1: Write the failing import test**

Create `tests/test_imports.py`:

```python
def test_top_level_package_importable():
    import urdf_validator_main  # noqa: F401


def test_parser_subpackage_importable():
    from urdf_validator_main import parser  # noqa: F401


def test_checks_subpackage_importable():
    from urdf_validator_main import checks  # noqa: F401


def test_physics_subpackage_importable():
    from urdf_validator_main import physics  # noqa: F401


def test_report_subpackage_importable():
    from urdf_validator_main import report  # noqa: F401


def test_integrations_subpackage_importable():
    from urdf_validator_main import integrations  # noqa: F401
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
pytest tests/test_imports.py -v
```

Expected: `ModuleNotFoundError: No module named 'urdf_validator_main.parser'` (and similar for the others).

- [ ] **Step 3: Create all five sub-package `__init__.py` files**

Create the following as empty files:
- `urdf_validator_main/parser/__init__.py`
- `urdf_validator_main/checks/__init__.py`
- `urdf_validator_main/physics/__init__.py`
- `urdf_validator_main/report/__init__.py`
- `urdf_validator_main/integrations/__init__.py`

- [ ] **Step 4: Run test to confirm it passes**

```bash
pytest tests/test_imports.py -v
```

Expected: all 6 tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add urdf_validator_main/parser/__init__.py urdf_validator_main/checks/__init__.py urdf_validator_main/physics/__init__.py urdf_validator_main/report/__init__.py urdf_validator_main/integrations/__init__.py tests/test_imports.py
git commit -m "feat: add sub-package __init__.py files — all subpackages importable"
```

---

### Task 4: Create `report/models.py` with `Confidence` type and all dataclasses

**Files:**
- Create: `urdf_validator_main/report/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write the failing models test**

Create `tests/test_models.py`:

```python
from urdf_validator_main.report.models import (
    LinkPhysicsReport,
    JointStaticsReport,
    StaticsReport,
    StabilityReport,
    WorkspaceReport,
    SchemaReport,
    ValidationReport,
)


def test_link_physics_report_defaults():
    r = LinkPhysicsReport(name="base_link")
    assert r.name == "base_link"
    assert r.mass is None
    assert r.mass_confidence == "missing"
    assert r.inertia_tensor is None
    assert r.inertia_confidence == "missing"
    assert r.com_offset is None
    assert r.com_confidence == "missing"


def test_link_physics_report_accepts_confidence_values():
    for val in ("exact", "estimated", "guessed", "missing"):
        r = LinkPhysicsReport(name="link", mass=1.0, mass_confidence=val)
        assert r.mass_confidence == val


def test_joint_statics_report_defaults():
    r = JointStaticsReport(name="shoulder_lift_joint")
    assert r.name == "shoulder_lift_joint"
    assert r.required_torque_gravity is None
    assert r.torque_confidence == "missing"
    assert r.declared_effort is None
    assert r.margin is None
    assert r.status == "UNKNOWN"


def test_statics_report_defaults():
    r = StaticsReport()
    assert r.joints == []
    assert r.full_body_com is None
    assert r.com_confidence == "missing"
    assert r.total_mass is None
    assert r.mass_confidence == "missing"
    assert r.status == "UNKNOWN"


def test_statics_report_joints_are_independent():
    r1 = StaticsReport()
    r2 = StaticsReport()
    r1.joints.append(JointStaticsReport(name="j1"))
    assert r2.joints == [], "mutable default must not be shared between instances"


def test_stability_report_defaults():
    r = StabilityReport()
    assert r.stable is None
    assert r.margin_mm is None
    assert r.tip_direction is None
    assert r.com_height_ratio is None
    assert r.com_height_ratio_confidence == "missing"
    assert r.status == "UNKNOWN"


def test_workspace_report_defaults():
    r = WorkspaceReport()
    assert r.max_reach is None
    assert r.reach_confidence == "missing"
    assert r.vertical_reach is None
    assert r.horizontal_reach is None
    assert r.status == "UNKNOWN"


def test_schema_report_defaults():
    r = SchemaReport()
    assert r.status == "UNKNOWN"
    assert r.critical_issues == []
    assert r.warnings == []
    assert r.infos == []


def test_schema_report_lists_are_independent():
    r1 = SchemaReport()
    r2 = SchemaReport()
    r1.critical_issues.append("broken ref")
    assert r2.critical_issues == [], "mutable default must not be shared between instances"


def test_validation_report_defaults():
    r = ValidationReport()
    assert r.urdf_path == ""
    assert r.robot_name == ""
    assert r.robot_type == "unknown"
    assert r.timestamp == ""
    assert r.validator_version == "0.1.0"
    assert r.overall_status == "UNKNOWN"
    assert r.unknowns == []
    assert r.confidence_level == "LOW"


def test_validation_report_contains_all_phase_reports():
    r = ValidationReport()
    assert isinstance(r.schema, SchemaReport)
    assert isinstance(r.links, list)
    assert isinstance(r.statics, StaticsReport)
    assert isinstance(r.stability, StabilityReport)
    assert isinstance(r.workspace, WorkspaceReport)


def test_validation_report_lists_are_independent():
    r1 = ValidationReport()
    r2 = ValidationReport()
    r1.unknowns.append("mimic joint")
    assert r2.unknowns == [], "mutable default must not be shared between instances"
```

- [ ] **Step 2: Run test to confirm it fails**

```bash
pytest tests/test_models.py -v
```

Expected: `ModuleNotFoundError: No module named 'urdf_validator_main.report.models'`

- [ ] **Step 3: Create `urdf_validator_main/report/models.py`**

```python
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional

Confidence = Literal["exact", "estimated", "guessed", "missing"]


@dataclass
class LinkPhysicsReport:
    name: str
    mass: Optional[float] = None
    mass_confidence: Confidence = "missing"
    inertia_tensor: Optional[List[float]] = None
    inertia_confidence: Confidence = "missing"
    com_offset: Optional[List[float]] = None
    com_confidence: Confidence = "missing"


@dataclass
class JointStaticsReport:
    name: str
    required_torque_gravity: Optional[float] = None
    torque_confidence: Confidence = "missing"
    declared_effort: Optional[float] = None
    margin: Optional[float] = None
    status: str = "UNKNOWN"


@dataclass
class StaticsReport:
    joints: List[JointStaticsReport] = field(default_factory=list)
    full_body_com: Optional[List[float]] = None
    com_confidence: Confidence = "missing"
    total_mass: Optional[float] = None
    mass_confidence: Confidence = "missing"
    status: str = "UNKNOWN"


@dataclass
class StabilityReport:
    stable: Optional[bool] = None
    margin_mm: Optional[float] = None
    tip_direction: Optional[str] = None
    com_height_ratio: Optional[float] = None
    com_height_ratio_confidence: Confidence = "missing"
    status: str = "UNKNOWN"


@dataclass
class WorkspaceReport:
    max_reach: Optional[float] = None
    reach_confidence: Confidence = "missing"
    vertical_reach: Optional[float] = None
    horizontal_reach: Optional[float] = None
    status: str = "UNKNOWN"


@dataclass
class SchemaReport:
    status: str = "UNKNOWN"
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    infos: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    urdf_path: str = ""
    robot_name: str = ""
    robot_type: str = "unknown"
    timestamp: str = ""
    validator_version: str = "0.1.0"
    schema: SchemaReport = field(default_factory=SchemaReport)
    links: List[LinkPhysicsReport] = field(default_factory=list)
    statics: StaticsReport = field(default_factory=StaticsReport)
    stability: StabilityReport = field(default_factory=StabilityReport)
    workspace: WorkspaceReport = field(default_factory=WorkspaceReport)
    overall_status: str = "UNKNOWN"
    critical_issues: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    unknowns: List[str] = field(default_factory=list)
    confidence_level: str = "LOW"
```

- [ ] **Step 4: Run test to confirm it passes**

```bash
pytest tests/test_models.py -v
```

Expected: all 13 tests `PASSED`.

- [ ] **Step 5: Commit**

```bash
git add urdf_validator_main/report/models.py tests/test_models.py
git commit -m "feat: add report/models.py with Confidence type and all dataclass skeletons"
```

---

### Task 5: Create all remaining stub modules and extend import tests

**Files:**
- Create: `urdf_validator_main/parser/urdf_adapter.py`
- Create: `urdf_validator_main/parser/xacro_handler.py`
- Create: `urdf_validator_main/checks/schema.py`
- Create: `urdf_validator_main/checks/statics.py`
- Create: `urdf_validator_main/checks/stability.py`
- Create: `urdf_validator_main/checks/workspace.py`
- Create: `urdf_validator_main/physics/geometry_physics.py`
- Create: `urdf_validator_main/physics/chain_walker.py`
- Create: `urdf_validator_main/report/formatter.py`
- Create: `urdf_validator_main/report/json_export.py`
- Create: `urdf_validator_main/integrations/mujoco_wrapper.py`
- Modify: `tests/test_imports.py`

- [ ] **Step 1: Extend `tests/test_imports.py` with stub symbol tests**

Replace the entire contents of `tests/test_imports.py` with:

```python
def test_top_level_package_importable():
    import urdf_validator_main  # noqa: F401


def test_parser_subpackage_importable():
    from urdf_validator_main import parser  # noqa: F401


def test_checks_subpackage_importable():
    from urdf_validator_main import checks  # noqa: F401


def test_physics_subpackage_importable():
    from urdf_validator_main import physics  # noqa: F401


def test_report_subpackage_importable():
    from urdf_validator_main import report  # noqa: F401


def test_integrations_subpackage_importable():
    from urdf_validator_main import integrations  # noqa: F401


def test_parser_urdf_adapter_stub():
    from urdf_validator_main.parser import urdf_adapter
    assert hasattr(urdf_adapter, "URDFAdapter")


def test_parser_xacro_handler_stub():
    from urdf_validator_main.parser import xacro_handler
    assert hasattr(xacro_handler, "preprocess")


def test_checks_schema_stub():
    from urdf_validator_main.checks import schema
    assert hasattr(schema, "run")


def test_checks_statics_stub():
    from urdf_validator_main.checks import statics
    assert hasattr(statics, "run")


def test_checks_stability_stub():
    from urdf_validator_main.checks import stability
    assert hasattr(stability, "run")


def test_checks_workspace_stub():
    from urdf_validator_main.checks import workspace
    assert hasattr(workspace, "run")


def test_physics_geometry_physics_stub():
    from urdf_validator_main.physics import geometry_physics
    assert hasattr(geometry_physics, "estimate_inertia")


def test_physics_chain_walker_stub():
    from urdf_validator_main.physics import chain_walker
    assert hasattr(chain_walker, "walk")


def test_report_formatter_stub():
    from urdf_validator_main.report import formatter
    assert hasattr(formatter, "format_report")


def test_report_json_export_stub():
    from urdf_validator_main.report import json_export
    assert hasattr(json_export, "export")


def test_integrations_mujoco_wrapper_stub():
    from urdf_validator_main.integrations import mujoco_wrapper
    assert hasattr(mujoco_wrapper, "run_deep")
```

- [ ] **Step 2: Run to confirm new tests fail**

```bash
pytest tests/test_imports.py -v
```

Expected: the 6 existing tests pass; the 11 new stub-symbol tests fail with `ModuleNotFoundError`.

- [ ] **Step 3: Create `urdf_validator_main/parser/urdf_adapter.py`**

```python
class URDFAdapter:
    pass
```

- [ ] **Step 4: Create `urdf_validator_main/parser/xacro_handler.py`**

```python
def preprocess(path: str) -> str:
    pass
```

- [ ] **Step 5: Create `urdf_validator_main/checks/schema.py`**

```python
def run(report) -> None:
    pass
```

- [ ] **Step 6: Create `urdf_validator_main/checks/statics.py`**

```python
def run(report) -> None:
    pass
```

- [ ] **Step 7: Create `urdf_validator_main/checks/stability.py`**

```python
def run(report) -> None:
    pass
```

- [ ] **Step 8: Create `urdf_validator_main/checks/workspace.py`**

```python
def run(report) -> None:
    pass
```

- [ ] **Step 9: Create `urdf_validator_main/physics/geometry_physics.py`**

```python
def estimate_inertia(link) -> None:
    pass
```

- [ ] **Step 10: Create `urdf_validator_main/physics/chain_walker.py`**

```python
def walk(robot) -> None:
    pass
```

- [ ] **Step 11: Create `urdf_validator_main/report/formatter.py`**

```python
def format_report(report) -> str:
    pass
```

- [ ] **Step 12: Create `urdf_validator_main/report/json_export.py`**

```python
def export(report, path: str) -> None:
    pass
```

- [ ] **Step 13: Create `urdf_validator_main/integrations/mujoco_wrapper.py`**

```python
def run_deep(report) -> None:
    pass
```

- [ ] **Step 14: Run full import test suite to confirm all pass**

```bash
pytest tests/test_imports.py -v
```

Expected: all 17 tests `PASSED`.

- [ ] **Step 15: Commit**

```bash
git add \
  urdf_validator_main/parser/urdf_adapter.py \
  urdf_validator_main/parser/xacro_handler.py \
  urdf_validator_main/checks/schema.py \
  urdf_validator_main/checks/statics.py \
  urdf_validator_main/checks/stability.py \
  urdf_validator_main/checks/workspace.py \
  urdf_validator_main/physics/geometry_physics.py \
  urdf_validator_main/physics/chain_walker.py \
  urdf_validator_main/report/formatter.py \
  urdf_validator_main/report/json_export.py \
  urdf_validator_main/integrations/mujoco_wrapper.py \
  tests/test_imports.py
git commit -m "feat: add all stub modules — full import surface established"
```

---

### Task 6: Full test suite run and end-to-end smoke

**Files:** None created — verification only.

- [ ] **Step 1: Run the complete test suite**

```bash
pytest tests/ -v
```

Expected: all tests across `test_install.py`, `test_cli.py`, `test_imports.py`, `test_models.py` pass. Zero failures.

- [ ] **Step 2: Confirm `urdf_validate` command from the shell**

```bash
which urdf_validate
urdf_validate
echo "Exit code: $?"
```

Expected output:
```
/path/to/env/bin/urdf_validate
urdf_validate: not yet implemented
Exit code: 0
```

- [ ] **Step 3: Confirm the full package tree looks correct**

```bash
find urdf_validator_main -type f | sort
```

Expected (21 files):
```
urdf_validator_main/__init__.py
urdf_validator_main/cli.py
urdf_validator_main/checks/__init__.py
urdf_validator_main/checks/schema.py
urdf_validator_main/checks/stability.py
urdf_validator_main/checks/statics.py
urdf_validator_main/checks/workspace.py
urdf_validator_main/integrations/__init__.py
urdf_validator_main/integrations/mujoco_wrapper.py
urdf_validator_main/parser/__init__.py
urdf_validator_main/parser/urdf_adapter.py
urdf_validator_main/parser/xacro_handler.py
urdf_validator_main/physics/__init__.py
urdf_validator_main/physics/chain_walker.py
urdf_validator_main/physics/geometry_physics.py
urdf_validator_main/report/__init__.py
urdf_validator_main/report/formatter.py
urdf_validator_main/report/json_export.py
urdf_validator_main/report/models.py
```

- [ ] **Step 4: Commit the plan doc alongside code if not already committed**

```bash
git add docs/superpowers/plans/2026-05-24-foundation.md
git commit -m "docs: add foundation implementation plan"
```
