import pytest

from autocode.helpers.code import (
    check_if_builtin,
    contains_function_definition,
    file_exists,
    has_functions_called,
    is_runnable,
)


def test_check_if_builtin_success():
    assert check_if_builtin("os") == True


def test_check_if_builtin_failure():
    assert check_if_builtin("fake_module") == False


def test_is_runnable_success(tmp_path):
    p = tmp_path / "hello.py"
    p.write_text("print('Hello, world!')")
    assert is_runnable(str(p)) == True


def test_is_runnable_failure(tmp_path):
    p = tmp_path / "bad.py"
    p.write_text("print('Hello, world!")
    assert is_runnable(str(p)) == False


def test_contains_function_definition_true():
    code = """
    def hello():
        print('Hello, world!')
    """
    assert contains_function_definition(code) == True


def test_contains_function_definition_false():
    code = """
    print('Hello, world!')
    """
    assert contains_function_definition(code) == False


def test_has_functions_called_true():
    code = """
    print('Hello, world!')
    """
    assert has_functions_called(code) == True


def test_has_functions_called_false():
    code = """
    def hello():
        print('Hello, world!')
    """
    assert has_functions_called(code) == False


def test_file_exists_true(tmp_path):
    p = tmp_path / "hello.py"
    p.write_text("print('Hello, world!')")
    assert file_exists(str(p)) == True


def test_file_exists_false(tmp_path):
    assert file_exists("/path/to/nonexistent/file") == False


from autocode.helpers.code import (
    install_imports,
    get_imports,
    count_lines,
    validate_file,
    validate_code,
    save_code,
    run_code,
    test_code,
)


def test_get_imports():
    code = """
    import os
    import sys
    from subprocess import call
    """
    assert set(get_imports(code)) == set(["os", "sys", "subprocess"])


def test_count_lines_with_comments_and_empty_lines():
    code = """
    # This is a comment
    print('Hello, world!')  # This is another comment

    # This is yet another comment
    """
    assert count_lines(code) == 1


def test_count_lines_without_comments_and_empty_lines():
    code = """
    # This is a comment
    print('Hello, world!')  # This is another comment

    # This is yet another comment
    """
    assert count_lines(code, exclude_comments=True, exclude_empty_lines=True) == 1


def test_validate_file_success(tmp_path):
    p = tmp_path / "good.py"
    p.write_text("def hello():\n\tprint('Hello, world!')\nhello()")
    assert validate_file(str(p)) == {"success": True, "error": None}


def test_validate_file_failure(tmp_path):
    p = tmp_path / "bad.py"
    p.write_text("print('Hello, world!")
    assert validate_file(str(p)) == {
        "success": False,
        "error": "The file is not runnable, or didn't compile.",
    }


def test_validate_code_success():
    code = """
    import os

    def hello():
        print('Hello, world!')

    hello()
    """
    assert validate_code(code) == {"success": True, "error": None}


def test_validate_code_failure():
    code = """
    import os
    TODO: Implement function here
    """
    assert validate_code(code) == {
        "success": False,
        "error": "The file has a TODO in it. Please replace the TODO with real code or remove it.",
    }


def test_save_code(tmp_path):
    p = tmp_path / "hello.py"
    code = "print('Hello, world!')"
    save_code(code, str(p))
    assert p.read_text() == code


def test_run_code_success(tmp_path):
    p = tmp_path / "hello.py"
    p.write_text("print('Hello, world!')")
    result = run_code(str(p))
    assert result["success"] == True
    assert result["error"] == None
    assert result["output"].strip() == "Hello, world!"


def test_run_code_failure(tmp_path):
    p = tmp_path / "bad.py"
    p.write_text("print('Hello, world!")
    result = run_code(str(p))
    assert result["success"] == False
    assert "SyntaxError: EOL while scanning string literal" in result["error"]


def test_test_code_success(tmp_path):
    p = tmp_path / "test_hello.py"
    p.write_text(
        """
    def test_hello():
        assert 'Hello, world!' == 'Hello, world!'
    """
    )
    result = test_code(str(p))
    assert result["success"] == True
    assert "1 passed" in result["output"]
    assert result["error"] == ""


def test_test_code_failure(tmp_path):
    p = tmp_path / "test_bad.py"
    p.write_text(
        """
    def test_bad():
        assert 'Hello, world!' == 'Goodbye, world!'
    """
    )
    result = test_code(str(p))
    assert result["success"] == False
    assert "1 failed" in result["output"]
