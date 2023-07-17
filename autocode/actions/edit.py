from easycompletion import compose_function, compose_prompt, openai_function_call

edit_prompt = """
Always give the complete script, including imports and tests.
Always wrap your code in a function so that it can be used modularly and imported into other scripts. Call your main function at the end of the script, in the __name__ == '__main__'.\n
NEVER use # ... to abbreviate or leave anything code out. Always respond with a complete script, not a snippet, explanation or plan.
Your response should start with an import statement and end with tests to validate your code.
Please add or update any tests to make sure these changes work. Tests should use the assert keyword and they should run under __name__ == '__main__' at the bottom of the script.

My goal is:
{{goal}}

Please fix the code and write the entire the script with the changes. Include all code, including imports, tests, all functions, everything. The script should run without errors, all tests should print their results to the console. The last line of code should print 'All tests complete!'.
I have this code:
```
{{code}}
```
I get this error:
```
{{error}}
```
\n
Please improve my code.
"""


def write_complete_script_handler(arguments, context):
    pass


def insert_code_handler(arguments, context):
    pass


def replace_code_handler(arguments, context):
    pass


def remove_code_handler(arguments, context):
    pass


def replace_function_handler(arguments, context):
    pass


def write_snippet_handler(arguments, context):
    pass


def create_new_file_handler(arguments, context):
    pass


def get_edit_actions():
    return [
        {
            "function": compose_function(
                name="insert_code",
                description="Insert a snippet of code before a line.",
                properties={
                    "reasoning": {
                        "type": "string",
                        "description": "What does this code do? Why are you inserting it?",
                    },
                    "code": {
                        "type": "string",
                        "description": "The snippet of code to insert.",
                    },
                    "line_number": {
                        "type": "number",
                        "description": "The line number to insert the code before.",
                    },
                },
                required_properties=["reasoning", "code", "line_number"],
            ),
            "handler": insert_code_handler,
        },
        {
            "function": compose_function(
                name="replace_code",
                description="Replace some lines with a snippet of code. This is useful for replacing a function with a new implementation, for example. Requires an input and output line number.",
                properties={
                    "reasoning": {
                        "type": "string",
                        "description": "Which code are you replacing? What does the new code do? Why are you replacing it?",
                    },
                    "code": {
                        "type": "string",
                        "description": "The snippet of code to replace the existing code with.",
                    },
                    "start_line": {
                        "type": "number",
                        "description": "The start line number of the file where code is being replaced.",
                    },
                    "end_line": {
                        "type": "number",
                        "description": "The end line number of the file where code is being replaced.",
                    },
                },
                required_properties=["reasoning", "code", "start_line", "end_line"],
            ),
            "handler": replace_code_handler,
        },
        {
            "function": compose_function(
                name="write_complete_script",
                description="Writes a complete script.",
                properties={
                    "reasoning": {
                        "type": "string",
                        "description": "What does this code do? Why are you rewriting it? How will this change the behavior of the script?",
                    },
                    "code": {
                        "type": "string",
                        "description": "The complete script to write.",
                    },
                },
                required_properties=["reasoning", "code"],
            ),
            "handler": write_complete_script_handler,
        },
        {
            "function": compose_function(
                name="remove_code",
                description="Removes a range of lines from the code.",
                properties={
                    "reasoning": {
                        "type": "string",
                        "description": "Why are you removing this code?",
                    },
                    "start_line": {
                        "type": "number",
                        "description": "The start line number of the code to remove.",
                    },
                    "end_line": {
                        "type": "number",
                        "description": "The end line number of the code to remove.",
                    },
                },
                required_properties=["reasoning", "start_line", "end_line"],
            ),
            "handler": remove_code_handler,
        },
        {
            "function": compose_function(
                name="replace_function",
                description="Replaces a function with new code.",
                properties={
                    "reasoning": {
                        "type": "string",
                        "description": "Why are you replacing this function?",
                    },
                    "function_name": {
                        "type": "string",
                        "description": "The name of the function to replace.",
                    },
                    "new_code": {
                        "type": "string",
                        "description": "The new code to replace the function with.",
                    },
                },
                required_properties=["reasoning", "function_name", "new_code"],
            ),
            "handler": replace_function_handler,
        },
        {
            "function": compose_function(
                name="write_snippet",
                description="Writes a snippet of code, which aren't added to the code but are used to help the user write the complete script.",
                properties={
                    "explanation": {
                        "type": "string",
                        "description": "What does this code do? Why are you writing it?",
                    },
                    "code": {
                        "type": "string",
                        "description": "The snippet of code to write.",
                    },
                },
                required_properties=["code"],
            ),
            "handler": write_snippet_handler,
        },
        {
            "function": compose_function(
                name="create_new_file",
                description="Creates a new file.",
                properties={
                    "filename": {
                        "type": "string",
                        "description": "The name of the new file to create.",
                    },
                },
                required_properties=["filename"],
            ),
            "handler": create_new_file_handler,
        },
    ]


def edit_handler(arguments, context):
    valid = False
    while valid is False:
        # call the edit validation prompt
        valid = validate_edits(arguments, context)
        if valid is True:
            break
        else:
            # call the edit again
            context = openai_function_call(
                text=compose_prompt(edit_prompt, context),
                functions=get_edit_actions(),
            )


def get_actions():
    return [
        {
            "function": get_edit_actions(),
            "handler": edit_handler,
        }
    ]
