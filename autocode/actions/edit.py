# TODO: edit the edit prompt

from easycompletion import openai_function_call
from autocode.helpers.heal_code import heal_code

from autocode.helpers.code import (
    compose_header,
    run_code,
    save_code,
    strip_header,
)

from autocode.helpers.validation import validate_file

from autocode.helpers.imports import install_imports


def edit(filename, goal, error):
    code = open(filename).read()
    previous_code = code

    # Improvement prompt for loop
    edit_prompt = (
        "Always give the complete script, including imports and tests.\n"
        "Always wrap your code in a function so that it can be used modularly and imported into other scripts. Call your main function at the end of the script, in the __name__ == '__main__'.\n"
        "NEVER use # ... to abbreviate or leave anything code out. Always respond with a complete script, not a snippet, explanation or plan."
        "Your response should start with an import statement and end with tests to validate your code."
        "Please add or update any tests to make sure these changes work. Tests should use the assert keyword and they should run under __name__ == '__main__' at the bottom of the script."
        "My goal is:```\n"
        + goal
        + "```\nPlease fix the code and write the entire the script with the changes. Include all code, including imports, tests, all functions, everything. The script should run without errors, all tests should print their results to the console. The last line of code should print 'All tests complete!'."
        + "```\nI have this code:\n```"
        + code
        + "```\nI get this error:\n```"
        + error
        + "```\n"
        "Please improve my code.```\n"
    )
    
    improve_code_function = {
        "name": "edit",
        "description": "Improve the code",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The complete script, including imports, all functions and tests.",
                },
                "reasoning": {
                    "type": "string",
                    "description": "The reasoning and explanation for what needed edit in the script that is being fixed with the new code",
                },
                "response_type": {
                    "type": "string",
                    "enum": ["complete_script", "snippet"],
                    "description": "The type of code response. Is the assistant is responding with a complete script that will run, use 'complete'. If the assistant is providing a snippet or example that is not a complete script, use 'snippet'.",
                },
            },
            "required": ["reasoning", "code", "response_type"],
        },
    }

    previous_code = code

    retries = 10
    retry_count = 0
    code = None
    reasoning = None
    arguments = None
    response_code = None
    response_type = None

    while retry_count < retries:
        retry_count += 1
        response = openai_function_call(
            text=edit_prompt,
            functions=[improve_code_function]
        )
        arguments = response["arguments"]
        if arguments is None:
            continue

        if "response_type" not in arguments:
            continue

        response_type = arguments["response_type"]

        reasoning = arguments["reasoning"]

        response_code = arguments["code"]

        if response_code is None:
            continue

        is_complete_script = (
            any(
                [
                    line.startswith("import") or line.startswith("from")
                    for line in response_code.split("\n")
                ]
            )
            and "__name__" in response_code or "main(" in response_code
        )

        if is_complete_script is not True and response_type != "complete_script":
            continue
        break

    code = compose_header(goal, reasoning) + strip_header(response_code)
    save_code(code, filename)

    code_before_heal = code
    [error, output] = run_code(filename)

    should_install_imports = True

    # pre-validate the code, basically catch the cases where we could easily fix the code
    full_validation = validate_file(filename)
    full_validation_success = full_validation["success"]
    if error or full_validation_success == False:
        soft_validation = validate_file(filename)
        soft_validation_success = soft_validation["success"]
        if soft_validation_success == True:
            response = heal_code(code, previous_code, goal, reasoning)
            if response["success"]:
                code = response["code"]
                should_install_imports = response["new_imports"]
                save_code(code, filename)

    if should_install_imports:
        install_imports(code)
    [error, output] = run_code(filename)

    if previous_code == code:
        return [False, error, output]

    if previous_code != code and previous_code != code_before_heal:
        return [True, error, output]

    if error:
        return [False, error, output]
    else:
        return [True, error, output]
