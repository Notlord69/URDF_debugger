from __future__ import annotations

import collections
from typing import Set

from urdf_validator_main.parser.urdf_adapter import ParsedRobot
from urdf_validator_main.report.models import ValidationReport


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run(parsed: ParsedRobot, report: ValidationReport) -> None:
    """Run all schema checks. Writes findings as formatted strings into report.schema.

    Call order matters:
      1. _check_broken_refs must run before _check_kinematic_loops so the loop
         guard has an accurate broken-ref count.
      2. _set_schema_status runs last after all findings are collected.
    """
    broken_ref_count = _check_broken_refs(parsed, report)
    _check_duplicate_names(parsed, report)
    _check_missing_root(parsed, report)
    _check_kinematic_loops(parsed, report, skip=broken_ref_count > 0)
    _check_zero_mass(parsed, report)
    _check_zero_inertia(parsed, report)
    _check_inertia_positive_definite(parsed, report)
    _set_schema_status(report)


# ---------------------------------------------------------------------------
# Structural checks
# ---------------------------------------------------------------------------

def _check_duplicate_names(parsed: ParsedRobot, report: ValidationReport) -> None:
    """Append CRITICAL for any link or joint name that appears more than once."""
    link_counts = collections.Counter(lnk.name for lnk in parsed.links)
    for name, count in link_counts.items():
        if count > 1:
            report.schema.critical_issues.append(
                f"Duplicate link name: '{name}' appears {count} times"
            )

    joint_counts = collections.Counter(j.name for j in parsed.joints)
    for name, count in joint_counts.items():
        if count > 1:
            report.schema.critical_issues.append(
                f"Duplicate joint name: '{name}' appears {count} times"
            )


def _check_broken_refs(parsed: ParsedRobot, report: ValidationReport) -> int:
    """Append CRITICAL for joints referencing link names not in parsed.links.

    Returns the number of broken references found (used by _check_kinematic_loops
    to decide whether to skip DFS — a graph with broken refs is untrustworthy).
    """
    link_names: Set[str] = {lnk.name for lnk in parsed.links}
    broken = 0
    for j in parsed.joints:
        if j.parent not in link_names:
            report.schema.critical_issues.append(
                f"Joint '{j.name}' references unknown parent link: '{j.parent}'"
            )
            broken += 1
        if j.child not in link_names:
            report.schema.critical_issues.append(
                f"Joint '{j.name}' references unknown child link: '{j.child}'"
            )
            broken += 1
    return broken


def _check_missing_root(parsed: ParsedRobot, report: ValidationReport) -> None:
    """Check that exactly one root link exists (a link not appearing as any joint child)."""
    children: Set[str] = {j.child for j in parsed.joints}
    root_candidates = [lnk.name for lnk in parsed.links if lnk.name not in children]

    if len(root_candidates) == 0:
        report.schema.critical_issues.append(
            "No root link found: every link is a child of some joint "
            "(kinematic loop or broken reference)"
        )
    elif len(root_candidates) > 1:
        report.schema.infos.append(
            f"Multiple root links found: {root_candidates} — expected exactly one"
        )
    # Exactly one root → silent pass


def _check_kinematic_loops(
    parsed: ParsedRobot, report: ValidationReport, skip: bool = False
) -> None:
    """Detect cycles in the joint graph using iterative DFS with back-edge detection.

    Skipped entirely when broken refs are present (the graph is untrustworthy
    for traversal and would produce false-positive loop reports).
    """
    if skip:
        return

    # Build adjacency: parent link → list of child links
    adjacency: dict = collections.defaultdict(list)
    for j in parsed.joints:
        adjacency[j.parent].append(j.child)

    all_link_names = {lnk.name for lnk in parsed.links}
    visited: Set[str] = set()

    for start in all_link_names:
        if start in visited:
            continue

        # Iterative DFS — stack holds (node, iterator-over-children)
        stack = [(start, iter(adjacency.get(start, [])))]
        in_stack: Set[str] = {start}
        visited.add(start)

        while stack:
            node, children_iter = stack[-1]
            try:
                child = next(children_iter)
                if child in in_stack:
                    # Back-edge detected → cycle
                    report.schema.critical_issues.append(
                        f"Kinematic loop detected involving link: '{child}'"
                    )
                elif child not in visited:
                    visited.add(child)
                    in_stack.add(child)
                    stack.append((child, iter(adjacency.get(child, []))))
            except StopIteration:
                stack.pop()
                in_stack.discard(node)


# ---------------------------------------------------------------------------
# Physics checks
# ---------------------------------------------------------------------------

def _check_zero_mass(parsed: ParsedRobot, report: ValidationReport) -> None:
    """Warn about non-fixed links with missing or non-positive mass.

    Fixed links and the root link (joint_type_incoming=None) are skipped:
    they commonly have zero mass (sensor frames, visual-only links) and that
    is harmless — flagging them would produce noise on every real-world URDF.
    """
    for lnk in parsed.links:
        if lnk.joint_type_incoming in ("fixed", None):
            continue
        if lnk.mass is None:
            report.schema.warnings.append(
                f"Link '{lnk.name}' has no inertial block (mass unknown) "
                "— will cause physics engine instability"
            )
        elif lnk.mass <= 0:
            report.schema.warnings.append(
                f"Link '{lnk.name}' has zero or negative mass "
                f"(mass={lnk.mass}) — will cause Gazebo/PyBullet collapse"
            )


def _check_zero_inertia(parsed: ParsedRobot, report: ValidationReport) -> None:
    """Warn about non-fixed links whose entire inertia tensor is all zeros."""
    import numpy as np

    for lnk in parsed.links:
        if lnk.joint_type_incoming in ("fixed", None):
            continue
        if lnk.inertia_3x3 is None:
            continue
        if np.all(lnk.inertia_3x3 == 0):
            report.schema.warnings.append(
                f"Link '{lnk.name}' has all-zero inertia tensor "
                "— will cause physics engine collapse"
            )


def _check_inertia_positive_definite(
    parsed: ParsedRobot, report: ValidationReport
) -> None:
    """Warn about non-fixed links with a non-positive-definite inertia tensor.

    Uses numpy.linalg.eigvalsh (symmetric eigenvalue solver — correct for
    inertia tensors). Skips all-zero tensors (already caught by _check_zero_inertia).
    Catches any eigvalsh failure so a malformed tensor never propagates.
    """
    import numpy as np

    for lnk in parsed.links:
        if lnk.joint_type_incoming in ("fixed", None):
            continue
        if lnk.inertia_3x3 is None:
            continue
        if np.all(lnk.inertia_3x3 == 0):
            continue  # already reported by _check_zero_inertia
        try:
            eigenvalues = np.linalg.eigvalsh(lnk.inertia_3x3)
            if np.any(eigenvalues <= 0):
                min_ev = float(np.min(eigenvalues))
                report.schema.warnings.append(
                    f"Link '{lnk.name}' has non-positive-definite inertia tensor "
                    f"(min eigenvalue: {min_ev:.6f}) — physically impossible"
                )
        except Exception:
            report.schema.warnings.append(
                f"Link '{lnk.name}' inertia eigenvalue check failed "
                "— tensor may be malformed"
            )


# ---------------------------------------------------------------------------
# Status derivation
# ---------------------------------------------------------------------------

def _set_schema_status(report: ValidationReport) -> None:
    """Derive report.schema.status from populated issue lists (call last)."""
    if report.schema.critical_issues:
        report.schema.status = "CRITICAL"
    elif report.schema.warnings:
        report.schema.status = "WARN"
    elif report.schema.infos:
        report.schema.status = "INFO"
    else:
        report.schema.status = "PASS"
