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
    assert os.path.isdir("/home/user/modal_pipeline"), (
        "/home/user/modal_pipeline directory does not exist"
    )


def test_starter_pipeline_py_exists():
    app_path = "/home/user/modal_pipeline/pipeline.py"
    assert os.path.isfile(app_path), f"starter pipeline.py not found at {app_path}"


def test_starter_pipeline_py_has_modal_app():
    app_path = "/home/user/modal_pipeline/pipeline.py"
    with open(app_path) as f:
        source = f.read()
    try:
        ast.parse(source)
    except SyntaxError as e:
        assert False, f"pipeline.py has invalid Python syntax: {e}"
    assert "import modal" in source, "pipeline.py should import modal"
    assert "modal.App" in source, "pipeline.py should define a modal.App"
    assert "text-index-pipeline" in source, "App must be named 'text-index-pipeline'"


def test_index_documents_function_not_present():
    """Verify that the index_documents function doesn't exist yet (task not solved)."""
    app_path = "/home/user/modal_pipeline/pipeline.py"
    with open(app_path) as f:
        source = f.read()
    tree = ast.parse(source)
    func_names = [
        node.name for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    assert "index_documents" not in func_names, (
        "index_documents function already exists — initial state is incorrect"
    )
