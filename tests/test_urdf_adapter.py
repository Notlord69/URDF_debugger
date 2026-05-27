import os
import tempfile

import numpy as np
import pytest

from urdf_validator_main.parser.urdf_adapter import (
    ParsedLink,
    ParsedJoint,
    ParsedRobot,
    ParseError,
    load_urdf,
)

SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "sample_urdf")
