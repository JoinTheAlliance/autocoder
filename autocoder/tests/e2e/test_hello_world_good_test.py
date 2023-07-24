import os
from time import sleep
from dotenv import load_dotenv
import subprocess
import shutil

load_dotenv()

main_py = """\
def main():
    print("hello world")


if __name__ == "__main__":
main()
"""

main_test_py = """\
def test_main(capsys):
    captured = capsys.readouterr()

    from main import main
    main()

    captured = capsys.readouterr()
    assert captured.out == "hello world2\n"
"""


def test_create_hello_world_good_test():
    api_key = os.getenv("OPENAI_API_KEY")

    project = {
        "project_name": "helloworld_e2e_goodtest",
        "goal": "print hello world if the main file is run",
        "project_dir": "project_data/helloworld_e2e_goodtest",
        "log_level": "debug",
        "step": False,
        "api_key": api_key,
    }

    os.makedirs("project_data/helloworld_e2e_goodtest")
    with open("project_data/helloworld_e2e_goodtest/main.py", "w") as f:
        f.write(main_py)

    with open("project_data/helloworld_e2e_goodtest/main_test.py", "w") as f:
        f.write(main_test_py)

    from autocoder import autocoder

    loop_data = autocoder(project)
    while loop_data["thread"].is_alive():
        sleep(1)

    output = subprocess.check_output(
        ["python", "project_data/helloworld_e2e_goodtest/main.py"]
    ).decode("utf-8")
    assert "hello world" in output.lower()
    # remove the project_data/helloworld_e2e folder
    shutil.rmtree("project_data/helloworld_e2e_goodtest")
