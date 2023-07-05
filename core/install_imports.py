import subprocess


system_packages = [
    "os",
    "sys",
    "re",
    "math",
    "random",
    "time",
    "datetime",
    "json",
    "csv",
    "glob",
    "pickle",
    "subprocess",
    "shutil",
    "itertools",
    "collections",
    "functools",
    "operator",
    "pprint",
    "logging",
    "warnings",
    "inspect",
    "copy",
    "gc",
    "traceback",
    "types",
    "asyncio",
    "unittest",
    "doctest",
    "timeit",
    "string",
    "hashlib",
    "getpass",
    "argparse",
    "logging",
]


def install_imports(code):
    import_lines = get_imports(code)
    for line in import_lines:
        print(f"ADDING PACKAGES TO SYSTEM: {line}")
        package = line.replace("import", "").strip()
        subprocess.call(["pip", "install", package])
        print(f"INSTALLED PACKAGE: {package}")


def get_imports(code):
    # Split the code into lines
    lines = [line.strip() for line in code.split("\n")]

    # Find import lines
    imports = [
        line.split("as")[0].replace("import", "").strip()
        for line in lines
        if line.startswith("import")
    ]

    # Find 'from' import lines
    from_imports = [
        line.split("import")[0].replace("from", "").strip()
        for line in lines
        if line.startswith("from")
    ]

    # Combine, deduplicate, and remove submodules
    all_imports = list(set(imports + from_imports))
    all_imports = [imp.split(".")[0] if "." in imp else imp for imp in all_imports]

    # Exclude system packages, and sort
    user_imports = sorted([imp for imp in all_imports if imp not in system_packages])

    return user_imports


if __name__ == "__main__":
    example_code = "import os\nimport numpy as np\nimport numpy as np\nfrom pandas.core import series\nfrom pysmt import typings"
    print("imports:", get_imports(example_code))
    print(get_imports(example_code))
    # write a test for get_imports using example code
    assert get_imports(example_code) == ["numpy", "pandas", "pysmt"]
