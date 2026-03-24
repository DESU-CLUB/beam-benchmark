import ast
import os
import shutil
import subprocess


def test_python3_in_path():
    assert shutil.which("python3") is not None, "python3 not found in PATH"


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal package is not importable: {result.stderr}"


def test_project_directory_exists():
    assert os.path.isdir("/home/user/modal_cron"), (
        "/home/user/modal_cron directory does not exist"
    )


def test_starter_reporter_py_exists():
    app_path = "/home/user/modal_cron/reporter.py"
    assert os.path.isfile(app_path), f"starter reporter.py not found at {app_path}"


def test_starter_reporter_py_has_modal_app():
    app_path = "/home/user/modal_cron/reporter.py"
    with open(app_path) as f:
        source = f.read()
    try:
        ast.parse(source)
    except SyntaxError as e:
        assert False, f"reporter.py has invalid Python syntax: {e}"
    assert "import modal" in source, "reporter.py should import modal"
    assert "modal.App" in source, "reporter.py should define a modal.App"
    assert "status-reporter" in source, "App must be named 'status-reporter'"


def test_report_status_function_not_present():
    """Verify that report_status function does not exist yet (pre-task state)."""
    app_path = "/home/user/modal_cron/reporter.py"
    with open(app_path) as f:
        source = f.read()
    tree = ast.parse(source)
    func_names = [
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert "report_status" not in func_names, (
        "report_status function already exists — initial state is incorrect"
    )
