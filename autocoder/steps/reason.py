from easycompletion import (
    openai_function_call,
    compose_prompt,
    compose_function,
)
from autocoder.helpers.code import validate_file

from autocoder.helpers.context import (
    backup_project,
    collect_errors,
    collect_files,
    get_file_count,
    read_and_format_code,
    run_main,
    run_tests,
    validate_files,
)

from agentlogger import log

from agentloop import stop

reasoning_prompt = """This is my code:
{{project_code_formatted}}
This is my goal:
{{goal}}
{{errors_formatted}}
Your task: Evaluate the code and determine if it meets the goal, or what could be improved about it.
- Please provide reasoning for why the code is valid and complete (or not) and respond with is_valid_and_complete=True
- If it does not meet the goals, please provide explain why it does not, and what could be improved.
- If there is way to improve the code, respond with is_valid_and_complete=False.
"""


def compose_project_validation_function():
    """
    This function defines the structure and requirements of the 'assess' function to be called in the 'Decide' stage of the OODA loop.

    Returns:
        dict: A dictionary containing the details of the 'assess' function, such as its properties, description, and required properties.
    """
    return compose_function(
        name="project_validation_action",
        description="Decide which action to take next.",
        properties={
            "reasoning": {
                "type": "string",
                "description": "Does the code fill the specification and complete all of my goals? Provide reasoning for why it does or doesn't, and what could be improved.",
            },
            "is_valid_and_complete": {
                "type": "boolean",
                "description": "Does the code fill the specification and complete all of my goals?. True if there is nothing else that needs to be improved, False otherwise.",
            },
        },
        required_properties=["reasoning", "is_valid_and_complete"],
    )


def step(context, loop_dict):
    """
    This function serves as the 'Decide' stage in the OODA loop. It uses the current context data to assess which action should be taken next.

    Args:
        context (dict): The dictionary containing data about the current state of the system.

    Returns:
        dict: The updated context dictionary after the 'Decide' stage, including the selected action and reasoning behind the action.
    """
    if context["running"] == False:
        return context
    should_log = context.get("log_level", "normal") != "quiet"

    log(
        "Reasoning Step Started",
        title="step",
        type="info",
        log=should_log,
    )

    context = get_file_count(context)

    debug = context.get("log_level", "normal") == "debug"
    should_log = context.get("log_level", "normal") != "quiet"

    # If we have no files, go immediately to the create step
    if context["file_count"] == 0:
        log(
            "Creating main.py for new project",
            title="new project",
            type="start",
            log=should_log,
        )
        return context

    context = backup_project(context)
    context = collect_files(context)
    context = validate_files(context)
    context = run_tests(context)
    context = run_main(context)
    context = collect_errors(context)
    context = read_and_format_code(context)

    # If we have an error, go immediately to the edit step
    if context.get("main_success") is False and context.get("main_error") is not None:
        log(
            f"main.py failed to run\nError:\n{context.get('main_error', 'unknown')}",
            title="main.py",
            type="error",
            log=should_log,
        )
        context[
            "reasoning"
        ] = "main.py failed to run - I probably need to fix that before I can do anything else."
        return context

    # If any of the files failed to validate for any reason, go immediately to the edit step
    if context["project_validated"] is False:
        validation_errors = ""
        for file_dict in context["project_code"]:
            file_path = file_dict["absolute_path"]
            validation = validate_file(file_path)
            if validation["success"] is False:
                validation_errors += f"\n{file_path}:\n{validation['error']}\n"
        if validation_errors != "":
            log(
                "Project failed to validate. Errors:\n" + validation_errors,
                title="validation",
                type="error",
                log=should_log,
            )
            context[
                "reasoning"
            ] = "The project failed to validate. I need to fix the validation errors."
        return context

    if context["project_tested"] is False:
        test_errors = ""
        for file_dict in context["project_code"]:
            if (
                file_dict.get("test_success") is False
                and file_dict.get("test_error") is not None
            ):
                test_errors += (
                    f"\n{file_dict['absolute_path']}:\n{file_dict['test_error']}\n"
                )
        if test_errors != "":
            log(
                "Project failed in testing. Errors:\n" + test_errors,
                title="test",
                type="error",
                log=should_log,
            )
            context[
                "reasoning"
            ] = "The project failed in testing. I need to fix the test errors."
            return context

    text = compose_prompt(reasoning_prompt, context)
    functions = compose_project_validation_function()

    # Handle the auto case
    response = openai_function_call(
        text=text, functions=functions, debug=debug, model=context.get("model", "gpt-3.5-turbo-0613")
    )

    # Add the action reasoning to the context object
    is_valid_and_complete = response["arguments"]["is_valid_and_complete"]

    if is_valid_and_complete is True:
        log(
            "Project is valid and complete. Good luck!",
            title="validation",
            type="success",
            log=should_log,
        )
        stop(loop_dict)
        context["running"] = False

    else:
        log(
            response["arguments"]["reasoning"],
            title="validation",
            type="reasoning",
            log=should_log,
        )

    context["reasoning"] = response["arguments"]["reasoning"]
    return context
