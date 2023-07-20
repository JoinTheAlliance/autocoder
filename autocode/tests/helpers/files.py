import os
import tempfile
import shutil
from pathlib import Path
import zipfile
from autocode.helpers.files import (
    count_files,
    file_tree_to_dict,
    file_tree_to_string,
    get_full_path,
    get_python_files,
    zip_python_files,
)


def test_count_files():
    dirpath = tempfile.mkdtemp()
    open(os.path.join(dirpath, "file1.txt"), "w").close()
    open(os.path.join(dirpath, "file2.txt"), "w").close()
    open(os.path.join(dirpath, "file3.txt"), "w").close()

    assert count_files(dirpath) == 3

    # Clean up
    shutil.rmtree(dirpath)

    # Test with non-existing directory
    assert count_files("nonexistingdirectory") == 0


def test_get_full_path():
    # TODO: does't work, needs to be tested with a real project?
    project_dir = "/home/user/project"
    filepath = "subdir/file.txt"
    expected_full_path = "/home/user/project/subdir/file.txt"

    assert get_full_path(filepath, project_dir) == expected_full_path


def test_file_tree_to_dict():
    # create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.makedirs(os.path.join(tmpdirname, "dir1/dir2"))
        open(os.path.join(tmpdirname, "file1.txt"), "w").close()
        open(os.path.join(tmpdirname, "dir1/file2.txt"), "w").close()
        open(os.path.join(tmpdirname, "dir1/dir2/file3.txt"), "w").close()

        file_tree = file_tree_to_dict(tmpdirname)
        expected_tree = {
            "file1.txt": None,
            "dir1": {"file2.txt": None, "dir2": {"file3.txt": None}},
        }

        assert file_tree == expected_tree


def test_file_tree_to_string():
    # create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.makedirs(os.path.join(tmpdirname, "dir1/dir2"))
        open(os.path.join(tmpdirname, "file1.txt"), "w").close()
        open(os.path.join(tmpdirname, "dir1/file2.txt"), "w").close()
        open(os.path.join(tmpdirname, "dir1/dir2/file3.txt"), "w").close()

        file_tree_str = file_tree_to_string(tmpdirname)
        assert "dir1/\n" in file_tree_str
        assert "dir2/\n" in file_tree_str
        assert "file1.txt\n" in file_tree_str
        assert "file2.txt\n" in file_tree_str
        assert "file3.txt\n" in file_tree_str


def test_get_python_files():
    dirpath = tempfile.mkdtemp()
    open(os.path.join(dirpath, "file1.py"), "w").close()
    open(os.path.join(dirpath, "file2.py"), "w").close()
    open(os.path.join(dirpath, "file3.txt"), "w").close()

    py_files = get_python_files(dirpath)
    assert len(py_files) == 2
    assert all([f.endswith(".py") for f in py_files])

    # Clean up
    shutil.rmtree(dirpath)


def test_zip_python_files():
    project_dir = tempfile.mkdtemp()
    open(os.path.join(project_dir, "file1.py"), "w").close()
    open(os.path.join(project_dir, "file2.py"), "w").close()
    open(os.path.join(project_dir, "file3.txt"), "w").close()

    zip_file_path = zip_python_files(project_dir, "test_project")

    assert Path(zip_file_path).is_file()

    # Check the zip file contents
    with zipfile.ZipFile(zip_file_path, "r") as zipf:
        assert len(zipf.namelist()) == 2
        assert all([f.endswith(".py") for f in zipf.namelist()])

    # Clean up
    shutil.rmtree(project_dir)
    os.remove(zip_file_path)
