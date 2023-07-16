import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

from autocode.main import main


def terminal():
    if os.path.exists(".env"):
        # read from it if it does
        with open(".env", "r") as f:
            for line in f.readlines():
                key, value = line.strip().split("=", 1)
                os.environ[key] = value
                break
    project_path = None

    if "--project_path" in sys.argv:
        project_path = sys.argv[sys.argv.index("--project_path") + 1]

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

    # Ask the user if they want to create a project or use an existing one
    if project_path is None:
        project_path = input(
            "Do you want to create a new project or use an existing one? [ (c)reate | (e)xisting ]"
        )
        if project_path.lower().startswith("c"):
            project_name = input("What is the name of your project? ")
            project_path = f"projects/{project_name}.json"
            goal = input("What is the goal of your project? ")
            project_dir = f"projects/{project_name}"
            if not os.path.exists(project_dir):
                os.makedirs(project_dir)
            project_data = {
                "name": project_name,
                "goal": goal,
                "project_dir": project_dir,
                "project_path": project_path,
            }
            with open(project_path, "w") as f:
                json.dump(project_data, f)
        elif project_path.lower().startswith("e"):
            project_path = input("What is the name or path of your project file? ")

            # if project_path doesn't contain any "/" or ".json", its a project name
            if "/" not in project_path and ".json" not in project_path:
                project_path = f"projects/{project_path}.json"

            if os.path.exists(project_path) == False:
                print("That project does not exist.")
                project_path = None
                sys.exit(1)
        else:
            print("Invalid option.")
            project_path = None
            sys.exit(1)

    # load file and read json
    project_data = json.load(open(project_path))
    return [project_data]


[project_data] = terminal()
main(project_data)