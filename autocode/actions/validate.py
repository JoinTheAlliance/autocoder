import os
from easycompletion import openai_function_call
from autocode.helpers.code import save_code, strip_header
from autocode.helpers.validation import validate_file


def validate_code(filename, goal, output):
    code = open(filename).read()

    stripped_code = strip_header(code)
    # strip the code temporarily
    save_code(stripped_code, "temp_" + filename)
    validation = validate_file("temp_" + filename)
    os.remove("temp_" + filename)
    if output is None or output == "":
        return {
            "success": False,
            "revert": False,
            "explanation": "The file didn't output anything. All tests should print their output. The file should output ('All tests complete') at the end to indicate to the user that tests ran and were successful.",
        }

    success = validation["success"]

    if success == False:
        return validation

    # TODO: revert code if validation fails and try again, otherwise call with the additional validation information

    validate_function = {
        "name": "validate_script",
        "description": "Validates if the script implements the intended changes and original stated goals, and if it is valid code that should work",
        "parameters": {
            "type": "object",
            "properties": {
                "reasoning": {
                    "type": "string",
                    "description": "The reasoning and explanation for what the script is supposed to do and whether or not it does that",
                },
                "valid": {
                    "type": "boolean",
                    "description": "Is the script valid or not?",
                },
            },
            "required": ["reasoning", "valid"],
        },
    }

    validate_prompt = (
        "I have this goal:```\n" + goal + "```\n"
        "I have this code:\n```"
        "" + code + ""
        "Does the code implement the intended changes as well as the original stated goals? Is it real python code that should work?\n```"
        "```\nPlease return a boolean value indicating if the script is valid and implements the intended goal."
    )

    retries = 10
    retry_count = 0
    arguments = None
    while retry_count < retries:
        retry_count += 1
        arguments = openai_function_call(
            text=validate_prompt, functions=[validate_function]
        )

        if arguments is None:
            continue

        return {
            "success": arguments["valid"],
            "explanation": arguments["reasoning"],
            "revert": False,
        }
