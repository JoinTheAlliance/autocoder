import os
import time
import zipfile
from pathlib import Path
import fnmatch
from agentlogger import log


def count_files(dir):
    # check if the dir exists
    if not os.path.exists(dir):
        log("Directory does not exist.", title="count_files", type="error")
        return 0
    count = len(
        [name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]
    )
    return count


def get_full_path(filepath, project_dir):
    """
    Takes a filepath and a project directory, and constructs a full path based on the inputs.
    Returns the absolute path to the file.

    :param filepath: The input filepath, which can include directories and a filename.
    :type filepath: str
    :param project_dir: The directory where the project files are located.
    :type project_dir: str
    :return: The absolute path to the file, given the filename.
    :rtype: str
    """
    filename = os.path.basename(filepath)
    directory_path = os.path.dirname(filepath)

    if not directory_path:
        directory_path = "."

    # Calculate the common path between project_dir and directory_path
    common_path = os.path.commonpath([project_dir, directory_path])

    # Remove the common_path from directory_path and join it with project_dir
    sub_path = directory_path.replace(common_path, "").lstrip(os.path.sep)
    full_path = os.path.join(project_dir, sub_path)

    if not os.path.exists(full_path):
        os.makedirs(full_path)

    full_path = os.path.join(full_path, filename)
    full_path = os.path.abspath(full_path)
    return full_path


def file_tree_to_dict(startpath):
    file_tree = {}
    for root, dirs, files in os.walk(startpath):
        rel_path = os.path.relpath(root, startpath)
        parent_dict = file_tree

        # Skip the root directory
        if rel_path == ".":
            rel_dirs = []
        else:
            rel_dirs = rel_path.split(os.sep)

        for d in rel_dirs[:-1]:  # traverse down to the current directory
            parent_dict = parent_dict.setdefault(d, {})

        if rel_dirs:  # if not at the root directory
            parent_dict[rel_dirs[-1]] = dict.fromkeys(files, None)
        else:  # at the root directory
            parent_dict.update(dict.fromkeys(files, None))

    return file_tree


def file_tree_to_string(startpath):
    tree_string = ""
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, "").count(os.sep)
        indent = " " * 4 * (level)
        tree_string += "{}{}/\n".format(indent, os.path.basename(root))
        subindent = " " * 4 * (level + 1)
        for f in files:
            tree_string += "{}{}\n".format(subindent, f)
    return tree_string


def get_python_files(startpath):
    py_files = []
    for root, dirnames, filenames in os.walk(startpath):
        for filename in fnmatch.filter(filenames, "*.py"):
            py_files.append(os.path.join(root, filename))
    return py_files


def zip_python_files(project_dir, project_name):
    # Check if ./.project_cache exists, create if not
    cache_dir = Path("./.project_cache")
    cache_dir.mkdir(exist_ok=True)

    # Check if "./.project_cache/{context["project_name"]}" dir exists, and create if not
    project_cache_dir = cache_dir / project_name
    project_cache_dir.mkdir(exist_ok=True)

    # create a timestamp
    epoch = int(time.time())

    # Create zip file path
    zip_file_path = f"{project_cache_dir}/{project_name}_{str(epoch)}.zip"

    # Create a zip file
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(project_dir):
            for file in files:
                if file.endswith(".py"):
                    # Get absolute path of the file
                    abs_file_path = os.path.join(root, file)
                    # Get relative path for storing in the zip
                    rel_file_path = os.path.relpath(abs_file_path, project_dir)
                    zipf.write(abs_file_path, arcname=rel_file_path)

    return zip_file_path
