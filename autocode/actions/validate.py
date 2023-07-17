from easycompletion import compose_function


prompt = """
    I have this goal:
    ```
    {{goal}}
    ```
    I have this code:
    ```
    {{code}}
    Does the code implement the intended changes as well as the original stated goals? Is it real python code that should work?
    ```
    Please return a boolean value indicating if the script is valid and implements the intended goal.
"""


def builder(context):
    return context


def handler(arguments, context):
    pass


def get_actions():
    return [
        {
            "function": compose_function(
                name="validate_script",
                description="Validates if the script implements the intended changes and original stated goals, and if it is valid code that should work",
                properties={
                    "reasoning": {
                        "type": "string",
                        "description": "The reasoning and explanation for what the script is supposed to do and whether or not it does that",
                    },
                    "valid": {
                        "type": "boolean",
                        "description": "Is the script valid or not?",
                    },
                },
                required_properties=["reasoning", "valid"],
            ),
            "prompt": prompt,
            "builder": builder,
            "handler": handler,
        }
    ]
