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
