from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Optional, Union

import numpy as np


# ---------------------------------------------------------------------------
# Intermediate Representation (IR) — plain dataclass containers, no methods
# ---------------------------------------------------------------------------

@dataclass
class ParsedLink:
    name: str
    mass: Optional[float]               # None if no <inertial> block
    inertia_3x3: Optional[np.ndarray]  # shape (3,3), symmetric; None if absent
    joint_type_incoming: Optional[str] # type of the joint whose child this link is; None = root
    visual_geometry_type: Optional[str]    # "box"|"cylinder"|"sphere"|"mesh"|None
    collision_geometry_type: Optional[str] # same set


@dataclass
class ParsedJoint:
    name: str
    joint_type: str        # "revolute"|"prismatic"|"fixed"|"continuous"|"floating"|"planar"
    parent: str            # parent link name
    child: str             # child link name
    limit_lower: Optional[float]
    limit_upper: Optional[float]
    limit_effort: Optional[float]
    limit_velocity: Optional[float]


@dataclass
class ParsedRobot:
    name: str
    links: List[ParsedLink]
    joints: List[ParsedJoint]


@dataclass
class ParseError:
    path: str
    message: str       # human-readable summary
    raw_exception: str # repr(e) — always str, never the live exception object


# ---------------------------------------------------------------------------
# Private helpers (implemented in Task 2)
# ---------------------------------------------------------------------------

def _extract_inertia(link) -> Optional[np.ndarray]:
    """Stub — returns None until Task 2."""
    return None


def _geometry_type(geoms) -> Optional[str]:
    """Stub — returns None until Task 2."""
    return None


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_urdf(path: str) -> Union[ParsedRobot, ParseError]:
    """Stub — always returns ParseError until Task 2 implements the full body."""
    return ParseError(
        path=path,
        message="load_urdf not yet implemented",
        raw_exception="",
    )
