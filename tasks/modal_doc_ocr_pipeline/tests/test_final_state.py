import os
import subprocess
import json
import pytest

APP_NAME = "modal-doc-ocr-pipeline"
APP_FILE = "/home/user/modal_project/modal_doc_ocr_pipeline.py"
DICT_NAME = "modal-doc-ocr-pipeline-output"
VOLUME_NAME = "modal-doc-ocr-pipeline-vol"
SECRET_NAME = "modal-doc-ocr-pipeline-secret"
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
    # Create the secret before deploying
    run_modal(
        [
            "secret", "create", SECRET_NAME,
            "OCR_SERVICE_KEY=ocr-key-2024-xyz",
            "MAX_PAGES=100",
            "--force",
        ],
        timeout=60,
    )

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


def test_secret_listed(deployed_app):
    result = run_modal(["secret", "list", "--json"], timeout=60)
    secrets = json.loads(result.stdout)
    secret_names = [s.get("Name", "") for s in secrets]
    assert SECRET_NAME in secret_names, (
        f"Secret '{SECRET_NAME}' not found in modal secret list. Found: {secret_names}"
    )


def test_volume_summary_file_exists(deployed_app):
    result = run_modal(
        ["volume", "ls", VOLUME_NAME, "/"],
        timeout=60,
        check=False,
    )
    assert "summary.json" in result.stdout, (
        f"File 'summary.json' not found in volume. "
        f"Output: {result.stdout}\nSTDERR: {result.stderr}"
    )


def test_dict_documents_processed(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "documents_processed"], timeout=60)
    raw = result.stdout.strip()
    try:
        value = int(raw)
    except ValueError:
        pytest.fail(f"Dict key 'documents_processed' is not an integer. Got: '{raw}'")
    assert value >= 6, (
        f"Dict key 'documents_processed' must be >= 6, got {value}"
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


def test_dict_total_sentences(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "total_sentences"], timeout=60)
    raw = result.stdout.strip()
    try:
        value = int(raw)
    except ValueError:
        pytest.fail(f"Dict key 'total_sentences' is not an integer. Got: '{raw}'")
    assert value > 0, (
        f"Dict key 'total_sentences' must be > 0, got {value}"
    )


def test_dict_ocr_service_key_present(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "ocr_service_key_present"], timeout=60)
    value = result.stdout.strip()
    assert value == "true", (
        f"Dict key 'ocr_service_key_present' must equal 'true', got '{value}'"
    )


def test_dict_summary_path(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "summary_path"], timeout=60)
    value = result.stdout.strip()
    assert value == "/ocr_output/summary.json", (
        f"Dict key 'summary_path' must equal '/ocr_output/summary.json', got '{value}'"
    )
