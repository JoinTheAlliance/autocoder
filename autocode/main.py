import os
from dotenv import load_dotenv
from pyfiglet import Figlet
from rich.console import Console

from agentaction import import_actions
from agentloop import start

from autocode.steps import orient
from autocode.steps import decide
from autocode.steps import act

# Suppress warning
os.environ["TOKENIZERS_PARALLELISM"] = "False"

load_dotenv()  # take environment variables from .env.


def print_logo():
    """
    Prints ASCII logo using pyfiglet.
    """

    f = Figlet(font="letters")
    console = Console()
    print("\n")
    console.print(f.renderText("autocode"), style="yellow")
    console.print("Starting...\n", style="BRIGHT_BLACK")


# old loop

# from autocode.helpers.code import run_code, save_code
# from autocode.helpers.validation import file_exists
# from autocode.actions.validate import validate_code
# from autocode.actions.edit import edit
# from autocode.actions.create_main import create_main

# def main(goal, filename):
#     if file_exists(filename) == False:
#         code = create_main(filename, goal)

#     # read the code
#     original_code = open(filename).read()
#     [error, _] = run_code(filename)
#     validation_passed = False
#     while True:
#         # always run at least once
#         if validation_passed == False and error:
#             [success, error, output] = edit(filename, goal, error)

#             # something went wrong, feed the error back into the model and run it again
#             if error:
#                 continue

#             validation = validate_code(filename, goal, output)

#             # passed validation, finish up
#             if validation["success"]:
#                 validation_passed = True
#                 error = None
#                 break
#             # validation failed
#             else:
#                 error = validation["explanation"]
#                 if error is None and success is False:
#                     error = output
#                     continue
#                 # if revert is true, revert to the last version of the code
#                 if validation["revert"]:
#                     save_code(original_code, filename)
#                     continue
#                 continue
#         else:
#             break

def create_initialization_step(project_data):
    # load the json file at the project path
    def initialize(context):
        context = {}
        print("project_data")
        print(project_data)
        # for every key in project data, add it to the context
        for key in project_data:
            context[key] = project_data[key]
        return context
    return initialize


def main(project_data):
    print_logo()
    import_actions("./autocode/actions")
    initialize = create_initialization_step(project_data)

    loop_dict = start(
        [
            initialize,
            orient,
            decide,
            act,
        ]
    )
    return loop_dict
