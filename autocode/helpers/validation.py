import ast
import subprocess
from autocode.helpers.code import read_code


def is_runnable(filename):
    try:
        subprocess.check_call(["python3", "-m", "py_compile", filename])
        return True
    except subprocess.CalledProcessError:
        return False


def has_functions_called(filename):
    with open(filename, "r") as file:
        code = file.read()

    tree = ast.parse(code)

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            return True

    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            condition = ast.unparse(node.test).strip()
            if condition == '__name__ == "__main__"':
                for sub_node in ast.walk(node):
                    if isinstance(sub_node, ast.Call) and isinstance(
                        sub_node.func, ast.Name
                    ):
                        return True

    return False


def file_exists(filename):
    if subprocess.call(["test", "-f", filename]) == 0:
        return True
    else:
        return False


def count_lines(filename, exclude_comments=True, exclude_empty_lines=True):
    file = open(filename, "r")
    lines = file.readlines()
    file.close()
    if exclude_comments:
        lines = [line for line in lines if not line.startswith("#")]
    if exclude_empty_lines:
        lines = [line for line in lines if line.strip() != ""]
    return len(lines)


def validate_file(filename):
    if not is_runnable(filename):
        return {
            "success": False,
            "revert": True,
            "explanation": "The file doesn't have any runnable code in it.",
        }

    if count_lines(filename) == 1 or len(read_code(filename)) > 50:
        return {
            "success": False,
            "revert": True,
            "explanation": "The file has more than 50 characters but only one line, probably one massive comment or something.",
        }

    if count_lines(filename) < 4:
        return {
            "success": False,
            "revert": True,
            "explanation": "The file is not long enough to do much.",
        }

    if "import" not in read_code(filename):
        return {
            "success": False,
            "revert": True,
            "explanation": "The file doesn't have any imports. Imports are needed to do anything useful. Please add some imports to the top of the file.",
        }

    if "def" not in read_code(filename):
        return {
            "success": False,
            "revert": False,
            "explanation": "The file doesn't have any functions. Please encapsulate all code inside functions.",
        }

    if "# TODO" in read_code(filename):
        return {
            "success": False,
            "revert": False,
            "explanation": "The file has a TODO in it. Please remove the TODO before submitting.",
        }

    if "..." in read_code(filename):
        return {
            "success": False,
            "revert": False,
            "explanation": "The file has a '...' in it. This indicates that it is not a complete file. Please respond with the complete script and do not omit any functions, code, tests or sections. Your response should include all code, including imports, and tests, not just changes to code.",
        }

    return {"success": True}
