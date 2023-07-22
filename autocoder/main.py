import os
from dotenv import load_dotenv

from agentloop import start, step_with_input_key

from autocoder.steps import reason
from autocoder.steps import act
from agentlogger import log, print_header

# Suppress warning
os.environ["TOKENIZERS_PARALLELISM"] = "False"

load_dotenv()  # take environment variables from .env.


def main(project_data):
    """
    Main entrypoint for autocoder. Usually called from the CLI.
    """

    print_header(text="autocoder", color="yellow", font="letters")
    log("Initializing...", title="autocoder", type="system")

    import sys

    if "-q" in sys.argv or os.getenv("QUIET") == "True" or os.getenv("QUIET") == "true":
        project_data["quiet"] = True
    else:
        project_data["quiet"] = False
    if "-d" in sys.argv or os.getenv("DEBUG") == "True" or os.getenv("DEBUG") == "true":
        project_data["debug"] = True
    else:
        project_data["debug"] = False

    def initialize(context):
        if context is None:
            # Should only run on the first run
            context = project_data
        return context

    loop_dict = step_with_input_key(start([initialize, reason, act], stepped=True))
    return loop_dict
