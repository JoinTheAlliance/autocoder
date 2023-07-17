from easycompletion import compose_function, compose_prompt


prompt = """ENTRYPOINT PROMPT GOES HERE"""


def builder(context):
    return compose_prompt(prompt, context)


def handler(arguments, context):
    # arguments are plan, code, pakages, test
    # print plan
    # save code to main.py
    # save test to main_test.py
    # pip install packages
    pass


def get_actions():
    return [
        {
            "function": compose_function(
                name="create_script",
                description="Create a new script called main.py, as well as a test for main.py named main_test.py.",
                properties={
                    "plan": {
                        "type": "string",
                        "description": "Write out a plan, the reason about whether or not it is the best approach. If it is not the best approach, write out a better plan and explain your reasoning.",
                    },
                    "code": {
                        "type": "string",
                        "description": "The full code for main.py, including all imports and code",
                    },
                    "packages": {
                        "type": "array",
                        "description": "A list of packages to install, derived from the imports of the code. Each package should be a string, e.g. ['numpy', 'pandas']",
                        "items": {"type": "string"},
                    },
                    "test": {
                        "type": "string",
                        "description": "The full code for main_test.py, including all imports and code. Tests should use a functional style, use the assert keyword and be prepared to work with pytest.",
                    },
                },
                required_properties=["plan", "code", "packages", "test"],
            ),
            "prompt": prompt,
            "builder": builder,
            "handler": handler
        }
    ]
