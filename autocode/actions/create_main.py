# entrypoint for a project

from easycompletion import openai_function_call
from autocode.helpers.imports import install_imports
from autocode.helpers.code import strip_header, compose_header, save_code


def create_main(filename, goal):
    # Store user message and response in chat history
    def write_code_prompt(goal):
        return (
            "Write a python script which will be named " + filename + "\n"
            "The script should include all code and be extremely detailed, including imports and tests.\n"
            "NEVER use # ... to abbreviate or leave anything code out. Always respond with a complete script, not a snippet, explanation or plan.\n"
            "Fill in any incomplete code and remove unnecessary or dangling comments. Replace any TODOs or implied to-dos with code. Do not use any comments, and remove any comments that aren't important or aren't related to code.\n"
            "Your response should start with an import statement and end with tests to validate your code.\n"
            "Tests should be simple and use the assert keyword and only run if __name__ == '__main__' at the bottom of the python script. All tests should print their result.\n"
            "The last line of code should print 'All tests complete!'.\n"
            "The script should do the following:\n" + goal + "\n"
        )

    write_code_function = {
        "name": "create_main",
        "description": "Write a python script and save it to a filename",
        "parameters": {
            "type": "object",
            "properties": {
                "reasoning": {
                    "type": "string",
                    "description": "The explanation for what the script is supposed to do",
                },
                "code": {
                    "type": "string",
                    "description": "The code for a complete script file, should include everything, including imports and tests and all code",
                },
                "response_type": {
                    "type": "string",
                    "enum": ["complete_script", "snippet", "example", "abbreviated"],
                    "description": "The type of code response. Is the assistant is responding with a complete script that will run, use 'complete_script'. If the assistant is providing a snippet or example that is not a complete script, use 'snippet' or 'abbreviated'.",
                },
            },
            "required": ["reasoning", "code", "response_type"],
        },
    }
    code = None
    reasoning = None
    retries = 10
    retry_count = 0
    while retry_count < retries:
        retry_count += 1
        arguments = openai_function_call(
            text=write_code_prompt(goal),
            functions=[write_code_function],
        )

        if arguments is None:
            return

        response_type = arguments["response_type"]
        if response_type == "complete_script":
            reasoning = arguments["reasoning"]
            code = arguments["code"]
            break
        else:
            return

    if code is None:
        return

    code = compose_header(goal, reasoning) + strip_header(code)

    save_code(code, filename)

    install_imports(code)

    return code
