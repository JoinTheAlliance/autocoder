import ast
import subprocess


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


def count_lines(code, exclude_comments=True, exclude_empty_lines=True):
    lines = code.split("\n")
    if exclude_comments:
        lines = [line for line in lines if not line.startswith("#")]
    if exclude_empty_lines:
        lines = [line for line in lines if line.strip() != ""]
    return len(lines)


def validate_file(filename):
    code = open(filename, "r").read()
    if count_lines(code) == 0:
        return {
            "success": False,
            "error": "The file doesn't have any code in it.",
        }
    
    if not is_runnable(filename):
        return {
            "success": False,
            "error": "The file is not runnable, or didn't compile.",
        }

    if count_lines(code) == 1 and len(code) > 50:
        return {
            "success": False,
            "error": "The file has more than 50 characters but only one line, probably one massive comment or something.",
        }

    if count_lines(code) < 4:
        return {
            "success": False,
            "error": "The file is not long enough to do much.",
        }

    if "import" not in code:
        return {
            "success": False,
            "error": "The file doesn't have any imports. Imports are needed to do anything useful. Please add some imports to the top of the file.",
        }

    if "def" not in code:
        return {
            "success": False,
            "error": "The file doesn't have any functions. Please encapsulate all code inside functions.",
        }

    if "TODO" in code:
        return {
            "success": False,
            "error": "The file has a TODO in it. Please replace the TODO with real code or remove it.",
        }

    if "..." in code:
        return {
            "success": False,
            "error": "The file has a '...' in it. This indicates that it is not a complete file. Please respond with the complete script and do not omit any functions, code, tests or sections. Your response should include all code, including imports, and tests, not just changes to code.",
        }

    return {"success": True}
