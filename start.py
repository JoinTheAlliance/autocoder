import os
import json
import sys
from prompt_toolkit.shortcuts import button_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit import PromptSession
from termcolor import colored

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env.

style = Style.from_dict(
    {
        "dialog": "bg:#88ff88",
        "button": "bg:#884444 #ffffff",
        "dialog.body": "bg:#ccffcc",
        "dialog shadow": "bg:#000088",
    }
)

# Define the key bindings
kb = KeyBindings()


@kb.add(Keys.ControlS)
def _(event):
    "By pressing `Control-S`, finish the input."
    event.app.current_buffer.validate_and_handle()


# Create a multiline prompt session
session = PromptSession(key_bindings=kb, multiline=True)


def get_input_from_prompt(question, default_text):
    print("##########################################################################")
    print(colored("Press ", "white"), end="")
    print(colored("'Ctrl-S'", "yellow"), end="")
    print(colored(" to finish editing and continue to the next question.\n", "white"))
    print(colored(question, "green"))
    return session.prompt(default=default_text)


def get_project_details(project_data=None, is_editing=False):
    questions = [
        {"key": "project_name", "question": "How is the name of your script?"},
        {
            "key": "goal",
            "question": "What do you want your script to do? Please be as detailed as possible.",
        },
        {
            "key": "test",
            "question": "How can I test the script? Please be as detailed as possible.",
        },
    ]

    project_data = project_data or {}

    for item in questions:
        answer = None

        # If it's not in editing mode and the question is about the project name, ask for input
        if not is_editing and item["key"] == "project_name":
            answer = input(f'{item["question"]}: ')

        if is_editing and item["key"] == "project_name":
            continue

        # If the answer is still None, go through the prompt session
        if answer is None:
            default_answer = project_data.get(item["key"], "")
            # Always use session.prompt() even if default_answer is an empty string
            answer = get_input_from_prompt(item["question"], default_answer)
            project_data[item["key"]] = answer if answer else default_answer

        # Don't overwrite the project name if in edit mode
        if not (is_editing and item["key"] == "project_name"):
            project_data[item["key"]] = answer if answer else default_answer

    return project_data


def save_project_data(name, project_data):
    ensure_project_data_folder()
    # check if ./project_data/{name}.json exists, delete it if it does
    if os.path.exists(f"./project_data/{name}.json"):
        os.remove(f"./project_data/{name}.json")
    with open(f"./project_data/{name}.json", "w") as f:
        json.dump(project_data, f)


def run(project_data):
    from autocoder.main import main as autocoder
    autocoder(project_data)
    sys.exit(0)


def ensure_project_data_folder():
    os.makedirs("./project_data", exist_ok=True)


def get_existing_projects():
    ensure_project_data_folder()
    return [f[:-5] for f in os.listdir("./project_data") if f.endswith(".json")]


def choose_project():
    return button_dialog(
        title="Project name",
        text="Choose a project:",
        buttons=[(name, name) for name in get_existing_projects()] + [("Back", "Back")],
        style=style,
    ).run()


def new_or_edit_project(is_editing=False):
    project_name = ""
    if is_editing:
        project_name = choose_project()
        if project_name == "Back":
            return
        with open(f"./project_data/{project_name}.json") as f:
            project_data = json.load(f)
        project_data = get_project_details(
            project_data, is_editing=is_editing
        )  # Update the project_data dict
    else:
        project_data = get_project_details()

    # Use the chosen project_name for 'Edit' case
    project_name = project_name if is_editing else project_data["project_name"]

    save_project_data(project_name, project_data)
    print("Project saved.")

    action = button_dialog(
        title="Run project?",
        text="Do you want to run this project now?",
        buttons=[
            ("Yes", "Yes"),
            ("No", "No"),
        ],
        style=style,
    ).run()

    if action == "Yes":
        run(project_data)


def main():
    project_path = None

    if "--project" in sys.argv:
        project_path = sys.argv[sys.argv.index("--project") + 1]

    while not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY env var is not set. Enter it here:")
        api_key = input("Enter your API key: ")
        if not api_key.startswith("sk-") or len(api_key) < 8:
            print("Invalid API key.")
            api_key = input("Enter your API key: ")
        else:
            with open(".env", "w") as f:
                f.write(f"OPENAI_API_KEY={api_key}")
            os.environ["OPENAI_API_KEY"] = api_key

    if project_path is not None:
        with open(f"./project_data/{project_path}.json") as f:
            run(json.load(f))

    while True:
        existing_projects = get_existing_projects()
        has_projects = bool(existing_projects)

        buttons = [
            ("New", "New"),
        ]

        if has_projects:
            buttons += [
                ("Edit", "Edit"),
                ("Run", "Run"),
                ("Delete", "Delete"),
            ]
        buttons += [("Quit", "Quit")]

        action = button_dialog(
            title="autocoder",
            text="Choose an action:",
            buttons=buttons,
            style=style,
        ).run()

        if action == "Quit":
            break
        elif action == "New":
            new_or_edit_project(is_editing=False)
        elif action == "Edit" and has_projects:
            new_or_edit_project(is_editing=True)
        elif action == "Run" and has_projects:
            project_name = choose_project()
            if project_name == "Back":
                continue
            with open(f"./project_data/{project_name}.json") as f:
                run(json.load(f))
        elif action == "Delete" and has_projects:
            delete_project()

        if not get_existing_projects():
            continue



def delete_project():
    project_name = choose_project()
    if project_name == "Back":
        return

    action = button_dialog(
        title="Confirm Deletion",
        text=f'Are you sure you want to delete the project "{project_name}"?',
        buttons=[
            ("Yes", "Yes"),
            ("No", "No"),
        ],
        style=style,
    ).run()

    if action == "Yes":
        # Delete the project
        os.remove(f"./project_data/{project_name}.json")
        print(f'Project "{project_name}" has been deleted.')
        # If no projects remain, return to the main menu immediately
        if not get_existing_projects():
            return


if __name__ == "__main__":
    main()
