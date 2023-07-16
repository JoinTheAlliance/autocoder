import subprocess

def compose_header(goal, reasoning=None):
    header = "# GOAL:\n"
    header += "\n".join(["# " + line for line in goal.split("\n")])
    # header += "#\n# REASONING:\n"
    # # remove any duplicate lines
    # if reasoning is not None:
    #     header = header + "\n".join(["# " + line for line in reasoning.split("\n")])
    # remove any duplicate lines
    header += "\n\n\n"
    # iterate through each line, if it was the same as xthe last line, remove it
    header = "\n".join(
        [
            line
            for line in header.split("\n")
            if line != header.split("\n")[header.split("\n").index(line) - 1]
        ]
    )

    return header


def strip_header(code):
    if code is None:
        print("Error, can't strip header, code is None")
        return code
    if len(code.split("\n")) == 1 and code.startswith("#"):
        print("Error, can't strip header, code is only one line and it's a comment")
        return code
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


def read_code(filename):
    return open(filename, "r").read()


def save_code(code, filename):
    with open(filename, "w") as f:
        f.write(code)


def run_code(filename):
    process = subprocess.Popen(
        ["python3", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    output = output.decode("utf-8")
    error = error.decode("utf-8")
    return [error, output]

