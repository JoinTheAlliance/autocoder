import os
import sys
from core.autocode import main


def terminal():
    if os.path.exists(".env"):
        # read from it if it does
        with open(".env", "r") as f:
            for line in f.readlines():
                key, value = line.strip().split("=", 1)
                os.environ[key] = value
                break
    filename = None
    goal = None

    if "--improve" in sys.argv:
        goal = "Write one or more tests to validate the functions and add them to the bottom of the script. Add test cases to ensure that the tests work. The tests should use assert and only run if __name__ == '__main__' at the bottom of the script. If there are any errors in the code, fix them. Your reponse should strt with 'import os' and end with the tests."
        filename = "autocode.py"
        if "--utils" in sys.argv:
            filename = "utils.py"
        elif "--start" in sys.argv:
            filename = "start.py"
        elif "--language_model" in sys.argv:
            filename = "language_model.py"
        return [goal, filename]

    else:
        if "--filename" in sys.argv:
            filename = sys.argv[sys.argv.index("--filename") + 1]
        if "--goal" in sys.argv:
            goal = sys.argv[sys.argv.index("--goal") + 1]

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

    if filename is None:
        filename = input("Enter filename: ")
    if goal is None:
        goal = input("What do you want the script to do? Please be very detailed: ")
    return [goal, filename]


[goal, filename] = terminal()
main(goal, filename)

if __name__ == "__main__":
    # TESTS GO HERE
    pass
