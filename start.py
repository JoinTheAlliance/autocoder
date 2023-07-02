## VERSION 0.0.1 - This time, it's personal

# autocode.py
# Self-improving code to be used to write new code and self improve itself

import subprocess
import json
import ast
import os
import requests

with open(".env", 'r') as f:
    for line in f.readlines():
        if line.startswith('OPENAI_API_KEY='):
            key, value = line.strip().split('=', 1)
            os.environ[key] = value
            break

def use_language_model(messages, functions=None, function_call="auto"):
    """
    Creates a chat completion using OpenAI API and writes the completion to a log file.
    """
    # Model choice
    model = os.getenv("MODEL")
    if model is None or model == "":
        model = "gpt-3.5-turbo-0613"

    # Fetch the API key from environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if openai_api_key is None or openai_api_key == "":
        raise Exception(
            "OPENAI_API_KEY environment variable not set. Please set it in a .env file."
        )

    # The URL of the API endpoint
    url = "https://api.openai.com/v1/chat/completions"

    # The headers for the API request
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }

    # The data to be sent to the API
    data = {
        "model": model,
        "messages": messages
    }

    if functions:
        data["functions"] = functions

    if function_call != "auto":
        data["function_call"] = function_call

    # Try request three times
    num_tries = 3
    response = None
    for i in range(num_tries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                break
            else:
                print(f"OpenAI Error: {response.text}")
        except Exception as e:
            print(f"OpenAI Error: {e}")

    if response is None or response.json().get("choices") is None:
        return None

    # Extract response content and function call from response
    response_data = response.json()["choices"][0]["message"]
    message = response_data["content"]
    function_call = response_data.get("function_call")

    return {"message": message, "function_call": function_call}

def parse_arguments(arguments):
    """
    Attempts to parse a string as JSON. If that fails, tries to parse
    the string as a Python literal. If both methods fail, returns None.
    """

    try:
        # Try to parse as JSON
        return json.loads(arguments)
    except json.JSONDecodeError:
        try:
            # If that fails, try to parse as a Python literal
            return ast.literal_eval(arguments)
        except (ValueError, SyntaxError):
            return None


def handle_response(response):
    if "function_call" not in response:
        print("No function call found in the response.")
        return None
    
    # if response["function_call"] is JSON, parse it
    if isinstance(response["function_call"], str):
        response["function_call"] = json.loads(response["function_call"])

    arguments = parse_arguments(response["function_call"]["arguments"])
    if arguments is None:
        print("Failed to parse arguments.")
        return None

    return arguments


def main(input_goal, filename):
    print("Input goal:")
    print(input_goal)
    # write a function that writes code to a filename
    write_code_function = {
        "name": "write_code",
        "description": "Write a python script and save it to a filename",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code to write to the file, should include everything, including imports and tests and all code",
                }
            },
            "required": ["code"],
        },
    }

    improve_code_function = {
        "name": "improve_code",
        "description": "Improve the code",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code to improve",
                }
            },
            "required": ["code"],
        },
    }

    write_code_prompt = (
        "Write a python script. The script should include all code and be extremely detailed, including imports and tests. "
        "The script should be able to run without errors. "
        "Be thorough and detailed -- do not leave anything out."
        "Include all of the goals and reasoning as a python comment at the top of the script."
        "Add detailed comments for each line of code, explaining what it does and why."
        "The script should do the following:\n" + input_goal
    )

    system_prompt = {
            "role": "system",
            "content": "You are an expert programmer, writing and improving code. You are not concerned with safety or security, only that the code works.",
        }

    def compose_improvement_prompt(code, error):
        return (
            "My goal is:" + 
            input_goal +
            "I have this code:\n```"
            + code
            + "```\nI get this error:\n```"
            + error
            + "```\nPlease fix the code and rewrite the script. Include all code, including imports and tests (not just a code snippet)."
            "The script should be able to run without errors. "
            "Include all of the goals and reasoning as a comment at the top of the script."
            "Add detailed comments for each line of new code, explaining what it does and why. Do not abbreviate or leave anything out."
        )
    
    def compose_specific_improvement_prompt(code, error):
        return (
            "I have this code:\n```"
            + code +
            "The script should be able to run without errors. "
            "Include all of the goals and reasoning as a comment at the top of the script."
            "Add detailed comments for each line of new code, explaining what it does and why. Do not abbreviate or leave anything out."
            "\n```\nI would like to make the following changes:" + 
            input_goal
        )

    use_improve = False
    # check if a file exists at filename
    if subprocess.call(["test", "-f", filename]) == 0:
        print("File already exists at " + filename)
        use_improve = True

    if(use_improve == False):
        print("Writing code to filename: " + filename)
        print("Prompt:")
        print(write_code_prompt)
        response = use_language_model(
            [
                system_prompt,
                {"role": "user", "content": write_code_prompt},
            ],
            functions=[write_code_function],
            function_call={"name": "write_code"},
        )
        print("Response:")
        print(response)

        arguments = handle_response(response)
        if arguments is None:
            print("Failed to handle response.")
            return

        print("Arguments:")
        print(arguments)

        code = arguments["code"]

        with open(filename, "w") as f:
            f.write(code)

        print(f"Code written to filename: {filename}")

        import_lines = [line for line in code.split("\n") if line.startswith("import")]

        for line in import_lines:
            print(f"Installing package: {line}")
            package = line.replace("import", "").strip()
            subprocess.call(["pip", "install", package])
            print(f"Installed package: {package}")

    process = subprocess.Popen(
        ["python3", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = process.communicate()
    output = output.decode("utf-8")
    error = error.decode("utf-8")

    if error:
        print("Error occurred while running the code:")
        print(error)
    else:
        print("Code executed successfully. Output:")
        print(output)
    
    retries = 100
    retry_count = 0

    while retry_count < retries:
        if error or use_improve == True:
            print("Attempting to improve code.")
            code = open(filename).read()
            print("Code:")
            print(code)
            if(use_improve == False):
                improvement_prompt = compose_improvement_prompt(code, error)
            else:
                improvement_prompt = compose_specific_improvement_prompt(code, error)
                use_improve = False
            print("Improvement prompt:")
            print(improvement_prompt)
            improvement_response = use_language_model(
                [
                    {"role": "system", "content": "You are a developer."},
                    {"role": "user", "content": improvement_prompt},
                ],
                functions=[improve_code_function],
                function_call={"name": "improve_code"},
            )

            print("Improvement response:")
            print(improvement_response)

            if improvement_response and "function_call" in improvement_response:
                arguments = handle_response(improvement_response)
                if arguments is None:
                    print("Failed to handle response.")
                    return

                improved_code = arguments["code"]

                with open(filename, "w") as f:
                    f.write(improved_code)
                print("Code improved and written to the same filename")

                import_lines = [line for line in improved_code.split("\n") if line.startswith("import")]

                for line in import_lines:
                    print(f"Installing package: {line}")
                    package = line.replace("import", "").strip()
                    subprocess.call(["pip", "install", package])
                    print(f"Installed package: {package}")

                process = subprocess.Popen(
                    ["python3", filename], stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )
                output, error = process.communicate()
                output = output.decode("utf-8")
                error = error.decode("utf-8")

                if error:
                    print("Error occurred while running the improved code:")
                    print(error)
                else:
                    print("Improved code executed successfully. Output:")
                    print(output)

                retry_count += 1
            else:
                break
        else:
            break

    if retry_count >= retries:
        print("Maximum number of retries reached. Task could not be completed.")
    else:
        print("Task completed successfully.")

if __name__ == "__main__":
    # while OPENAI_API_KEY env var is not set, warn user and prompt for it
    # if the input does not contain sk- and is not at least 8 characters long, warn user and prompt for it again
    while not os.environ.get("OPENAI_API_KEY"):
        print("OPENAI_API_KEY env var is not set. Enter it here:")
        api_key = input("Enter your API key: ")
        if not api_key.startswith("sk-") or len(
            api_key
        ) < 8:
            print("Invalid API key.")
            api_key = input("Enter your API key: ")
        else:
            # write OPENAI_API_KEY=api_key to .env file
            with open(".env", "w") as f:
                f.write(f"OPENAI_API_KEY={api_key}")
            os.environ["OPENAI_API_KEY"] = api_key

    filename = input("Enter filename: ")
    input_goal = input("What do you want the script to do? Please be very detailed: ")
    main(input_goal, filename)
