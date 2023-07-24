import os
import subprocess
import ast
import sys
import black
from importlib_metadata import distributions
from agentlogger import log


def is_runnable(filename):
    try:
        result = subprocess.run(
            ["python", "-m", "py_compile", filename],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        if result.stderr and result.stderr != "":
            return False

        if result.returncode != 0:
            return False
    except Exception as e:
        log(f"An error occurred: {e}", title="is_runnable", type="error")
        return False

    return True


def contains_function_definition(code):
    """Checks if a string of Python code contains any function definitions."""

    def visit(node):
        """Recursively visit nodes in the AST."""
        if isinstance(node, ast.FunctionDef):
            # If we're at a function definition node, return True
            return True
        else:
            # For all other nodes, recursively visit their children and return True if any of them return True
            for child in ast.iter_child_nodes(node):
                if visit(child):
                    return True
        # If no function definition was found, return False
        return False

    try:
        tree = ast.parse(code)
        return visit(tree)
    except SyntaxError:
        return False


def has_functions_called(code):
    """Checks if a string is valid Python code and if it performs a function call at root level."""

    def visit(node, inside_function_def=False):
        """Recursively visit nodes in the AST."""
        if isinstance(node, ast.FunctionDef):
            # If we're at a function definition node, recursively visit its children without updating the result
            for child in ast.iter_child_nodes(node):
                visit(child, inside_function_def=True)
        elif isinstance(node, ast.Call) and not inside_function_def:
            # If we're at a call node and it's not inside a function definition, return True
            return True
        else:
            # For all other nodes, recursively visit their children and return True if any of them return True
            for child in ast.iter_child_nodes(node):
                if visit(child, inside_function_def):
                    return True
        # If no function call at the root level was found, return False
        return False

    try:
        tree = ast.parse(code)
        return visit(tree)
    except SyntaxError:
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
    if not is_runnable(filename):
        return {
            "success": False,
            "error": "The file is not runnable, or didn't compile.",
        }
    return validate_code(open(filename, "r").read())


def validate_code(code):
    if count_lines(code) == 0:
        return {
            "success": False,
            "error": "The file doesn't have any code in it.",
        }
    if has_functions_called(code) is False and contains_function_definition is False:
        return {
            "success": False,
            "error": "The file doesn't call any functions or have any functions. Please make sure the code meets the specifications and goals.",
        }
    if count_lines(code) == 1 and len(code) > 50:
        return {
            "success": False,
            "error": "The file has more than 50 characters but only one line, probably one massive comment or something.",
        }

    # if count_lines(code) < 4:
    #     return {
    #         "success": False,
    #         "error": "The file is not long enough to do much.",
    #     }

    # if "import" not in code:
    #     return {
    #         "success": False,
    #         "error": "The file doesn't have any imports. Imports are needed to do anything useful. Please add some imports to the top of the file.",
    #     }

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

    return {"success": True, "error": None}


def save_code(code, filename):
    try:
        code = format_code(code)
    except Exception as e:
        log(f"Code could not be formatted: {e}", title="save_code", type="warning")
    with open(filename, "w") as f:
        f.write(code)


def format_code(code: str, line_length: int = 110) -> str:
    """Format python code string with black.

    Parameters:
    code (str): The python code to be formatted.
    line_length (int): Maximum line length. Default is 88.

    Returns:
    str: The formatted python code.
    """
    return black.format_str(code, mode=black.FileMode(line_length=line_length))


def run_code(filename):
    process = subprocess.Popen(
        ["python", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    output = output.decode("utf-8")
    error = error.decode("utf-8")
    if error == "":
        error = None
    success = process.returncode == 0 and error == None
    return {"success": success, "error": error, "output": output}


def run_code_tests(script_path):
    """Run pytest on a given Python file."""

    # Run the command and get the output
    result = subprocess.run(
        ["python", "-m", "pytest", script_path], capture_output=True, text=True
    )
    if result.stderr == "" or result.stderr is None:
        result.stderr = False
    # Return the exit code. The exit code is 0 if the tests pass.
    return {
        "success": result.returncode == 0,
        "output": result.stdout,
        "error": result.stderr,
    }

def extract_imports(code, directory):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        log("Syntax error", title="extract_imports", type="warning", )
        return set()
    
    all_imports = []

    # List of built-in modules to be ignored
    builtin_modules = list(sys.builtin_module_names) + common_std_libs

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                package = alias.name.split(".")[0]  # only keep top-level package
                if package not in builtin_modules and not os.path.exists(
                    os.path.join(directory, f"{package}.py")
                ):
                    all_imports.append(package)
        elif isinstance(node, ast.ImportFrom):
            if node.level > 0:  # Skip relative imports
                continue
            if node.module is not None:
                package = node.module.split(".")[0]  # only keep top-level package
                if package not in builtin_modules and not os.path.exists(
                    os.path.join(directory, f"{package}.py")
                ):
                    all_imports.append(package)
    return set(all_imports)

common_std_libs = [
    "os",
    "sys",
    "math",
    "datetime",
    "json",
    "random",
    "re",
    "collections",
    "itertools",
    "functools",
    "pickle",
    "subprocess",
    "multiprocessing",
    "threading",
    "logging",
    "argparse",
    "shutil",
    "glob",
    "time",
    "pathlib",
    "socket",
    "asyncio",
    "csv",
    "urllib",
    "heapq",
    "hashlib",
    "base64",
    "timeit",
    "contextlib",
    "io"
]