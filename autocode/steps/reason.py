from easycompletion import (
    compose_prompt,
    compose_function,
)

from agentevents import create_event
from easycompletion import openai_function_call

decision_prompt = """Current Epoch: {{epoch}}
The current time is {{current_time}} on {{current_date}}.
{{relevant_knowledge}}
{{events}}
{{available_actions}}
Assistant Notes:
- Do not ask if you can help. Do not ask how you can assist. Do not gather more information.
- I will not repeat the same action unless it achieves some additional goal. I don't like getting stuck in loops or repeating myself.
- I prefer to act in a way that is novel and interesting.
- I only want to gather additional knowledge when I have to. I like to try things first.

Your task: 
- Based on recent events, which of the actions that you think is the best next action for me to progress towards my goals.
- Based on the information provided, write a summary from your perspective of what action I should take next and why (assistant_reasoning)
- Respond with the name of the action (action_name)
- Rewrite the summary as if you were me, the user, in the first person (user_reasoning)
- I can only choose from the available actions. You must choose one of the available actions.
"""


def compose_decision_function():
    """
    This function defines the structure and requirements of the 'decide' function to be called in the 'Decide' stage of the OODA loop.

    Returns:
        dict: A dictionary containing the details of the 'decide' function, such as its properties, description, and required properties.
    """
    return compose_function(
        name="decide_action",
        description="Decide which action to take next.",
        properties={
            "assistant_reasoning": {
                "type": "string",
                "description": "The reasoning behind the decision. Why did you choose this action? Should be written from your perspective, as the assistant, telling the user why you chose this action.",
            },
            "action_name": {
                "type": "string",
                "description": "The name of the action to take. Should be one of the available actions, and should not include quotes or any punctuation",
            },
            "user_reasoning": {
                "type": "string",
                "description": "Rewrite the assistant_reasoning from the perspective of the user. Rewrite your reasoning from my perspective, using 'I' instead of 'You'.",
            },
        },
        required_properties=["action_name", "assistant_reasoning", "user_reasoning"],
    )


def decide(context):
    """
    This function serves as the 'Decide' stage in the OODA loop. It uses the current context data to decide which action should be taken next.

    Args:
        context (dict): The dictionary containing data about the current state of the system.

    Returns:
        dict: The updated context dictionary after the 'Decide' stage, including the selected action and reasoning behind the decision.
    """
    response = openai_function_call(
        text=compose_prompt(decision_prompt, context),
        functions=compose_decision_function()
    )

    # Add the action reasoning to the context object
    reasoning = response["arguments"]["user_reasoning"]
    reasoning_header = "Action Reasoning:"
    context["reasoning"] = reasoning_header + "\n" + reasoning + "\n"
    context["action_name"] = response["arguments"]["action_name"]
    create_event(reasoning, type="reasoning")
    return context
