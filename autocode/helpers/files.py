import os
import time
import zipfile
from pathlib import Path
import fnmatch


def count_files(dir):
    # check if the dir exists
    if not os.path.exists(dir):
        print("Directory does not exist.")
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

    if directory_path:  # there are directories in filepath
        full_path = os.path.join(project_dir, directory_path)
        if not os.path.exists(full_path):  # directories don't exist yet
            # check for overlapping directory names
            proj_dirs = set(project_dir.split(os.path.sep))
            dir_path_dirs = set(directory_path.split(os.path.sep))
            overlap = proj_dirs & dir_path_dirs
            if overlap:
                # find the index of the overlapping directory in the project directory
                overlap_dir = overlap.pop()
                index = project_dir.split(os.path.sep).index(overlap_dir)
                # consolidate paths
                full_path = os.path.join(project_dir.split(os.path.sep)[0 : index + 1])
                full_path = os.path.join(
                    full_path, directory_path.split(os.path.sep)[index + 1 :]
                )
                full_path = os.path.join(full_path, filename)
            else:
                # create directories until the path exists
                os.makedirs(full_path)
    else:  # there are no directories in filepath, just a filename
        full_path = os.path.join(project_dir, filename)

    absolute_path = os.path.abspath(full_path)
    return absolute_path


def file_tree_to_dict(startpath):
    file_tree = {}
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, "").count(os.sep)
        if level > 0:
            branch = dict.fromkeys(files)
            parent = startpath.split(os.sep)
            leaf = file_tree
            for subdir in parent[1:]:
                leaf = leaf[subdir]
            leaf[os.path.basename(root)] = branch
        else:
            file_tree[os.path.basename(root)] = dict.fromkeys(files)
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
