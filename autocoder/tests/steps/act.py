import os
import shutil
from autocoder.helpers.files import get_full_path

from autocoder.steps.act import (
    create_handler,
    create_new_file_handler,
    delete_file_handler,
    insert_code_handler,
    remove_code_handler,
    replace_code_handler,
    write_complete_script_handler,
)


def setup_function():
    if not os.path.exists("test_dir"):
        os.makedirs("test_dir")


def teardown_function():
    if os.path.exists("test_dir"):
        for root, dirs, files in os.walk("test_dir", topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
    # remove test_dir
    if os.path.exists("test_dir"):
        # use shutil to recursively remove the directory
        shutil.rmtree("test_dir")


def test_create_handler():
    setup_function()
    context = {"project_dir": "test_dir"}
    arguments = {
        "reasoning": "Testing create handler",
        "code": "print('Hello, World!')",
        "test": "def test_main(): assert True",
    }
    create_handler(arguments, context)

    assert os.path.isfile("test_dir/main.py")
    assert os.path.isfile("test_dir/main_test.py")
    teardown_function()


def test_write_complete_script_handler():
    setup_function()
    context = {"project_dir": "test_dir"}
    arguments = {
        "reasoning": "Testing write complete script handler",
        "code": "print('Hello, World!')",
        "filename": "main.py",
    }
    write_complete_script_handler(arguments, context)

    assert os.path.isfile("test_dir/main.py")
    # read and print file contents
    with open("test_dir/main.py", "r") as f:
        text = f.read()
    lines = text.split("\n")
    assert "Hello, World!" in lines[0]
    print(text)
    teardown_function()


def test_insert_code_handler():
    setup_function()
    context = {"project_dir": "test_dir"}
    arguments = {
        "reasoning": "Testing insert code handler",
        "code": "print('Inserted line')",
        "start_line": 1,
        "filename": "main.py",
    }

    write_arguments = {
        "reasoning": "Testing write complete script handler",
        "code": "print('Hello, World!')\nprint('An inserted line should come before this!')",
        "filename": "main.py",
    }
    write_complete_script_handler(
        write_arguments, context
    )  # First, create a file to insert into

    insert_code_handler(arguments, context)

    with open("test_dir/main.py", "r") as f:
        text = f.read()
        lines = text.split("\n")
    print("Insert code:\n====================")
    print(text)
    print("====================")
    assert "Inserted line" in lines[1]
    teardown_function()


def test_replace_code_handler():
    setup_function()
    context = {"project_dir": "test_dir"}
    arguments = {
        "reasoning": "Testing replace code handler",
        "code": "print('New line')\nprint('Second new line')",
        "start_line": 1,
        "end_line": 2,
        "filename": "main.py",
    }

    # write test_dir/main.py
    with open("test_dir/main.py", "w") as f:
        f.write("print('Old line')\nprint('Second old line')\nprint('Third old line')")

    replace_code_handler(arguments, context)

    with open("test_dir/main.py", "r") as f:
        text = f.read()
        lines = text.split("\n")
        print("Replace code:")
        print(text)
    assert "New line" in lines[0]
    teardown_function()


def test_remove_code_handler():
    setup_function()
    context = {"project_dir": "test_dir"}
    arguments = {
        "reasoning": "Testing remove code handler",
        "start_line": 1,
        "end_line": 1,
        "filename": "main.py",
    }
    write_arguments = {
        "reasoning": "Testing write complete script handler",
        "code": "print('Hello, World!')",
        "filename": "main.py",
    }
    write_complete_script_handler(
        write_arguments, context
    )  # First, create a file to remove from
    remove_code_handler(arguments, context)

    with open("test_dir/main.py", "r") as f:
        text = f.read()
        print(text)
    lines = text.split("\n")
    assert "New line" not in lines
    teardown_function()


def test_create_new_file_handler():
    setup_function()
    context = {"project_dir": "test_dir"}
    arguments = {
        "reasoning": "Testing create new file handler",
        "filename": "new_file.py",
        "code": "print('Hello, New File!')",
        "test": "def test_new_file(): assert True",
    }
    create_new_file_handler(arguments, context)

    assert os.path.isfile("test_dir/new_file.py")
    assert os.path.isfile("test_dir/new_file_test.py")
    teardown_function()


def test_delete_file_handler():
    setup_function()

    # Add a file that will be deleted
    with open(os.path.join("test_dir", "file_to_delete.py"), "w") as f:
        f.write('print("This file will be deleted!")')

    # Add the corresponding test file
    with open(os.path.join("test_dir", "file_to_delete_test.py"), "w") as f:
        f.write("def test_file_to_delete(): assert True")

    context = {"project_dir": "test_dir", "log_level": "debug"}

    arguments = {
        "reasoning": "Testing delete function",
        "filename": "file_to_delete.py",
    }

    context = delete_file_handler(arguments, context)

    file_path = get_full_path("file_to_delete.py", context["project_dir"])
    test_file_path = get_full_path("file_to_delete_test.py", context["project_dir"])

    # Ensure the files were deleted
    assert not os.path.exists(file_path), f"{file_path} was not deleted"
    assert not os.path.exists(test_file_path), f"{test_file_path} was not deleted"

    teardown_function()
