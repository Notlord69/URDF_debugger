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
