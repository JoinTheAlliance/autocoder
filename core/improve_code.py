from core.coalesce import coalesce
from core.model import use_language_model
from core.utils import (
    compose_header,
    run_code,
    save_code,
    strip_header,
    validate_file,
    log,
)

from core.install_imports import install_imports


def improve_code(filename, goal, error):
    log(filename, "ATTEMPTING IMPROVEMENT EXPERIMENT")
    code = open(filename).read()
    previous_code = code

    # Improvement prompt for loop
    improvement_prompt = (
        "Always give the complete script, including imports and tests.\n"
        "Always wrap your code in a function so that it can be used modularly and imported into other scripts. Call your main function at the end of the script, in the __name__ == '__main__'.\n"
        "NEVER use # ... to abbreviate or leave anything code out. Always respond with a complete script, not a snippet, explanation or plan."
        "Your response should start with an import statement and end with tests to validate your code."
        "Please add or update any tests to make sure these changes work. Tests should be simple and use the assert keyword and only run if __name__ == '__main__' at the bottom of the script."
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

    # Improvement prompt on existing script
    if error is None or error == "":
        improvement_prompt = (
            "Always give the complete script, including imports and tests.\n"
            "Always wrap your code in a function so that it can be used modularly and imported into other scripts. Call your main function at the end of the script, in the __name__ == '__main__'.\n"
            "NEVER use # ... to abbreviate or leave anything code out. Always respond with a complete script, not a snippet, explanation or plan.\n"
            "Your response should start with an import statement and end with tests to validate your code.\n"
            "Please add or update any tests to make sure these changes work. Tests should be simple and use the assert keyword and only run if __name__ == '__main__' at the bottom of the script.\n"
            + "```\nPlease improve the code to meet my goals, and rewrite the entire the script with the changes. Include all code, including imports, and tests. The script should run without errors, all tests should print their output to the console, and the last line of code should print 'All tests complete!'"
            + "I have this code:\n"
            "\n```\n" + code + "```\n"
            "I want to improve my code. My goal is:```\n" + goal
        )
    log(filename, improvement_prompt)

    improve_code_function = {
        "name": "improve_code",
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
                    "description": "The reasoning and explanation for what needed improvement in the script that is being fixed with the new code",
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

    user_message = {"role": "user", "content": improvement_prompt}

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
        log(filename, "*** CALLING GENERATION FUNCTION")
        arguments = use_language_model(
            [user_message],
            functions=[improve_code_function],
            function_call={"name": "improve_code"},
            filename=filename,
        )
        if arguments is None:
            log(filename, "INVALID GENERATION RESULT.")
            continue

        if "response_type" not in arguments:
            log(filename, "INVALID GENERATION RESULT TYPE.")
            continue

        response_type = arguments["response_type"]

        reasoning = arguments["reasoning"]

        response_code = arguments["code"]

        if response_code is None:
            log(filename, "INVALID GENERATION TYPE.")
            log(filename, "GENERATION RESULT TYPE WAS: " + response_type.capitalize())
            log(filename, "RECALIBRATING...")
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
            log(filename, "Invalid response type.")
            continue
        break

    print("*** response_code:", response_code)
    print("*** goal:", goal)
    print("*** reasoning:", reasoning)

    code = compose_header(goal, reasoning) + strip_header(response_code)
    save_code(code, filename)

    code_before_coalesce = code
    [error, output] = run_code(filename)

    should_install_imports = True

    # pre-validate the code, basically catch the cases where we could easily fix the code
    full_validation = validate_file(filename)
    full_validation_success = full_validation["success"]
    if error or full_validation_success == False:
        soft_validation = validate_file(filename)
        soft_validation_success = soft_validation["success"]
        if soft_validation_success == True:
            response = coalesce(filename, code, previous_code, goal, reasoning)
            if response["success"]:
                code = response["code"]
                should_install_imports = response["new_imports"]
                save_code(code, filename)

    if should_install_imports:
        install_imports(code)
    [error, output] = run_code(filename)

    log(filename, reasoning)

    if previous_code == code_before_coalesce:
        log(filename, "NO IMPROVEMENTS MADE BEFORE COALESCE.")
        return [False, error, output]

    if previous_code == code:
        log(filename, "NO IMPROVEMENTS MADE AFTER COALESCE.")
        return [False, error, output]

    if previous_code != code and previous_code != code_before_coalesce:
        log(filename, "SOME IMPROVEMENTS MADE.")
        return [True, error, output]

    if error:
        log(filename, "ERROR OCCURED WHILE RUNNING SIMULATION:")
        log(filename, error)
        return [False, error, output]
    else:
        log(filename, "SIMULATION RAN SUCCESSFULLY. OUTPUT:")
        log(filename, output)
        return [True, error, output]
