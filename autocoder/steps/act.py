import os
import re
from easycompletion import compose_function, compose_prompt, openai_function_call, trim_prompt
from termcolor import colored
from autocoder.helpers.code import save_code
from autocoder.helpers.context import handle_packages

from autocoder.helpers.files import get_full_path
from agentlogger import log

create_file_prompt = """\
The above is external context. Below is the internal context.

Task: Create a Python module that meets the stated goals, along with a set of tests for that module.

This is my project goal:
{{goal}}

Include the following arguments:
- code: The full code for the script, including all imports and code
    - Since this is the entrypoint for the project, there should be a main function which is called if __name__ == '__main__'"
    - Use a functional style, only use classes when necessary
- test: The code for <module>_test.py, including all imports and functions. Tests should use a functional style with the assert keyword and run with pytest
    - All tests should be in their own functions and have setup and teardown so that they are isolated from each other
    - There should be multiple tests for each function, including tests for edge cases, different argument cases and failure cases
    - Do not use fixtures or anything else that is not a standard part of pytest"""

edit_file_prompt = """\
{{additional}}

The above is external context. Below is the internal context.

Notes:
- Use a functional style for code and tests where possible
- Do not include line numbers [#] at the beginning of the lines in your response
- Include the correct tabs at the beginning of lines in your response
- When rewriting the code, include the complete script, including all imports and code
- Do NOT shorten or abbreviate anything, DO NOT use "..." or "# Rest of the code" - ALWAYS put the complete code in your response
- Implement everything necessary for the code to work. Do not stub any functions or leave anything out -- the code should be complete and functional
- Please help me to write production-grade code that is clean, readable, and maintainable

This is my project goal:
{{goal}}

{{project_code_formatted}}

{{errors_formatted}}

{{reasoning}}
Task:
- Rewrite the code to meet the stated goals and fix any errors
- Whatever you do, ALWAYS RESPOND WITH THE ENTIRE SCRIPT, INCLUDING ALL IMPORTS AND CODE, NOT JUST CHANGES TO CODE. I need the whole script from beginning to end in your response. No shortcuts.
- Your response should include all code, including imports, functions, comments, etc-- not just changes to code
- Your response CANNOT include "TODO", "...", "# Rest of the code" etc. Your response needs to be a full script, not just changes to code
"""

entrypoint_function = compose_function(
    name="entrypoint",
    description="Create a new script called main.py, as well as a test for main.py named main_test.py.",
    properties={
        "code": {
            "type": "string",
            "description": "The full code for main.py, including all imports and code, with no abbreviations.",
        },
        "test": {
            "type": "string",
            "description": "The full code for main_test.py, including all imports and code, with no abbreviations. The tests should be functional and simple, i.e. no fixtures, and compatible with pytest.",
        },
    },
    required_properties=["code", "test"],
)

create_file_function = compose_function(
    name="create_file",
    description="Create a new script in the project, as well as a test file for it.",
    properties={
        "code": {
            "type": "string",
            "description": "The full code for the module, including all imports and code, with no abbreviations. Be thorough.",
        },
        "test": {
            "type": "string",
            "description": "The full test code, including all imports and code, with no abbreviations. The tests must be functional, compatible with pytest and simple, i.e. don't use fixtures. Be very thorough.",
        },
    },
    required_properties=["code", "test"],
)

edit_function = compose_function(
    name="edit_file",
    description="Write all of the code for the module, including imports and functions. No snippets, abbreviations or single lines. Must be a complete code file with the structure 'imports', 'functions', and a main entrypoint in main.py which is called if __name__ == '__main__'.",
    properties={
        "code": {
            "type": "string",
            "description": "The full code for the module, including all imports and code, with no abbreviations. Be very thorough.",
        },
        "filename": {
            "type": "string",
            "description": "Name of the file.",
        },
    },
    required_properties=["code", "filename"],
)


def entrypoint_handler(arguments, context):
    should_log = context.get("log_level", "normal") != "quiet"

    code = arguments["code"]
    test = arguments["test"]

    project_dir = context["project_dir"]

    log(
        f"Creating main.py in {project_dir}"
        + f"\n\nCode:\n{code}"
        + f"\n\nTest:\n{test}",
        title="action",
        type="create",
        log=should_log,
    )

    save_code(code, f"{project_dir}/main.py")
    save_code(test, f"{project_dir}/main_test.py")

    return context


def remove_line_numbers(text):
    # Regular expression pattern to match '[n]' at the beginning of a line
    pattern = r"^\s*\[\d+\]\s*"

    # Split the text into lines
    lines = text.split("\n")

    # Remove the pattern from each line
    cleaned_lines = [re.sub(pattern, "", line) for line in lines]

    # Join the cleaned lines back into a single string
    cleaned_text = "\n".join(cleaned_lines)

    return cleaned_text


def edit_file_handler(arguments, context):
    should_log = context.get("log_level", "normal") != "quiet"
    code = remove_line_numbers(arguments["code"])

    filename = arguments["filename"]
    write_path = get_full_path(filename, context["project_dir"])

    # get old code
    try:
        with open(write_path, "r") as f:
            old_code = f.read()
    except Exception as e:
        old_code = ""

    log(
        f"Editing script {write_path}"
        + f"\n\nOld Code:\n{colored(old_code), 'yellow'}"
        + f"\n\nNew Code:\n{colored(code, 'white')}",
        title="action",
        type="write",
        log=should_log,
    )

    save_code(code, write_path)
    return context


def create_file_handler(arguments, context):
    should_log = context.get("log_level", "normal") != "quiet"
    filename = context["action_filename"]
    code = arguments["code"]
    test = arguments["test"]

    log(
        f"Creating new file {filename}"
        + f"\n\nCode:\n{code}"
        + f"\n\nTest:\n{test}",
        title="action",
        type="create",
        log=should_log,
    )

    # Create a new file at filename with code
    write_path = get_full_path(filename, context["project_dir"])
    save_code(code, write_path)

    # Create a new file at filename_test.py with test
    test_path = get_full_path(
        f"{os.path.splitext(filename)[0]}_test.py", context["project_dir"]
    )
    save_code(test, test_path)

    return context


def delete_file_handler(context):
    should_log = context.get("log_level", "normal") != "quiet"
    filename = context["action_filename"]
    reasoning = context["reasoning"]

    if "main.py" in filename or "main_test.py" in filename:
        log(
            f"File {filename} contains main.py or main_test.py, so it will not be deleted",
            title="action",
            type="warning",
            log=should_log,
        )
        return context

    log(
        f"Deleting file {filename}" + f"\n\nReasoning:\n{reasoning}",
        title="action",
        type="delete",
        log=should_log,
    )

    # Delete the file at filename
    file_path = get_full_path(filename, context["project_dir"])
    # check if the file exists
    if os.path.exists(file_path):
        os.remove(file_path)
        # if file_path didn't contain _test.py, then delete the _test.py file
        if "_test.py" not in file_path:
            test_path = get_full_path(
                f"{os.path.splitext(filename)[0]}_test.py", context["project_dir"]
            )
            if os.path.exists(test_path):
                os.remove(test_path)
    else:
        log(
            f"File {filename} does not exist",
            title="action",
            type="warning",
            log=should_log,
        )

    return context


def step(context):
    """
    This function serves as the 'Act' stage in the OODA loop. It executes the selected action from the 'Decide' stage.

    Args:
        context (dict): The dictionary containing data about the current state of the system, including the selected action to be taken.

    Returns:
        dict: The updated context dictionary after the 'Act' stage, which will be used in the next iteration of the OODA loop.
    """

    if context["running"] == False:
        return context

    should_log = context.get("log_level", "normal") != "quiet"
    debug = context.get("log_level", "normal") == "debug"

    log(
        f"Act Step Started: {context['action_name']} on {context['action_filename']}",
        title="step",
        type="info",
        log=should_log,
    )

    prompt = edit_file_prompt
    functions = [edit_function]

    if context["file_count"] == 0:
        prompt = create_file_prompt
        functions = [entrypoint_function]

    log(
        f"Running action {context['action_name']} on {context['action_filename']}",
        title="action",
        color="green"
    )
        

    if context["action_name"] == "delete_file":
        delete_file_handler(context)
        return context

    if context["action_name"] == "create_file":
        prompt = create_file_prompt
        functions = [create_file_function]

    text = compose_prompt(prompt, context)
    text = trim_prompt(text, 10000, preserve_top=False)
    response = openai_function_call(
        text=text,
        functions=functions,
        debug=debug,
        model=context.get("model", "gpt-3.5-turbo-0613"),
    )
    
    # find the function in functions with the name that matches response["function_name"]
    # then call the handler with the arguments and context
    function_name = response["function_name"]
    arguments = response["arguments"]

    # make a formatted string of argument key values
    args_str = "\n".join(
        f"*** {key} ***\n{str(value)}"
        if "\n" in str(value)
        else f"*** {key}: {str(value)}"
        for key, value in arguments.items()
    )

    log(
        f"Running action {function_name} with arguments:\n{args_str}",
        title="action",
        type="handler",
        log=debug,
    )
    
    # if function_name is create, then we need to create a new file
    if function_name == "create_file":
        create_file_handler(arguments, context)
    elif function_name == "entrypoint":
        entrypoint_handler(arguments, context)
    elif function_name == "edit_file":
        edit_file_handler(arguments, context)

    # install any new imports if there are any
    context = handle_packages(context)

    context_str = "\n".join(
        f"*** {key} ***\n{str(value)}"
        if "\n" in str(value)
        else f"*** {key}: {str(value)}"
        for key, value in context.items()
    )

    log(
        f"Final context is:\n{context_str}",
        title="context",
        type="system",
        log=debug,
    )

    return context
