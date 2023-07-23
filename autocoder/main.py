import os
import sys

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

    print_header(text="autocoder", color="yellow", font="slant")
    log("Initializing...", title="autocoder", type="system")

    if (
        project_data.get("quiet") is None
        and "-q" in sys.argv
        or os.getenv("QUIET", "").lower() == "true"
    ):
        project_data["quiet"] = True
    else:
        project_data["quiet"] = False
    if (
        project_data.get("debug") is None
        and "-d" in sys.argv
        or os.getenv("DEBUG", "").lower() == "true"
    ):
        project_data["debug"] = True
    else:
        project_data["debug"] = False

    if (
        project_data.get("step") is None
        and ("-s" in sys.argv
        or os.getenv("STEP", "").lower() == "true")
    ):
        project_data["step"] = True
    else:
        project_data["step"] = False

    # check if project_dir exists and create it if it doesn't
    if not os.path.exists(project_data["project_dir"]):
        os.makedirs(project_data["project_dir"])

    def initialize(context):
        if context is None:
            # Should only run on the first run
            context = project_data
            context["running"] = True
        return context

    loop_dict = start([initialize, reason, act], stepped=project_data["step"])
    if project_data["step"]:
        step_with_input_key(loop_dict)

    return loop_dict
