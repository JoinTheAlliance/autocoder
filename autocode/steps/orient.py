from agentevents import (
    increment_epoch,
)

from pathlib import Path

from autocode.helpers.files import (
    count_files,
    file_tree_to_dict,
    file_tree_to_string,
    get_python_files,
    zip_python_files,
)


def update_epoch(context):
    epoch = increment_epoch()
    context["epoch"] = epoch
    context["last_epoch"] = str(epoch - 1)
    return context


def get_file_count(context):
    project_dir = context["project_dir"]
    context["file_count"] = count_files(project_dir)
    return context


def read_and_format_code(context):
    # Read the contents of all python files and create a list of dicts
    project_files_str = "Project Files:\n"

    for project_dict in context["project_code"]:
        rel_path = project_dict["rel_path"]
        file_path = project_dict["file_path"]
        content = project_dict["content"]
        valid = project_dict["valid"]

        # adding file content to the string with line numbers
        project_files_str += "\n================================================\n"
        project_files_str += "File: {}\nPath: {}\n".format(str(rel_path), file_path)
        project_files_str += "Valid: {}\n".format(valid)
        if valid is False:
            project_files_str += "Error: {}\n".format(
                project_dict.get("error", "None found")
            )
        project_files_str += "\n+----------------------------------------------+\n"
        for i, line in enumerate(content):
            project_files_str += "[{}] {}".format(i + 1, line)
        project_files_str += "\n================================================\n"

    context["project_code_formatted"] = project_files_str
    return context


def collect_files(context):
    project_dir = context["project_dir"]
    # create a file tree dict of all files
    context["filetree"] = file_tree_to_dict(project_dir)

    # format file tree to string
    context["filetree_formatted"] = file_tree_to_string(project_dir)

    # Create an array of paths to all python files
    context["get_python_files"] = get_python_files(project_dir)

    project_code = []

    for file_path in context["get_python_files"]:
        with open(file_path, "r") as file:
            content = file.readlines()
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
    # TODO: Validate files
    project_code = context["project_code"]
    for file_dict in project_code:
        # TODO: dont just pass through
        file_dict["valid"] = True
    context["project_code"] = project_code
    return context


def run_tests(context):
    # call pytest
    # no tests? error
    # tests failed? error
    # tests passed? success
    context["test_success"] = True
    context["test_errors"] = []
    return context


def run_main(context):
    # call pytest
    # no tests? error
    # tests failed? error
    # tests passed? success
    context["main_success"] = True
    context["main_error"] = None
    return context


def backup_project(context):
    project_dir = context["project_dir"]
    project_name = context["project_name"]
    epoch = context["epoch"]
    context["last_state"] = zip_python_files(project_dir, project_name, epoch)
    return context


def orient(context):
    """
    This function serves as the 'Orient' stage in the OODA loop. It uses the current context data to summarize the previous epoch and formulate a plan for the next steps.

    Args:
        context (dict): The dictionary containing data about the current state of the system.

    Returns:
        dict: The updated context dictionary after the 'Orient' stage, including the summary of the last epoch, relevant knowledge, available actions, and so on.
    """
    context = update_epoch(context)
    context = get_file_count(context)

    # New path
    if context["file_count"] == 0:
        return context

    # Collect existing file name
    context = collect_files(context)

    context = validate_files(context)

    context = run_tests(context)

    context = run_main(context)

    context = read_and_format_code(context)

    return context
