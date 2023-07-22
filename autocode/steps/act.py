import os
from easycompletion import compose_function, compose_prompt, openai_function_call
from autocode.helpers.context import handle_packages

from autocode.helpers.files import get_full_path
from agentlogger import log

create_prompt = """
This is my project goal:
{{goal}}

Task: Create a Python module that meets the stated goals, along with a set of tests for that module.
You should include the following details
- Plan: Think about the best approach and write out a reasoning. Explain your reasoning.
- Code: The full code for main.py, including all imports and code.
    - There should be a main function which is called if __name__ == '__main__'
    - Use a functional style, with no global variables or classes unless absolutely necessary
    - All code should be encapsulated in functions which can be tested
- Packages: A list of packages to install, derived from the imports of the code. 
- Test: The full code for main_test.py, including all imports and code. Tests should use a functional style, use the assert keyword run with pytest.
    - All tests should be in their own functions and have setup and teardown so that they are isolated from each other.
    - There should be multiple tests for each function in main.py, including tests for edge cases, different argument cases and failure cases.
"""

edit_prompt = """
{{goal}}
{{project_code_formatted}}
{{reasoning}}
{{error}}
{{available_actions}}
Please use a function from the available functions.
"""

create_function = compose_function(
    name="create",
    description="Create a new script called main.py, as well as a test for main.py named main_test.py.",
    properties={
        "reasoning": {
            "type": "string",
            "description": "Think about the best approach and write out a reasoning. Explain your reasoning.",
        },
        "code": {
            "type": "string",
            "description": "The full code for main.py, including all imports and code",
        },
        "packages": {
            "type": "array",
            "description": "A list of packages to install, derived from the imports of the code.",
            "items": {"type": "string"},
        },
        "test": {
            "type": "string",
            "description": "The full code for main_test.py, including all imports and code. Tests should use a functional style with the assert keyword for pytest.",
        },
    },
    required_properties=["reasoning", "code", "packages", "test"],
)


def create_handler(arguments, context):
    should_log = not context.get("quiet") or context.get("debug")
    reasoning = arguments["reasoning"]
    code = arguments["code"]
    packages = arguments["packages"]
    test = arguments["test"]

    project_dir = context["project_dir"]

    log(
        f"Creating main.py in {project_dir}"
        + f"\n\nReasoning:\n{reasoning}"
        + f"\n\nCode:\n{code}"
        + f"\n\nTest:\n{test}",
        title="action",
        type="create",
        log=should_log,
    )

    # save code to main.py
    with open(f"{project_dir}/main.py", "w") as f:
        f.write(code)

    # save test to main_test.py
    with open(f"{project_dir}/main_test.py", "w") as f:
        f.write(test)

    context["packages"] = packages

    return context


def write_complete_script_handler(arguments, context):
    should_log = not context.get("quiet") or context.get("debug")
    reasoning = arguments["reasoning"]
    code = arguments["code"]
    filepath = arguments["filepath"]
    packages = arguments.get("packages", [])
    write_path = get_full_path(filepath, context["project_dir"])

    log(
        f"Writing complete script to {write_path}"
        + f"\n\nReasoning:\n{reasoning}"
        + f"\n\nCode:\n{code}",
        title="action",
        type="write",
        log=should_log,
    )

    with open(write_path, "w") as f:
        f.write(code)
    context["packages"] = packages
    return context


def insert_code_handler(arguments, context):
    should_log = not context.get("quiet") or context.get("debug")
    reasoning = arguments["reasoning"]
    code = arguments["code"]
    line_number = arguments["line_number"]
    packages = arguments.get("packages", [])
    filepath = arguments["filepath"]
    write_path = get_full_path(filepath, context["project_dir"])

    log(
        f"Inserting code into {write_path} at line {line_number}"
        + f"\n\nReasoning:\n{reasoning}"
        + f"\n\nCode:\n{code}",
        title="action",
        type="insert",
        log=should_log,
    )

    with open(write_path, "r") as f:
        text = f.read()
    lines = text.split("\n")
    lines.insert(line_number, code)
    text = "\n".join(lines)

    log(f"New code:\n{text}", title="action", type="insert", log=should_log)

    with open(write_path, "w") as f:
        f.write(text)
    context["packages"] = packages
    return context


def replace_code_handler(arguments, context):
    should_log = not context.get("quiet") or context.get("debug")
    reasoning = arguments["reasoning"]
    code = arguments["code"]
    start_line = int(arguments["start_line"])
    end_line = int(arguments["end_line"])
    packages = arguments.get("packages", [])
    filepath = arguments["filepath"]
    write_path = get_full_path(filepath, context["project_dir"])

    log(
        f"Replacing code in {write_path} from line {start_line} to {end_line}"
        + f"\n\nReasoning:\n{reasoning}"
        + f"\n\nCode:\n{code}",
        title="action",
        type="replace",
        log=should_log,
    )

    # Replace the code between start_lines and end_lines with new code
    with open(write_path, "r") as f:
        lines = f.readlines()
        lines[start_line - 1 : end_line] = [code]  # python's list indices start at 0

    lines = "\n".join(lines)

    log(f"New code:\n{lines}", title="action", type="replace", log=should_log)

    with open(write_path, "w") as f:
        f.write(lines)

    context["packages"] = packages
    return context


def remove_code_handler(arguments, context):
    should_log = not context.get("quiet") or context.get("debug")
    reasoning = arguments["reasoning"]
    start_line = int(arguments["start_line"])
    end_line = int(arguments["end_line"])
    filepath = arguments["filepath"]
    write_path = get_full_path(filepath, context["project_dir"])

    log(
        f"Removing code in {write_path} from line {start_line} to {end_line}"
        + f"\n\nReasoning:\n{reasoning}",
        title="action",
        type="remove",
        log=should_log,
    )

    # Remove the code between start_lines and end_lines
    with open(write_path, "r") as f:
        lines = f.readlines()
        del lines[start_line - 1 : end_line]  # python's list indices start at 0

    lines = "\n".join(lines)

    log(f"New code:\n{lines}", title="action", type="remove", log=should_log)

    with open(write_path, "w") as f:
        f.write(lines)

    return context


def create_new_file_handler(arguments, context):
    should_log = not context.get("quiet") or context.get("debug")
    reasoning = arguments["reasoning"]
    filepath = arguments["filepath"]
    code = arguments["code"]
    test = arguments["test"]
    packages = arguments.get("packages", [])

    log(
        f"Creating new file {filepath}"
        + f"\n\nReasoning:\n{reasoning}"
        + f"\n\nCode:\n{code}"
        + f"\n\nTest:\n{test}",
        title="action",
        type="create",
        log=should_log,
    )

    # Create a new file at filepath with code
    code_path = get_full_path(filepath, context["project_dir"])
    with open(code_path, "w") as f:
        f.write(code)

    # Create a new file at filepath_test.py with test
    test_path = get_full_path(
        f"{os.path.splitext(filepath)[0]}_test.py", context["project_dir"]
    )
    with open(test_path, "w") as f:
        f.write(test)

    context["packages"] = packages

    return context


def get_actions():
    return [
        {
            "function": compose_function(
                name="insert_code",
                description="Insert a snippet of code before a line. This is useful for inserting a function, for example, although if the functio needs to be called, write_complete_module is probably a better choice.",
                properties={
                    "reasoning": {
                        "type": "string",
                        "description": "What does this code do? Why are you inserting it, and into which file? Please explain as though this is a code review on a pull request.",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "The relative path of the file to insert code into, including .py. Must be an existing file from the provided project directory.",
                    },
                    "code": {
                        "type": "string",
                        "description": "The snippet of code to insert.",
                    },
                    "line_number": {
                        "type": "number",
                        "description": "The line number to insert the code before.",
                    },
                    "packages": {
                        "type": "array",
                        "description": "A list of packages to install, derived from the imports of the code.",
                        "items": {"type": "string"},
                    },
                },
                required_properties=["reasoning", "filepath", "code", "line_number"],
            ),
            "handler": insert_code_handler,
        },
        {
            "function": compose_function(
                name="replace_code",
                description="Replace lines in the original code with a new snippet of code.",
                properties={
                    "reasoning": {
                        "type": "string",
                        "description": "Which code are you replacing? What does the new code do? Why are you replacing it?",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "The relative path of the file to insert code into, including .py.",
                    },
                    "code": {
                        "type": "string",
                        "description": "The snippet of code to replace the existing code with.",
                    },
                    "start_line": {
                        "type": "number",
                        "description": "The start line number of the file where code is being replaced.",
                    },
                    "end_line": {
                        "type": "number",
                        "description": "The end line number of the file where code is being replaced.",
                    },
                    "packages": {
                        "type": "array",
                        "description": "A list of packages to install, derived from the imports of the code.",
                        "items": {"type": "string"},
                    },
                },
                required_properties=[
                    "reasoning",
                    "filepath",
                    "code",
                    "start_line",
                    "end_line",
                ],
            ),
            "handler": replace_code_handler,
        },
        {
            "function": compose_function(
                name="write_complete_module",
                description="Writes a python module, including imports and functions.",
                properties={
                    "reasoning": {
                        "type": "string",
                        "description": "What does this code do? Why are you rewriting it? How will this change the behavior of the script?",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "The relative path of the file where the code will be written, including .py. Must be an existing file from the provided project directory. Must include imports, functions and all code with no abbreviations.",
                    },
                    "packages": {
                        "type": "array",
                        "description": "A list of packages to install, derived from the imports of the code.",
                        "items": {"type": "string"},
                    },
                    "code": {
                        "type": "string",
                        "description": "The complete module code to write.",
                    },
                },
                required_properties=["reasoning", "filepath", "code"],
            ),
            "handler": write_complete_script_handler,
        },
        {
            "function": compose_function(
                name="remove_code",
                description="Removes a range of lines from the code. Requires a start and end line number.",
                properties={
                    "reasoning": {
                        "type": "string",
                        "description": "Why are you removing this code?",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "The relative path of the file to remove code from, including .py. Must be an existing file from the provided project directory.",
                    },
                    "start_line": {
                        "type": "number",
                        "description": "The start line number of the code to remove.",
                    },
                    "end_line": {
                        "type": "number",
                        "description": "The end line number of the code to remove.",
                    },
                },
                required_properties=["reasoning", "start_line", "end_line"],
            ),
            "handler": remove_code_handler,
        },
        {
            "function": compose_function(
                name="create_new_file",
                description="Create a Python file",
                properties={
                    "reasoning": {
                        "type": "string",
                        "description": "Think about the best approach and write out a reasoning. Explain your reasoning.",
                    },
                    "filepath": {
                        "type": "string",
                        "description": "The relative path of the file to create, starting with './' and ending with '.py'. Should be relative to the project directory",
                    },
                    "code": {
                        "type": "string",
                        "description": "The full code for the module names <filename>, including all imports and code",
                    },
                    "packages": {
                        "type": "array",
                        "description": "A list of packages to install, derived from the imports of the code.",
                        "items": {"type": "string"},
                    },
                    "test": {
                        "type": "string",
                        "description": "The full code for <filename>_test.py, which is a set of functional pytest-compatible tests for the module code, including all imports and code.",
                    },
                },
                required_properties=[
                    "reasoning",
                    "filepath",
                    "code",
                    "test",
                ],
            ),
            "handler": create_new_file_handler,
        },
    ]


def step(context):
    """
    This function serves as the 'Act' stage in the OODA loop. It executes the selected action from the 'Decide' stage.

    Args:
        context (dict): The dictionary containing data about the current state of the system, including the selected action to be taken.

    Returns:
        dict: The updated context dictionary after the 'Act' stage, which will be used in the next iteration of the OODA loop.
    """

    prompt = edit_prompt
    actions = get_actions()

    quiet = context.get("quiet")
    debug = context.get("debug")

    should_log = not quiet or debug

    # each entry in functions is a dict
    # # get the "fuction" value from each entry in the function list
    functions = [f["function"] for f in actions]

    if context["file_count"] == 0:
        prompt = create_prompt
        functions = [create_function]

    header = (
        "Available functions:"
        + ", ".join([fn["function"]["name"] for fn in actions])
        + "\n"
    )

    context["available_actions"] = header + "\n".join(
        [f"{fn['function']['name']}: {fn['function']['description']}" for fn in actions]
    )

    if context.get("error") is None:
        # find {{error}} in prompt and replace with empty string
        prompt = prompt.replace("{{error}}", "")

    if context.get("reasoning") is None:
        # find {{reasoning}} in prompt and replace with empty string
        prompt = prompt.replace("{{reasoning}}", "")
    else:
        log(
            f"Reasoning:\n{context['reasoning']}",
            title="action",
            type="reasoning",
            log=should_log,
        )

    text = compose_prompt(prompt, context)

    log(f"Prompt:\n{text}", title="action", type="prompt", log=debug)

    response = openai_function_call(text=text, functions=functions)

    log(
        f"Response:\n{str(response)}",
        title="action",
        type="response",
        color="debug",
        log=debug,
    )

    # find the function in functions with the name that matches response["function_name"]
    # then call the handler with the arguments and context
    function_name = response["function_name"]

    # if function_name is create, then we need to create a new file
    if function_name == "create":
        create_handler(response["arguments"], context)
        return context

    arguments = response["arguments"]
    action = None

    for f in actions:
        if f["function"]["name"] == function_name:
            action = f
            break

    log(
        f"Running action {function_name} with arguments:\n{str(arguments)}",
        title="action",
        type="handler",
        log=debug,
    )

    # call the handler with the arguments and context
    context = action["handler"](arguments, context)

    # install any new imports if there are any
    context = handle_packages(context)

    return context
