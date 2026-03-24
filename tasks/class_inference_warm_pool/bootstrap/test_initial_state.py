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
    assert os.path.isdir("/home/user/modal_class"), (
        "/home/user/modal_class directory does not exist"
    )


def test_starter_app_py_exists():
    app_path = "/home/user/modal_class/app.py"
    assert os.path.isfile(app_path), f"starter app.py not found at {app_path}"


def test_starter_app_py_has_modal_app():
    app_path = "/home/user/modal_class/app.py"
    with open(app_path) as f:
        source = f.read()
    try:
        ast.parse(source)
    except SyntaxError as e:
        assert False, f"app.py has invalid Python syntax: {e}"
    assert "import modal" in source, "app.py should import modal"
    assert "modal.App" in source, "app.py should define a modal.App"
    assert "class-inference-warm" in source, "App must be named 'class-inference-warm'"


def test_text_classifier_class_not_present():
    """Verify that TextClassifier class does not exist yet (pre-task state)."""
    app_path = "/home/user/modal_class/app.py"
    with open(app_path) as f:
        source = f.read()
    tree = ast.parse(source)
    class_names = [
        node.name for node in ast.walk(tree)
        if isinstance(node, ast.ClassDef)
    ]
    assert "TextClassifier" not in class_names, (
        "TextClassifier class already exists — initial state is incorrect"
    )
