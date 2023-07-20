import os
import shutil
from pathlib import Path

from autocode.helpers.context import (
    get_file_count,
    read_and_format_code,
    collect_files,
    validate_files,
    run_tests,
    run_main,
    backup_project,
)

# Assuming you have a directory for testing
TEST_DIR = "test_dir"
PROJECT_NAME = "test_project"


def setup_function():
    # Create a temporary directory for testing
    os.makedirs(TEST_DIR)

    # Add some python files
    with open(os.path.join(TEST_DIR, "main.py"), "w") as f:
        f.write('print("Hello, world!")')

    with open(os.path.join(TEST_DIR, "test_main.py"), "w") as f:
        f.write("def test_main(): assert True")


def teardown_function():
    # Remove the directory after test
    shutil.rmtree(TEST_DIR)


def test_get_file_count():
    setup_function()

    context = {"project_dir": TEST_DIR}
    result = get_file_count(context)

    assert "file_count" in result
    assert result["file_count"] == 2  # We've created 2 files in setup

    teardown_function()


def test_read_and_format_code():
    setup_function()

    context = {"project_dir": TEST_DIR}
    context = collect_files(context)
    context = validate_files(context)
    context = run_tests(context)
    context = run_main(context)
    result = read_and_format_code(context)

    assert "project_code_formatted" in result
    assert "Hello, world!" in result["project_code_formatted"]

    teardown_function()


def test_collect_files():
    setup_function()

    context = {"project_dir": TEST_DIR}
    result = collect_files(context)

    assert "filetree" in result
    assert "filetree_formatted" in result
    assert "python_files" in result
    assert "project_code" in result

    teardown_function()


def test_validate_files():
    setup_function()

    context = {"project_dir": TEST_DIR}
    context = collect_files(context)
    result = validate_files(context)

    assert "project_code" in result
    assert "project_validated" in result
    assert result["project_validated"] is True  # Assuming the files pass validation

    teardown_function()


def test_run_tests():
    setup_function()

    context = {"project_dir": TEST_DIR}
    context = collect_files(context)
    result = run_tests(context)

    assert "project_tested" in result
    assert result["project_tested"] is True  # We have a simple test that always passes

    teardown_function()


def test_run_main():
    setup_function()

    context = {"project_dir": TEST_DIR}
    context = collect_files(context)
    result = run_main(context)

    assert "main_success" in result
    assert (
        result["main_success"] is True
    )  # main.py just prints a string, so it should succeed

    teardown_function()


def test_backup_project():
    setup_function()

    context = {"project_dir": TEST_DIR, "name": PROJECT_NAME}
    result = backup_project(context)

    assert "backup" in result
    assert Path(result["backup"]).exists()  # The backup file should be created

    teardown_function()
