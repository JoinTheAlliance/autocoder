from core.utils import log, strip_header, compose_header, save_code, install_imports
from core.model import use_language_model

def write_code(filename, goal):
    log(filename, "*** GENERATING INITIAL EXPERIMENT")

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

    user_message = {"role": "user", "content": write_code_prompt(goal)}

    write_code_function = {
        "name": "write_code",
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
    log(filename, "*** CALLING GENERATION FUNCTION")
    while retry_count < retries:
        log(filename, "*** EPOCH: " + str(retry_count + 1) + "/" + str(retries))
        retry_count += 1
        arguments = use_language_model(
            [user_message],
            functions=[write_code_function],
            function_call={"name": "write_code"},
            filename=filename
        )

        if arguments is None:
            log(filename, "INVALID GENERATION RESULT.")
            return

        response_type = arguments["response_type"]
        if response_type == "complete_script":
            reasoning = arguments["reasoning"]
            code = arguments["code"]
            break
        else:
            log(filename, "INVALID GENERATION TYPE.")
            log(filename, "GENERATION RESULT TYPE WAS: " + response_type.capitalize())
            log(filename, "RECALIBRATING...")
            return

    if code is None:
        log(filename, 
            "INSTABILITY IN GENERATION RESULT. THE EXPERIMENT FAILED TO PRIME. PLEASE TRY AGAIN..."
        )
        return

    code = compose_header(goal, reasoning) + strip_header(code)

    save_code(code, filename)

    install_imports(code)

    return code

