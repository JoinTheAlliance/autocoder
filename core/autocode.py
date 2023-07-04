from core.utils import file_exists, run_code, save_code, log

from core.validate_code import validate_code
from core.improve_code import improve_code
from core.write_code import write_code


def main(goal, filename):
    run_improvement = True
    if file_exists(filename) == False:
        run_improvement = False
        retries = 0
        max_retries = 3
        while retries < max_retries:
            retries += 1
            code = write_code(filename, goal)
            if code is None:
                log(filename, "Failed to write code.")
                continue
            break

    retries = 100
    retry_count = 0

    # read the code
    original_code = open(filename).read()
    [error, _] = run_code(filename)
    while retry_count < retries:
        retry_count += 1
        if error or run_improvement == True:
            run_improvement = False # always run improvement at least once, even if code already works
            [success, error, output] = improve_code(filename, goal, error)
            if success:
                validation = validate_code(filename, goal, output)
                if validation["success"]:
                    log(
                        filename,
                        "THE EXPERIMENT WAS GENERATED. READY FOR MANUAL TESTING.",
                    )
                    break
                if validation["revert"]:
                    log(
                        filename,
                        "EXPERIMENT EXPERIENCED CATASTROPHIC ERROR. REVERTING TO PREVIOUS STATE",
                    )
                    save_code(original_code, filename)
        else:
            break

    if retry_count < retries:
        log(filename, "GENERATION COMPLETE. GOOD LUCK.")


if __name__ == "__main__":
    # TESTS GO HERE
    pass  # replace me with tests!
