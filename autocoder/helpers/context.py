import subprocess
from pathlib import Path
import pkg_resources
import sys
import ast

from autocoder.helpers.files import (
    count_files,
    file_tree_to_dict,
    file_tree_to_string,
    get_python_files,
    zip_python_files,
)
from autocoder.helpers.code import extract_imports, file_exists, run_code, run_code_tests, validate_file
from agentlogger import log


def get_file_count(context):
    project_dir = context["project_dir"]
    context["file_count"] = count_files(project_dir)
    return context


def read_and_format_code(context):
    # Read the contents of all python files and create a list of dicts
    project_files_str = "Project Files:"

    main_success = context.get("main_success", None)
    main_error = context.get("main_error", None)

    for project_dict in context["project_code"]:
        rel_path = project_dict["relative_path"]
        absolute_path = project_dict["absolute_path"]
        content = project_dict["content"]
        validation_success = project_dict["validation_success"]
        validation_error = project_dict["validation_error"]
        test_success = project_dict.get("test_success", None)
        test_error = project_dict.get("test_error", None)

        # adding file content to the string with line numbers
        project_files_str += "\n================================================================================\n"
        project_files_str += "Path (Relative): {}\nPath (Absolute): {}\n".format(
            str(rel_path), absolute_path
        )
        if "main.py" in str(rel_path):
            project_files_str += "(Project Entrypoint)\n"
            project_files_str += "Run Success: {}\n".format(main_success)
            if main_success is False:
                project_files_str += "Run Error: {}\n".format(main_error)
        project_files_str += "Validated: {}\n".format(validation_success)
        if validation_success is False:
            project_files_str += "Validation Error: {}\n".format(validation_error)
        if test_success is not None:
            project_files_str += "Tests Passed: {}\n".format(test_success)
        # if test_success is False:
        #     project_files_str += "Pytest Error: {}\n".format(test_error)
        project_files_str += "\nLine # ------------------------------ CODE -------------------------------------\n"
        for i, line in enumerate(content.split('\n')):
            project_files_str += "[{}] {}\n".format(i + 1, line)
        project_files_str += "\n================================================================================\n"

    context["project_code_formatted"] = project_files_str
    return context


def collect_files(context):
    project_dir = context["project_dir"]
    # create a file tree dict of all files
    context["filetree"] = file_tree_to_dict(project_dir)

    # format file tree to string
    context["filetree_formatted"] = file_tree_to_string(project_dir)

    # Create an array of paths to all python files
    context["python_files"] = get_python_files(project_dir)

    project_code = []

    for file_path in context["python_files"]:
        with open(file_path, "r") as file:
            content = file.read()
        rel_path = Path(file_path).relative_to(project_dir)

        file_dict = {
            "relative_path": str(rel_path),
            "absolute_path": file_path,
            "content": content,
        }
        project_code.append(file_dict)
    context["project_code"] = project_code

    return context


def validate_files(context):
    project_code = context["project_code"]
    project_validated = True
    for file_dict in project_code:
        file_path = file_dict["absolute_path"]
        validation = validate_file(file_path)
        file_dict["validation_success"] = validation["success"]
        file_dict["validation_error"] = validation["error"]
        if validation["success"] is False:
            project_validated = False
    context["project_code"] = project_code
    context["project_validated"] = project_validated
    return context


def run_tests(context):
    # get python files which don't contain test in their name

    # if not, error
    # call pytest on each file
    # no tests? error
    # tests failed? error
    # tests passed? success

    project_code = context["project_code"]

    project_code_notests = []
    project_code_tests = []
    project_tested = True
    # get python_files which also have test in the name
    for file_dict in project_code:
        file_path = file_dict["absolute_path"]
        if "test" in file_path:
            project_code_tests.append(file_dict)
        else:
            project_code_notests.append(file_dict)

    for file_dict in project_code_tests:
        file_path = file_dict["absolute_path"]
        test = run_code_tests(file_path)
        if test["success"] is False:
            project_tested = False
        file_dict["test_success"] = test["success"]
        file_dict["test_error"] = test["output"]
    context["project_tested"] = project_tested
    context["project_code"] = project_code_notests + project_code_tests
    return context


def run_main(context):
    project_code = context["project_code"]
    # get entry from project code where the relative path includes main.py
    main_file = None
    for file_dict in project_code:
        if "main.py" in file_dict["relative_path"]:
            file_dict["test_success"] = None
            main_file = file_dict

    if main_file is None:
        return context

    result = run_code(main_file["absolute_path"])

    context["main_success"] = result["success"]
    if result["success"] is False:
        context["main_error"] = result["error"]
    else:
        context["main_error"] = None
    context["main_output"] = result["output"]

    return context


def collect_errors(context):
    # get all errors from project_code
    project_code = context["project_code"]
    project_errors = []
    for file_dict in project_code:
        if file_dict.get("validation_success") is False:
            project_errors.append(str(file_dict["relative_path"]) + ": " + str(file_dict["validation_error"]))
        if file_dict.get("test_success") is False:
            project_errors.append(str(file_dict["relative_path"]) + ": " + str(file_dict["test_error"]))
    # add main_error
    if context.get("main_success") is False:
        project_errors.append(str(context["main_error"]))
    context["errors"] = project_errors

    # format errors
    error_str = ""
    for error in project_errors:
        error_str += f"{error}\n"
    if error_str != "":
        context["errors_formatted"] = error_str
    else:
        context["errors_formatted"] = ""
    return context


def backup_project(context):
    project_dir = context["project_dir"]
    project_name = context["project_name"]
    context["backup"] = zip_python_files(project_dir, project_name)
    return context


def handle_packages(context):
    debug = context.get("log_level", "normal") == "debug"
    should_log = context.get("log_level", "normal") != "quiet"
    
    # Get the set of standard library modules
    std_module_set = set(sys.builtin_module_names)

    packages = []
    
    # get the content from every entry in project_code
    project_code = context["project_code"]
    project_dir = context["project_dir"]

    for file_dict in project_code:
        try:
            ast.parse(file_dict["content"])
        except SyntaxError:
            log("Couldn't parse file to extract imports", title="extract_imports", type="warning", log=debug)
        imports = list(extract_imports(file_dict["content"], file_dict["absolute_path"]))
        if len(imports) > 0:
            packages = list(packages) + imports

    # Get a list of currently installed packages
    installed = {pkg.key for pkg in pkg_resources.working_set}
    installed_packages = []

    # Loop through the packages
    for package in packages:
        # Check if package is installed and it is not a built-in package
        if package not in installed and package not in std_module_set:
            # Install missing package
            try:
                result = subprocess.run(
                    ["python", "-m", "pip", "install", package],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=True,
                )
                installed_packages.append(package)

            except subprocess.CalledProcessError as e:
                # Check if the error message contains the expected error
                if (
                    "Could not find a version that satisfies the requirement"
                    in e.stderr
                ):
                    # Extract the package name from the error message
                    error_package = e.stderr.split(" ")[10]
                    packages.remove(error_package)

    if len(installed_packages) > 0:
        log(
            f"Installing packages: {packages}",
            title="packages",
            type="system",
            log=should_log,
        )

    # for each package in packages, add to project_dir/requirements.txt
    # with open(f"{project_dir}/requirements.txt", "w") as f:
    #     # Only add to requirements.txt if it's not a built-in package
    #     f.write("\n".join([p for p in packages if p not in std_module_set]))

    return context
