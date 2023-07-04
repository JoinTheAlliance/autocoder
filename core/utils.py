import subprocess
import ast
import os

def log(filename, text):
    # if log folder doesn't exist, create it
    if not os.path.exists("logs"):
        os.makedirs("logs")
    # print to console
    print(text)
    # save to log.txt
    with open("logs/" + filename + ".log", "a") as f:
        f.write(text + "\n")

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


def compose_header(goal, reasoning=None):
    header = "# GOAL:\n"
    header += "\n".join(["# " + line for line in goal.split("\n")])
    # header += "#\n# REASONING:\n"
    # # remove any duplicate lines
    # if reasoning is not None:
    #     header = header + "\n".join(["# " + line for line in reasoning.split("\n")])
    # remove any duplicate lines
    header += "\n\n\n"
    # iterate through each line, if it was the same as the last line, remove it
    header = "\n".join(
        [
            line
            for line in header.split("\n")
            if line != header.split("\n")[header.split("\n").index(line) - 1]
        ]
    )

    return header


def strip_header(code):
    # remove any lines at the beginning that are whitespace only
    while code.startswith("\n"):
        code = code.split("\n", 1)[1]
    # remove any lines that start with # while code starts with #
    while code.startswith("#"):
        code = code.split("\n", 1)[1]
    # remove any lines at the beginning that are whitespace only
    while code.startswith("\n"):
        code = code.split("\n", 1)[1]
    return code


def install_imports(code):
    import_lines = [line for line in code.split("\n") if line.startswith("import")]
    import_lines = [line.split("as")[0] for line in import_lines]

    from_lines = [line for line in code.split("\n") if line.startswith("from")]
    # get the python module name
    # remove "from " and anything before import, also remove anything before .
    from_lines = [
        line.split("import")[0].split("from")[1].split(".")[-1].strip()
        for line in from_lines
    ]

    import_lines += from_lines
    

    for line in import_lines:
        print(f"ADDING PACKAGES TO SYSTEM: {line}")
        package = line.replace("import", "").strip()
        subprocess.call(["pip", "install", package])
        print(f"INSTALLED PACKAGE: {package}")


def read_code(filename):
    return open(filename, "r").read()


def save_code(code, filename):
    with open(filename, "w") as f:
        f.write(code)

def run_code(filename):
    log(filename, "RUNNING SIMULATION")

    process = subprocess.Popen(
        ["python3", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    output = output.decode("utf-8")
    error = error.decode("utf-8")
    if error:
        log(filename, "Error occurred while running the code:")
        log(filename, error)
    else:
        log(filename, "SIMULATION WAS SUCCESSFUL. Output:")
        log(filename, output)
    return [error, output]


def file_exists(filename):
    if subprocess.call(["test", "-f", filename]) == 0:
        return True
    else:
        return False


def count_lines(filename):
    file = open(filename, "r")
    lines = file.readlines()
    file.close()
    return len(lines)


def validate_file(filename, skip_import=False, skip_name_main_check=False):
    if not is_runnable(filename):
        return {
            "success": False,
            "revert": True,
            "explanation": "The file doesn't have any runnable code in it.",
        }

    if count_lines(filename) == 1 and len(read_code(filename)) > 50:
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

    if skip_import is False and "import" not in read_code(filename):
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

    if skip_name_main_check is False and "if __name__ == '__main__':" not in read_code(filename):
        return {
            "success": False,
            "revert": False,
            "explanation": "The file doesn't have a main function. Please add a main function and add tests to it..",
        }

    if "assert" not in read_code(filename):
        return {
            "success": False,
            "revert": False,
            "explanation": "The file doesn't have any tests. Please add tests to the main function using python's assert.",
        }
    
    if "# TODO" in read_code(filename):
        return {
            "success": False,
            "revert": False,
            "explanation": "The file has a TODO in it. Please remove the TODO before submitting.",
        }

    return {
            "success": True
        }


if __name__ == "__main__":
    # TESTS GO HERE
    pass  # replace me with tests!
