import os
from dotenv import load_dotenv
from pyfiglet import Figlet
from rich.console import Console

from agentaction import import_actions
from agentmemory import wipe_all_memories
from agentloop import (
    start as start_loop,
    create_default_context,
    create_context_builders,
)

from autocode.steps import act
from autocode.steps import reason
from autocode.steps import validate

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


def start(
    steps=None,
    actions_dir="./autocode/actions",
    context_dir="./autocode/context",
    seed_data=None,
    reset=False,
):
    print_logo()

    if steps is None:
        context_step = create_context_builders(context_dir)
        steps = [
            create_default_context,
            validate,
            reason,
            act,
        ]

    if reset:
        wipe_all_memories()

    if actions_dir is not None:
        import_actions(actions_dir)

    loop_dict = start_loop(steps)
    return loop_dict
