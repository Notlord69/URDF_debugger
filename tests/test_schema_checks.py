import os

import numpy as np
import pytest

from urdf_validator_main.checks import schema
from urdf_validator_main.parser.urdf_adapter import (
    ParsedJoint,
    ParsedLink,
    ParsedRobot,
    load_urdf,
)
from urdf_validator_main.report.models import ValidationReport

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_urdf")


# ---------------------------------------------------------------------------
# Test-local helpers — build minimal ParsedRobot without touching any files
# ---------------------------------------------------------------------------

def _make_link(
    name: str,
    mass: float = 1.0,
    joint_type_incoming: str = "revolute",
    inertia: np.ndarray = None,
) -> ParsedLink:
    """Build a non-fixed link with physics-valid defaults."""
    if inertia is None:
        inertia = np.diag([0.1, 0.1, 0.1])
    return ParsedLink(
        name=name,
        mass=mass,
        inertia_3x3=inertia,
        joint_type_incoming=joint_type_incoming,
        visual_geometry_type=None,
        collision_geometry_type=None,
    )


def _make_joint(
    name: str,
    parent: str,
    child: str,
    joint_type: str = "revolute",
) -> ParsedJoint:
    return ParsedJoint(
        name=name,
        joint_type=joint_type,
        parent=parent,
        child=child,
        limit_lower=-1.0,
        limit_upper=1.0,
        limit_effort=10.0,
        limit_velocity=1.0,
    )


def _run(robot: ParsedRobot) -> ValidationReport:
    """Run schema checks and return the populated report."""
    report = ValidationReport()
    schema.run(robot, report)
    return report


# ---------------------------------------------------------------------------
# Clean robot — the golden path
# ---------------------------------------------------------------------------

def test_clean_robot_schema_passes():
    robot = ParsedRobot(
        name="clean_robot",
        links=[
            _make_link("base_link", joint_type_incoming=None),
            _make_link("arm_link"),
        ],
        joints=[_make_joint("arm_joint", "base_link", "arm_link")],
    )
    report = _run(robot)
    assert report.schema.status == "PASS", f"Expected PASS, got {report.schema.status}"
    assert report.schema.critical_issues == []
    assert report.schema.warnings == []


# ---------------------------------------------------------------------------
# Broken joint references
# ---------------------------------------------------------------------------

def test_broken_parent_ref_is_critical():
    robot = ParsedRobot(
        name="broken_parent",
        links=[
            _make_link("base_link", joint_type_incoming=None),
            _make_link("arm_link"),
        ],
        joints=[_make_joint("arm_joint", "DOES_NOT_EXIST", "arm_link")],
    )
    report = _run(robot)
    assert report.schema.status == "CRITICAL"
    assert any(
        "arm_joint" in issue and "parent" in issue
        for issue in report.schema.critical_issues
    ), f"Expected broken-parent message, got: {report.schema.critical_issues}"


def test_broken_child_ref_is_critical():
    robot = ParsedRobot(
        name="broken_child",
        links=[
            _make_link("base_link", joint_type_incoming=None),
            _make_link("arm_link"),
        ],
        joints=[_make_joint("arm_joint", "base_link", "DOES_NOT_EXIST")],
    )
    report = _run(robot)
    assert report.schema.status == "CRITICAL"
    assert any(
        "arm_joint" in issue and "child" in issue
        for issue in report.schema.critical_issues
    ), f"Expected broken-child message, got: {report.schema.critical_issues}"


# ---------------------------------------------------------------------------
# Duplicate names
# ---------------------------------------------------------------------------

def test_duplicate_link_name_is_critical():
    robot = ParsedRobot(
        name="dup_links",
        links=[
            _make_link("base_link", joint_type_incoming=None),
            _make_link("base_link"),  # same name — duplicate
        ],
        joints=[],
    )
    report = _run(robot)
    assert report.schema.status == "CRITICAL"
    assert any(
        "base_link" in issue and "Duplicate link" in issue
        for issue in report.schema.critical_issues
    ), f"Expected duplicate-link message, got: {report.schema.critical_issues}"


def test_duplicate_joint_name_is_critical():
    robot = ParsedRobot(
        name="dup_joints",
        links=[
            _make_link("base_link", joint_type_incoming=None),
            _make_link("arm_link"),
            _make_link("hand_link"),
        ],
        joints=[
            _make_joint("arm_joint", "base_link", "arm_link"),
            _make_joint("arm_joint", "arm_link", "hand_link"),  # same name — duplicate
        ],
    )
    report = _run(robot)
    assert report.schema.status == "CRITICAL"
    assert any(
        "arm_joint" in issue and "Duplicate joint" in issue
        for issue in report.schema.critical_issues
    ), f"Expected duplicate-joint message, got: {report.schema.critical_issues}"


# ---------------------------------------------------------------------------
# Root link checks
# ---------------------------------------------------------------------------

def test_missing_root_is_critical():
    # Both links appear as joint children → no root candidate
    robot = ParsedRobot(
        name="no_root",
        links=[
            _make_link("link_a", joint_type_incoming="revolute"),
            _make_link("link_b", joint_type_incoming="revolute"),
        ],
        joints=[
            _make_joint("j1", "link_a", "link_b"),
            _make_joint("j2", "link_b", "link_a"),  # makes link_a also a child
        ],
    )
    report = _run(robot)
    assert any(
        "No root link" in issue for issue in report.schema.critical_issues
    ), f"Expected 'No root link' critical, got: {report.schema.critical_issues}"


# ---------------------------------------------------------------------------
# Kinematic loop detection
# ---------------------------------------------------------------------------

def test_kinematic_loop_is_critical():
    # A → B → C → A forms a directed cycle
    robot = ParsedRobot(
        name="loopy_robot",
        links=[
            _make_link("A", joint_type_incoming=None),
            _make_link("B", joint_type_incoming="revolute"),
            _make_link("C", joint_type_incoming="revolute"),
        ],
        joints=[
            _make_joint("j_ab", "A", "B"),
            _make_joint("j_bc", "B", "C"),
            _make_joint("j_ca", "C", "A"),  # back-edge closes the cycle
        ],
    )
    report = _run(robot)
    assert report.schema.status == "CRITICAL"
    assert any(
        "Kinematic loop" in issue for issue in report.schema.critical_issues
    ), f"Expected kinematic loop critical, got: {report.schema.critical_issues}"


def test_loop_check_skipped_on_broken_ref():
    # j_broken references MISSING_LINK (broken ref).
    # j_ca would produce a loop if DFS ran.
    # Expectation: broken ref fires; loop check is skipped.
    robot = ParsedRobot(
        name="broken_and_loopy",
        links=[
            _make_link("A", joint_type_incoming=None),
            _make_link("B", joint_type_incoming="revolute"),
            _make_link("C", joint_type_incoming="revolute"),
        ],
        joints=[
            _make_joint("j_ab", "A", "B"),
            _make_joint("j_bc", "B", "C"),
            _make_joint("j_ca", "C", "A"),            # would be a loop
            _make_joint("j_broken", "A", "MISSING_LINK"),  # broken ref
        ],
    )
    report = _run(robot)
    assert any(
        "MISSING_LINK" in issue for issue in report.schema.critical_issues
    ), "Broken ref must be reported as CRITICAL"
    assert not any(
        "Kinematic loop" in issue for issue in report.schema.critical_issues
    ), "Loop check must be skipped when broken refs are present"


# ---------------------------------------------------------------------------
# Status precedence
# ---------------------------------------------------------------------------

def test_schema_status_critical_when_any_critical():
    # Even with warnings present, one critical → status is CRITICAL not WARN
    robot = ParsedRobot(
        name="mixed_issues",
        links=[
            _make_link("base_link", joint_type_incoming=None),
            _make_link("arm_link", mass=0.0),      # will generate a WARNING
            _make_link("sensor_frame", mass=0.0, joint_type_incoming="revolute"),
        ],
        joints=[
            _make_joint("arm_joint", "base_link", "arm_link"),
            _make_joint("bad_joint", "base_link", "MISSING"),  # CRITICAL broken ref
        ],
    )
    report = _run(robot)
    assert report.schema.status == "CRITICAL", (
        f"Expected CRITICAL (broken ref present), got {report.schema.status}. "
        f"Criticals: {report.schema.critical_issues}, Warnings: {report.schema.warnings}"
    )


# ---------------------------------------------------------------------------
# Physics checks — zero mass
# ---------------------------------------------------------------------------

def test_zero_mass_non_fixed_link_is_warning():
    # arm_link has mass=0.0 and joint_type_incoming="revolute" → warning
    robot = ParsedRobot(
        name="zero_mass_robot",
        links=[
            _make_link("base_link", joint_type_incoming=None),
            _make_link("arm_link", mass=0.0),  # revolute (default), zero mass
        ],
        joints=[_make_joint("arm_joint", "base_link", "arm_link")],
    )
    report = _run(robot)
    assert any(
        "arm_link" in w and "mass" in w.lower() for w in report.schema.warnings
    ), f"Expected zero-mass warning for arm_link, got: {report.schema.warnings}"


def test_zero_mass_fixed_link_is_silent():
    # sensor_frame is a fixed child link with mass=0 → must NOT generate a warning
    robot = ParsedRobot(
        name="fixed_zero_mass",
        links=[
            _make_link("base_link", joint_type_incoming=None),
            _make_link("sensor_frame", mass=0.0, joint_type_incoming="fixed"),
        ],
        joints=[
            _make_joint("sensor_joint", "base_link", "sensor_frame", joint_type="fixed")
        ],
    )
    report = _run(robot)
    assert not any(
        "sensor_frame" in w for w in report.schema.warnings
    ), f"Fixed link with zero mass must not warn. Got: {report.schema.warnings}"


# ---------------------------------------------------------------------------
# Physics checks — zero inertia tensor
# ---------------------------------------------------------------------------

def test_zero_inertia_non_fixed_link_is_warning():
    zero_inertia = np.zeros((3, 3))
    robot = ParsedRobot(
        name="zero_inertia_robot",
        links=[
            _make_link("base_link", joint_type_incoming=None),
            _make_link("arm_link", inertia=zero_inertia),
        ],
        joints=[_make_joint("arm_joint", "base_link", "arm_link")],
    )
    report = _run(robot)
    assert any(
        "arm_link" in w and "zero inertia" in w.lower() for w in report.schema.warnings
    ), f"Expected all-zero-inertia warning for arm_link, got: {report.schema.warnings}"


# ---------------------------------------------------------------------------
# Physics checks — non-positive-definite inertia
# ---------------------------------------------------------------------------

def test_nonpositive_definite_inertia_is_warning():
    # The 2×2 block [[0.1, 0.5], [0.5, 0.1]] has eigenvalues 0.6 and -0.4.
    # Full matrix eigenvalues: 0.6, -0.4, 0.1 — one is negative → physically impossible.
    bad_inertia = np.array(
        [
            [0.1, 0.5, 0.0],
            [0.5, 0.1, 0.0],
            [0.0, 0.0, 0.1],
        ],
        dtype=float,
    )
    robot = ParsedRobot(
        name="bad_inertia_robot",
        links=[
            _make_link("base_link", joint_type_incoming=None),
            _make_link("arm_link", inertia=bad_inertia),
        ],
        joints=[_make_joint("arm_joint", "base_link", "arm_link")],
    )
    report = _run(robot)
    assert any(
        "arm_link" in w and "non-positive-definite" in w and "eigenvalue" in w
        for w in report.schema.warnings
    ), f"Expected eigenvalue warning for arm_link, got: {report.schema.warnings}"


# ---------------------------------------------------------------------------
# No-crash guarantee over all reference URDFs
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("urdf_name", [
    "ANYmal.urdf",
    "Franka_Panda.urdf",
    "PR2.urdf",
    "Spot.urdf",
    "TurtleBot3.urdf",
    "fetch.urdf",
])
def test_all_six_reference_urdfs_schema_does_not_crash(urdf_name):
    path = os.path.join(SAMPLE_DIR, urdf_name)
    result = load_urdf(path)
    if isinstance(result, ParsedRobot):
        report = ValidationReport()
        schema.run(result, report)
        assert report.schema.status in ("PASS", "WARN", "INFO", "CRITICAL"), (
            f"status must be a known value, got {report.schema.status!r} for {urdf_name}"
        )
    # If ParseError, that's acceptable — load_urdf handled the failure; no exception raised
