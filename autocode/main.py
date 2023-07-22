import os
from dotenv import load_dotenv
from pyfiglet import Figlet
from rich.console import Console

from agentloop import start

from autocode.steps import reason
from autocode.steps import act

# Suppress warning
os.environ["TOKENIZERS_PARALLELISM"] = "False"

load_dotenv()  # take environment variables from .env.

def main(project_data):
    """
    Main entrypoint for autocode. Usually called from the CLI.
    """

    # Print logo
    f = Figlet(font="letters")
    console = Console()
    print("\n")
    console.print(f.renderText("autocode"), style="yellow")
    console.print("Initializing...\n", style="BRIGHT_BLACK")

    def initialize(context):
        if context is None:
            # Should only run on the first run
            context = project_data
        return context

    loop_dict = start([initialize, reason, act])
    return loop_dict
