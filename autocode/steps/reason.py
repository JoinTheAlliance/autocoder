from easycompletion import (
    compose_prompt,
    compose_function,
)

from easycompletion import openai_function_call


reasoning_prompt = """
Assistant Notes:
- Do not ask if you can help. Do not ask how you can assist. Do not gather more information.
- I will not repeat the same action unless it achieves some additional goal. I don't like getting stuck in loops or repeating myself.
- I prefer to act in a way that is novel and interesting.
- I only want to gather additional knowledge when I have to. I like to try things first.

{{all_code}}
{{error}}

Your task: 
- Based on recent events, which of the actions that you think is the best next action for me to progress towards my goals.
- Based on the information provided, write a summary from your perspective of what action I should take next and why (assistant_reasoning)
- Respond with the name of the action (action_name)
- Rewrite the summary as if you were me, the user, in the first person (user_reasoning)
- I can only choose from the available actions. You must choose one of the available actions.
"""


def compose_reasoning_function():
    """
    This function defines the structure and requirements of the 'reason' function to be called in the 'Decide' stage of the OODA loop.

    Returns:
        dict: A dictionary containing the details of the 'reason' function, such as its properties, description, and required properties.
    """
    return compose_function(
        name="reason_action",
        description="Decide which action to take next.",
        properties={
            "assistant_reasoning": {
                "type": "string",
                "description": "The reasoning behind the reasoning. Why did you choose this action? Should be written from your perspective, as the assistant, telling the user why you chose this action.",
            },
            "action_name": {
                "type": "string",
                "description": "The name of the action to take. Should be one of the available actions, and should not include quotes or any punctuation",
            },
            "user_reasoning": {
                "type": "string",
                "description": "Rewrite the assistant_reasoning from my perspective, as the user. Use 'I' statements instead of 'You'.",
            },
        },
        required_properties=["assistant_reasoning", "action_name", "user_reasoning"],
    )


def reason(context):
    """
    This function serves as the 'Decide' stage in the OODA loop. It uses the current context data to reason which action should be taken next.

    Args:
        context (dict): The dictionary containing data about the current state of the system.

    Returns:
        dict: The updated context dictionary after the 'Decide' stage, including the selected action and reasoning behind the reasoning.
    """

    action_name = None

    # If we have no files, go immediately to the entrypoint
    if context["file_count"] == 0:
        # new project
        action_name = "entrypoint"

    # If we have an error, go immediately to the edit prompt
    if context["main_success"] is False:
        action_name = "edit"

    project_code = context["project_code"]
    for file_dict in project_code:
        # check if test_success or validation_success are False
        if file_dict.get("test_success", None) is False:
            action_name = "edit"
        if file_dict.get("validation_success", None) is False:
            action_name = "edit"

    if action_name is not None:
        context["action_name"] = action_name
        return context

    # Handle the auto case
    response = openai_function_call(
        text=compose_prompt(reasoning_prompt, context),
        functions=compose_reasoning_function(),
    )

    # Add the action reasoning to the context object
    context["action_reasoning"] = response["arguments"]["user_reasoning"]
    context["action_name"] = response["arguments"]["action_name"]
    return context
