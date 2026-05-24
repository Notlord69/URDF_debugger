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
