from easycompletion import (
    openai_function_call,
    compose_prompt,
    compose_function,
)

from autocode.helpers.context import (
    backup_project,
    collect_files,
    get_file_count,
    read_and_format_code,
    run_main,
    run_tests,
    validate_files,
)

reasoning_prompt = """
{{all_code}}

Client's stated goals:
{{goal}}

Client's stated test pass conditions:
{{test_conditions}}

Note: I have written this code to meet a client's stated goal. The code should also pass the client's stated tests.

Your task: Evaluate the code and determine if it meets the client's stated goals and passes the client's stated tests.
- If it meets the goals and passes the tests, please provide reasoning for why it does and respond with is_valid_and_complete=True
- If it does not meet the goals, please provide explain why it does not, and what could be improved.
- If there is any reason for improvement, respond with is_valid_and_complete=False.
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
    project_data = context["project_data"]
    context["file_count"] = get_file_count(context)

    # New path
    if context["file_count"] == 0:
        return context

    context = backup_project(context)
    context = collect_files(context)
    context = validate_files(context)
    context = run_tests(context)
    context = run_main(context)
    context = read_and_format_code(context)

    # for every key in project data, add it to the context
    for key in project_data:
        context[key] = project_data[key]

    # If we have no files, go immediately to the create step
    if context["file_count"] == 0:
        return context

    # If we have an error, go immediately to the edit step
    if context["main_success"] is False:
        return context

    # If any of the files failed to validate for any reason, go immediately to the edit step
    if context["project_validated"] is False or context["project_tested"] is False:
        return context

    # Handle the auto case
    response = openai_function_call(
        text=compose_prompt(reasoning_prompt, context),
        functions=compose_project_validation_function(),
    )

    # Add the action reasoning to the context object
    is_valid_and_complete = response["arguments"]["is_valid_and_complete"]

    if is_valid_and_complete is True:
        print("SUCCESS")
        loop_dict.stop()

    context["reasoning"] = response["arguments"]["reasoning"]
    context["action_name"] = "edit"
    return context
