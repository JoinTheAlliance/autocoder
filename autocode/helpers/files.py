import os
import zipfile
from pathlib import Path
import fnmatch


def count_files(dir):
    len([name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))])


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


def zip_python_files(project_dir, project_name, epoch):
    # Check if ./.project_cache exists, create if not
    cache_dir = Path("./.project_cache")
    cache_dir.mkdir(exist_ok=True)

    # Check if "./.project_cache/{context["project_name"]}" dir exists, and create if not
    project_cache_dir = cache_dir / project_name
    project_cache_dir.mkdir(exist_ok=True)

    # Create zip file path
    zip_file_path = project_cache_dir / f"{project_name}_{str(epoch)}.zip"

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
