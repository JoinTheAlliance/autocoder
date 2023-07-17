import subprocess


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
    if error == "":
        error = None
    success = process.returncode == 0 and error == None
    return {"success": success, "error": error, "output": output}


def test_code(filepath):
    """Run pytest on a given Python file."""
    
    # Create the command
    command = ["pytest", filepath]

    # Run the command and get the output
    result = subprocess.run(command, capture_output=True, text=True)

    # Return the exit code. The exit code is 0 if the tests pass.
    return { "success": result.returncode == 0, "output": result.stdout, "error": result.stderr }