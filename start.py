import os
import sys
from autocode.main import main


def terminal():
    if os.path.exists(".env"):
        # read from it if it does
        with open(".env", "r") as f:
            for line in f.readlines():
                key, value = line.strip().split("=", 1)
                os.environ[key] = value
                break
    goal = None

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

    if goal is None:
        goal = input("What do you want the script to do? Please be very detailed: ")
    return [goal, filename]


[goal, filename] = terminal()
main(goal)

if __name__ == "__main__":
    # TESTS GO HERE
    pass
