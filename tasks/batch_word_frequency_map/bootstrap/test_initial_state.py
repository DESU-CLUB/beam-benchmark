import os
import shutil
import subprocess
import pytest
import ast


def test_python3_in_path():
    assert shutil.which("python3") is not None, "python3 not found in PATH"


def test_modal_importable():
    result = subprocess.run(
        ["python3", "-c", "import modal"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"modal not importable: {result.stderr}"


def test_modal_batch_dir_exists():
    assert os.path.isdir("/home/user/modal_batch"), "/home/user/modal_batch directory does not exist"


def test_app_py_exists():
    assert os.path.isfile("/home/user/modal_batch/app.py"), "/home/user/modal_batch/app.py does not exist"


def test_app_py_has_import_modal():
    with open("/home/user/modal_batch/app.py", "r") as f:
        source = f.read()
    assert "import modal" in source, "app.py does not contain 'import modal'"


def test_app_py_has_modal_app():
    with open("/home/user/modal_batch/app.py", "r") as f:
        source = f.read()
    assert "modal.App" in source, "app.py does not contain 'modal.App'"


def test_app_py_has_app_name():
    with open("/home/user/modal_batch/app.py", "r") as f:
        source = f.read()
    assert "batch-word-freq" in source, "app.py does not contain app name 'batch-word-freq'"


def test_count_words_not_defined_yet():
    with open("/home/user/modal_batch/app.py", "r") as f:
        source = f.read()
    try:
        tree = ast.parse(source)
    except SyntaxError:
        pytest.fail("app.py has a syntax error and cannot be parsed")
    function_names = [
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    ]
    assert "count_words" not in function_names, (
        "count_words function already exists in app.py — expected pre-task state without it"
    )
