from agentaction import (
    compose_action_prompt,
    get_action,
    use_action,
)

from easycompletion import openai_function_call


def act(context):
    """
    This function serves as the 'Act' stage in the OODA loop. It executes the selected action from the 'Decide' stage.

    Args:
        context (dict): The dictionary containing data about the current state of the system, including the selected action to be taken.

    Returns:
        dict: The updated context dictionary after the 'Act' stage, which will be used in the next iteration of the OODA loop.
    """
    action_name = context["action_name"]
    action = get_action(action_name)

    # TODO: Handle the case where the action is not found
    # IMO we should retry 5 times and then give up
    if action is None:
        return {"error": f"Action {action_name} not found"}

    response = openai_function_call(
        text=compose_action_prompt(action, context), functions=action["function"]
    )

    use_action(response["function_name"], response["arguments"], context)
    return context
