import os
import json
import subprocess
import pytest
import re

MODAL_ENV = "modal-vsdatagen"
APP_FILE = "/home/user/modal_project/pipeline.py"
APP_NAME = "document-analytics-pipeline"
SECRET_NAME = "pipeline-credentials"
DICT_NAME = "doc-analytics-output"


def modal_cli(*args, timeout=300):
    """Run a Modal CLI command with MODAL_ENVIRONMENT set."""
    env = {**os.environ, "MODAL_ENVIRONMENT": MODAL_ENV}
    cmd = ["modal"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
    return result


@pytest.fixture(scope="module")
def deployed_app():
    """Create secret, deploy the app, run it to populate the dict, then clean up."""
    # Create the pipeline secret before deploying
    secret_result = modal_cli(
        "secret", "create", SECRET_NAME,
        "PIPELINE_API_KEY=super-secret-pipeline-key",
        "--force"
    )
    assert secret_result.returncode == 0, (
        f"Failed to create Modal secret '{SECRET_NAME}':\n"
        f"stdout: {secret_result.stdout}\nstderr: {secret_result.stderr}"
    )

    # Deploy the app
    deploy_result = modal_cli("deploy", APP_FILE, timeout=300)
    assert deploy_result.returncode == 0, (
        f"modal deploy failed:\nstdout: {deploy_result.stdout}\nstderr: {deploy_result.stderr}"
    )

    # Trigger a pipeline run to populate the Modal Dict
    run_result = modal_cli("run", APP_FILE, timeout=300)
    assert run_result.returncode == 0, (
        f"modal run failed:\nstdout: {run_result.stdout}\nstderr: {run_result.stderr}"
    )

    yield

    modal_cli("app", "stop", APP_NAME)


def test_pipeline_file_exists():
    assert os.path.isfile(APP_FILE), (
        f"Expected pipeline file {APP_FILE} does not exist."
    )


def test_deploy_succeeds(deployed_app):
    """Deployment must succeed — validated in the fixture."""
    pass


def test_app_listed(deployed_app):
    result = modal_cli("app", "list", "--json")
    assert result.returncode == 0, f"modal app list --json failed: {result.stderr}"
    apps = json.loads(result.stdout)
    app_names = [a["Description"] for a in apps]
    assert APP_NAME in app_names, (
        f"App '{APP_NAME}' not found in modal app list. Found: {app_names}"
    )


def test_secret_exists(deployed_app):
    result = modal_cli("secret", "list", "--json")
    assert result.returncode == 0, f"modal secret list --json failed: {result.stderr}"
    secrets = json.loads(result.stdout)
    secret_names = [s["Name"] for s in secrets]
    assert SECRET_NAME in secret_names, (
        f"Secret '{SECRET_NAME}' not found in modal secret list. Found: {secret_names}"
    )


def test_dict_summary_exists(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "summary")
    assert result.returncode == 0, (
        f"Failed to get key 'summary' from Dict '{DICT_NAME}':\n"
        f"stdout: {result.stdout}\nstderr: {result.stderr}"
    )
    assert result.stdout.strip() != "", (
        f"Dict '{DICT_NAME}' key 'summary' returned empty output."
    )


def test_dict_summary_has_required_fields(deployed_app):
    result = modal_cli("dict", "get", DICT_NAME, "summary")
    assert result.returncode == 0, (
        f"Failed to retrieve 'summary' from Dict '{DICT_NAME}': {result.stderr}"
    )
    raw = result.stdout.strip()
    assert "total_documents" in raw, (
        f"'summary' dict does not contain 'total_documents'. Got: {raw}"
    )
    assert "total_words" in raw, (
        f"'summary' dict does not contain 'total_words'. Got: {raw}"
    )
    assert "avg_words_per_doc" in raw or "avg_word" in raw, (
        f"'summary' dict does not contain average word count field. Got: {raw}"
    )
    assert "timestamp" in raw, (
        f"'summary' dict does not contain 'timestamp'. Got: {raw}"
    )


def test_dict_has_minimum_document_entries(deployed_app):
    result = modal_cli("dict", "items", DICT_NAME, "--json")
    assert result.returncode == 0, (
        f"Failed to list Dict '{DICT_NAME}' items: {result.stderr}"
    )
    items = json.loads(result.stdout)
    assert len(items) >= 11, (
        f"Expected at least 11 entries in '{DICT_NAME}' (10 documents + 1 summary), "
        f"but found {len(items)}."
    )


def test_dict_has_summary_key(deployed_app):
    result = modal_cli("dict", "items", DICT_NAME, "--json")
    assert result.returncode == 0, (
        f"Failed to list Dict '{DICT_NAME}' items: {result.stderr}"
    )
    items = json.loads(result.stdout)
    # items is a list of [key, value] pairs or dicts with key field
    keys = []
    for item in items:
        if isinstance(item, list):
            keys.append(str(item[0]))
        elif isinstance(item, dict):
            keys.append(str(item.get("key", item.get("Key", ""))))
    assert "summary" in keys, (
        f"Key 'summary' not found in Dict '{DICT_NAME}'. Keys found: {keys}"
    )


def test_dict_document_entries_have_analytics_fields(deployed_app):
    result = modal_cli("dict", "items", DICT_NAME, "--json")
    assert result.returncode == 0, (
        f"Failed to list Dict '{DICT_NAME}' items: {result.stderr}"
    )
    items = json.loads(result.stdout)

    # Find a non-summary document entry to validate
    doc_entry_raw = None
    for item in items:
        if isinstance(item, list):
            key = str(item[0])
            val = item[1] if len(item) > 1 else None
        elif isinstance(item, dict):
            key = str(item.get("key", item.get("Key", "")))
            val = item.get("value", item.get("Value", None))
        else:
            continue
        if key != "summary" and val is not None:
            doc_entry_raw = str(val)
            break

    assert doc_entry_raw is not None, (
        f"No document entries (non-summary) found in Dict '{DICT_NAME}'."
    )
    assert "word_count" in doc_entry_raw, (
        f"Document entry missing 'word_count'. Entry: {doc_entry_raw}"
    )
    assert "sentence_count" in doc_entry_raw, (
        f"Document entry missing 'sentence_count'. Entry: {doc_entry_raw}"
    )
    assert "keywords" in doc_entry_raw, (
        f"Document entry missing 'keywords'. Entry: {doc_entry_raw}"
    )
    assert "char_count" in doc_entry_raw, (
        f"Document entry missing 'char_count'. Entry: {doc_entry_raw}"
    )


def test_run_succeeds(deployed_app):
    """Running the pipeline must succeed, confirming cron logic is executable."""
    pass  # Assertion is in the fixture's run step
