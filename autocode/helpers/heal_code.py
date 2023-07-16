import os

from autocode.helpers.code import (
    read_code,
    strip_header,
    compose_header,
)


def heal_code(filename, code, previous_code, goal, reasoning):
    code_backup = code
    code = strip_header(code)
    previous_code = strip_header(previous_code)

    code_lines = code.split("\n")
    previous_code_lines = previous_code.split("\n")

    # find footer in the code
    footer_line = next((line for line in code_lines if "__name__" in line), None)
    previous_footer_line = next(
        (line for line in previous_code_lines if "__name__" in line), None
    )

    new_code_has_footer = footer_line is not None
    previous_code_has_footer = previous_footer_line is not None

    if new_code_has_footer:
        footer = "\n".join(code_lines[code_lines.index(footer_line) :])
    else:
        footer = None

    if previous_code_has_footer:
        previous_footer = "\n".join(
            previous_code_lines[previous_code_lines.index(previous_footer_line) :]
        )
    else:
        previous_footer = None

    has_new_footer = (
        new_code_has_footer and previous_code_has_footer and footer != previous_footer
    )

    footer_snippet = None
    if has_new_footer:
        if "..." in footer:
            footer_snippet = footer.split("...")[1]
            if footer_snippet.strip() == "":
                footer_snippet = None
                print("footer_snippet is empty")
        elif code_lines.index(footer_line) < 4:
            footer_snippet = footer.split("\n")
        if footer_snippet is not None and footer_line in footer_snippet:
            print("footer_snippet before:", footer_snippet)
            footer_snippet = footer_snippet.split(footer_line)[1]
            print("footer_snippet after:", footer_snippet)

        if footer_snippet is not None:
            code = code + "\n" + footer_snippet
        else:
            code_lines = code_lines[: code_lines.index(footer_line)]
            code = "\n".join(code_lines) + "\n" + footer
    if new_code_has_footer is False and previous_code_has_footer is False:
        code = (
            code
            + "\n\nif __name__ == '__main__':\n    # TODO: ADD TESTS HERE\n    assert(False)"
        )

    import_lines = [line for line in code.split("\n") if line.startswith("import")]
    from_import_lines = [line for line in code.split("\n") if line.startswith("from")]

    import_lines = [
        line.split(" as")[0].split("import")[1].split(".")[-1].strip()
        for line in import_lines
    ]

    # from_import_lines start with "from <package>.<subpackage> import <module> or from <package> import <module>"
    # we want to get the <package> part
    from_import_lines = [
        line.split("import")[0].split("from")[1].split(".")[0].strip()
        for line in from_import_lines
    ]

    import_lines += from_import_lines

    previous_import_lines = [
        line for line in previous_code.split("\n") if line.startswith("import")
    ]

    previous_from_import_lines = [
        line for line in previous_code.split("\n") if line.startswith("from")
    ]

    previous_import_lines = [
        line.split(" as")[0].split("import")[1].split(".")[-1].strip()
        for line in previous_import_lines
    ]

    previous_from_import_lines = [
        line.split("import")[0].split("from")[1].split(".")[0].strip()
        for line in previous_from_import_lines
    ]

    previous_import_lines += previous_from_import_lines

    new_code_has_imports = len(import_lines) > 0
    previous_code_has_imports = len(previous_import_lines) > 0

    if new_code_has_imports == False and previous_code_has_imports == False:
        return {"code": code_backup, "new_imports": None, "success": False}

    new_imports = new_code_has_imports == True and previous_code_has_imports == False

    if (
        new_imports == False
        and new_code_has_imports == True
        and previous_code_has_imports == True
    ):
        new_imports = any(
            [import_line not in previous_import_lines for import_line in import_lines]
        )

    if new_imports == True:
        new_imports = set(import_lines)
        code_lines = [line for line in code_lines if not line.startswith("import")] + [
            line for line in code_lines if not line.startswith("from")
        ]
        for line in code_lines:
            for previous_import_line in previous_import_lines:
                if previous_import_line in line:
                    new_imports.add(previous_import_line)

        code_lines = list(new_imports) + code_lines
        code = "\n".join(code_lines)

    code = compose_header(goal, reasoning) + code

    print("final footer snippet:", footer_snippet)

    # if there is a ... in the code, and it's not in a comment, then we probably lost some code
    if "..." in code and "#" not in code.split("...")[0]:
        return {
            "code": code_backup,
            "new_imports": new_imports,
            "success": False,
        }

    if code == code_backup:
        return {"code": code, "new_imports": new_imports, "success": False}

    return {"code": code, "new_imports": new_imports, "success": True}


if __name__ == "__main__":

    def create_test_file(filename, imports, footer):
        with open(filename, "w") as f:
            f.write(imports + "\n\n" + footer)

    # Test 1
    print("Running Test 1...")
    imports = "import os\nimport sys"
    footer = 'if __name__ == "__main__":\n    print("Hello, World!")'
    create_test_file("old.py", imports, footer)
    create_test_file("new.py", imports, footer)

    result = heal_code(
        "test1", read_code("new.py"), read_code("old.py"), "goal", "reasoning"
    )
    assert result["success"] == True, f"Test 1 failed with {result}"

    # Cleanup
    os.remove("old.py")
    os.remove("new.py")
    print("All tests passed!")
