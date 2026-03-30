import os
import subprocess
import json
import pytest

APP_NAME = "modal-event-pipeline"
APP_FILE = "/home/user/modal_project/modal_event_pipeline.py"
DICT_NAME = "modal-event-pipeline-output"
VOLUME_NAME = "modal-event-pipeline-vol"
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
    # Create the volume if it doesn't already exist
    vol_list = run_modal(["volume", "list", "--json"], timeout=60, check=False)
    volumes = json.loads(vol_list.stdout) if vol_list.stdout.strip() else []
    existing_volumes = [v.get("Name", "") for v in volumes]
    if VOLUME_NAME not in existing_volumes:
        run_modal(["volume", "create", VOLUME_NAME], timeout=60)

    # Deploy the app
    run_modal(
        ["deploy", APP_FILE],
        timeout=600,
    )

    # Run the local entrypoint to execute the pipeline
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


def test_volume_processed_events_file_exists(deployed_app):
    result = run_modal(
        ["volume", "ls", VOLUME_NAME, "/"],
        timeout=60,
        check=False,
    )
    assert "processed_events.json" in result.stdout, (
        f"File 'processed_events.json' not found in volume. "
        f"Output: {result.stdout}\nSTDERR: {result.stderr}"
    )


def test_dict_events_produced(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "events_produced"], timeout=60)
    value = result.stdout.strip()
    assert value == "10", (
        f"Dict key 'events_produced' must equal '10', got '{value}'"
    )


def test_dict_events_consumed(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "events_consumed"], timeout=60)
    value = result.stdout.strip()
    assert value == "10", (
        f"Dict key 'events_consumed' must equal '10', got '{value}'"
    )


def test_dict_processing_complete(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "processing_complete"], timeout=60)
    value = result.stdout.strip()
    assert value == "true", (
        f"Dict key 'processing_complete' must equal 'true', got '{value}'"
    )


def test_dict_output_path(deployed_app):
    result = run_modal(["dict", "get", DICT_NAME, "output_path"], timeout=60)
    value = result.stdout.strip()
    assert value == "/events/processed_events.json", (
        f"Dict key 'output_path' must equal '/events/processed_events.json', got '{value}'"
    )
