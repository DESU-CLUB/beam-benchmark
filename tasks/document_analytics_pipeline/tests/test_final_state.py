import os
import subprocess
import json
import pytest

APP_NAME = "document-analytics-pipeline"
APP_FILE = "/home/user/modal_project/document_analytics_pipeline.py"
DICT_NAME = "document-analytics-pipeline-output"
VOLUME_NAME = "document-analytics-pipeline-vol"
MODAL_ENV = os.environ.get("MODAL_ENVIRONMENT", "modal-vsdatagen")


def run_modal(args, timeout=300, check=True):
    env = os.environ.copy()
    env["MODAL_ENVIRONMENT"] = MODAL_ENV
    result = subprocess.run(
        ["modal"] + args,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    if check and result.returncode != 0:
        raise RuntimeError(
            f"modal {' '.join(args)} failed:\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}"
        )
    return result


@pytest.fixture(scope="module")
def deployed_app():
    # Deploy the app
    run_modal(
        ["deploy", APP_FILE],
        timeout=600,
    )

    # Run the local entrypoint to populate the Dict and Volume
    run_modal(
        ["run", APP_FILE],
        timeout=300,
    )

    yield

    # Teardown: stop the app
    run_modal(["app", "stop", APP_NAME], timeout=60, check=False)


def test_app_file_exists():
    assert os.path.isfile(APP_FILE), f"App file {APP_FILE} does not exist"


def test_deploy_succeeds(deployed_app):
    # If the fixture completed without raising, deploy succeeded
    pass


def test_app_listed(deployed_app):
    result = run_modal(["app", "list", "--json"], timeout=60)
    apps = json.loads(result.stdout)
    app_names = [a.get("Description", "") for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_names}"
    )


def test_volume_listed(deployed_app):
    result = run_modal(["volume", "list", "--json"], timeout=60)
    volumes = json.loads(result.stdout)
    vol_names = [v.get("Name", "") for v in volumes]
    assert VOLUME_NAME in vol_names, (
        f"Volume '{VOLUME_NAME}' not found in modal volume list. Found: {vol_names}"
    )


def test_volume_report_file_exists(deployed_app):
    result = run_modal(
        ["volume", "ls", VOLUME_NAME, "/"],
        timeout=60,
        check=False,
    )
    assert "analytics_report.json" in result.stdout, (
        f"File 'analytics_report.json' not found in volume. "
        f"Output: {result.stdout}\nSTDERR: {result.stderr}"
    )


def test_dict_total_documents(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "total_documents"], timeout=60)
    raw = result.stdout.strip()
    try:
        value = int(raw)
    except ValueError:
        pytest.fail(f"Dict key 'total_documents' is not an integer. Got: '{raw}'")
    assert value >= 5, (
        f"Dict key 'total_documents' must be >= 5, got {value}"
    )


def test_dict_total_words(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "total_words"], timeout=60)
    raw = result.stdout.strip()
    try:
        value = int(raw)
    except ValueError:
        pytest.fail(f"Dict key 'total_words' is not an integer. Got: '{raw}'")
    assert value > 0, (
        f"Dict key 'total_words' must be > 0, got {value}"
    )


def test_dict_avg_words_per_doc(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "avg_words_per_doc"], timeout=60)
    raw = result.stdout.strip()
    try:
        value = float(raw)
    except ValueError:
        pytest.fail(f"Dict key 'avg_words_per_doc' is not a float. Got: '{raw}'")
    assert value > 0.0, (
        f"Dict key 'avg_words_per_doc' must be > 0.0, got {value}"
    )


def test_dict_report_path(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "report_path"], timeout=60)
    value = result.stdout.strip()
    assert value == "/reports/analytics_report.json", (
        f"Dict key 'report_path' must equal '/reports/analytics_report.json', got '{value}'"
    )
