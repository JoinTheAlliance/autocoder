import os
from time import sleep
from dotenv import load_dotenv
import subprocess
import shutil

load_dotenv()


def test_create_hello_world_e2e():
    api_key = os.getenv("OPENAI_API_KEY")

    project = {
        "project_name": "helloworld_e2e",
        "goal": "print hello world if the main file is run",
        "project_dir": "project_data/helloworld_e2e",
        "log_level": "debug",
        "step": False,
        "api_key": api_key,
    }

    from autocoder import autocoder

    loop_data = autocoder(project)
    while loop_data["thread"].is_alive():
        sleep(1)

    output = subprocess.check_output(
        ["python", "project_data/helloworld_e2e/main.py"]
    ).decode("utf-8")
    assert "hello world" in output.lower()
    # remove the project_data/helloworld_e2e folder
    shutil.rmtree("project_data/helloworld_e2e")
