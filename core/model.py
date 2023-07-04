import os
import json
import requests
import ast
import sys
import re
from core.utils import log

def use_language_model(messages, functions=None, function_call="auto", filename=None):
    # check if --model is passed in
    model = None
    if "--model" in sys.argv:
        model_index = sys.argv.index("--model")
        model = sys.argv[model_index + 1]
        if model.startswith("-"):
            log(filename, "INVALID MODEL.")
            return
        sys.argv.pop(model_index)
        sys.argv.pop(model_index)
    if model is None or model == "":
        model = os.getenv("OPENAI_MODEL") or "gpt-3.5-turbo-0613"

    # only 0613 models support function calling for now
    if "3.5" in model:
        model = "gpt-3.5-turbo-0613"
    # check if model includes 4
    elif "4" in model:
        model = "gpt-4-0613"

    openai_api_key = os.getenv("OPENAI_API_KEY")

    if openai_api_key is None or openai_api_key == "":
        raise Exception(
            "OPENAI_API_KEY environment variable not set. Please set it in a .env file."
        )

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {openai_api_key}",
    }

    data = {"model": model, "messages": messages}

    if functions:
        data["functions"] = functions

    if function_call != "auto":
        data["function_call"] = function_call

    num_tries = 3
    response = None
    
    for i in range(num_tries):
        log(filename, f"EPOCH CYCLE {i+1}/{num_tries}")
        i = i + 1
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data))
            if response.status_code == 200:
                break
            else:
                log(filename, f"OpenAI Error: {response.text}")
        except Exception as e:
            log(filename, f"OpenAI Error: {e}")

    if response is None or response.json().get("choices") is None:
        if num_tries >= 3:
            response = None
        else:
            response = use_language_model(messages, functions, function_call, filename=filename)
    else:
        response_data = response.json()["choices"][0]["message"]
        message = response_data["content"]
        function_call = response_data.get("function_call")

        response = {"message": message, "function_call": function_call}

    if response is None:
        log(filename, "NO RESPONSE FROM GENERATION API API.")
        return None

    if "function_call" not in response:
        log(filename, "NO FUNCTION DETECTED IN THE RESULT.")
        return None

    if "arguments" in response["function_call"]:
        arguments = response["function_call"]["arguments"]
        if isinstance(arguments, str):
            arguments = parse_arguments(response["function_call"]["arguments"])
    if arguments is None:
        return None

    return arguments


def parse_arguments(arguments):
    if isinstance(arguments, dict) or isinstance(arguments, list):
        return arguments
    try:
        if isinstance(arguments, str):
            return json.loads(arguments)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(arguments)
        except (ValueError, SyntaxError):
            try:
                arguments = re.sub(r"[\r\n]+", "\n", arguments)
                arguments = re.sub(r"[^\x00-\x7F]+", "", arguments)
                return json.loads(arguments)
            except (ValueError, SyntaxError):
                return None


if __name__ == "__main__":
    # TESTS
    # Test parse_arguments
    test_input = '{"key1": "value1", "key2": 2}'
    expected_output = {"key1": "value1", "key2": 2}
    assert parse_arguments(test_input) == expected_output, "Test parse_arguments failed"

    # Test use_language_model
    test_messages = [{"role": "system", "content": "You are a helpful assistant."}, {"role": "user", "content": "Write a song about AI"}]
    test_functions = [{
        "name": "write_song",
        "description": "Write a song about AI",
        "parameters": {
            "type": "object",
            "properties": {
                "lyrics": {
                    "type": "string",
                    "description": "The lyrics for the song",
                }
            },
            "required": ["lyrics"]
        }
        }]
    test_filename = "test_filename"
    arguments = use_language_model(test_messages, test_functions, { "name": "write_song"}, test_filename)
    print(arguments["lyrics"])
    assert isinstance(arguments, dict), "Test use_language_model failed"

    print('All tests complete!')