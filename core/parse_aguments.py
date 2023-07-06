import json
import ast


def parse_arguments(arguments):
    print("Parsing arguments")
    if isinstance(arguments, (dict, list)):
        return arguments
    if isinstance(arguments, str):
        try:
            return json.loads(arguments)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(arguments)
            except (ValueError, SyntaxError):
                print("Error, could not parse arguments")
                return None


if __name__ == "__main__":
    with open("response.json", "r") as f:
        # parse f to json
        response = json.loads(f.read())
        # get the 'function_call' field from the object
        function_call = response["function_call"]
        # get the arguments from the function_call
        arguments = function_call["arguments"]
        print("Arguments before parsing:")
        print(arguments)
        result = parse_arguments(arguments)
        print("Arguments after parsing:")
        print(result)
        assert result is not None, "No return value from parse_arguments"
        assert isinstance(result, (dict, list)), "Return value is not a list or a dict"
    print("All tests complete!")
