import subprocess
import importlib.util


def check_if_builtin(module_name):
    # Try to find a built-in module with the provided name
    spec = importlib.util.find_spec(module_name)

    # If the spec exists and the module is built-in
    if spec and spec.origin == "built-in":
        return True

    # If the module isn't found or isn't built-in
    return False


def install_imports(code):
    import_lines = get_imports(code)
    for line in import_lines:
        package = line.replace("import", "").strip()
        subprocess.call(["pip", "install", package])
        print(f"INSTALLED PACKAGE: {package}")


def get_imports(code):
    # Split the code into lines
    lines = [line.strip() for line in code.split("\n")]

    # Find import lines
    imports = [
        line.split(" as")[0].replace("import", "").strip()
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
    user_imports = sorted(
        [imp for imp in all_imports if check_if_builtin(imp) is False]
    )

    return user_imports


if __name__ == "__main__":
    example_code = "import os\nimport numpy as np\nimport numpy as np\nfrom pandas.core import series\nfrom pysmt import typings"
    print("imports:", get_imports(example_code))
    print(get_imports(example_code))
    # write a test for get_imports using example code
    assert get_imports(example_code) == ["numpy", "pandas", "pysmt"]
