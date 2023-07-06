import os

from core.logger import log
from core.code import run_code, save_code
from core.validation import file_exists
from core.validate_code import validate_code
from core.improve_code import improve_code
from core.write_code import write_code

def main(goal, filename):
    retries =  os.environ.get("MAX_RETRIES", 1000) or 1000
    print("RUNNING AUTOCODER")
    if file_exists(filename) == False:
        retries = 0
        max_retries = 3
        while retries < max_retries:
            retries += 1
            code = write_code(filename, goal)
            if code is None:
                log(filename, "Failed to write code.")
                continue
            break

    retry_count = 0

    # read the code
    original_code = open(filename).read()
    [error, _] = run_code(filename)
    while retry_count < retries:
        retry_count += 1
        # always run at least once
        if error or retry_count == 1:
            [success, error, output] = improve_code(filename, goal, error)

            # something went wrong, feed the error back into the model and run it again
            if error or success == False:
                log(filename, "THE IMPROVEMENT EXPERIMENT FAILED. RECALIBRATING...")
                continue

            validation = validate_code(filename, goal, output)

            log(filename, validation["explanation"])
            # passed validation, finish up
            if validation["success"]:
                log(
                    filename,
                    "THE EXPERIMENT PASSED AUTOMATIC VALIDATION. READY FOR MANUAL TESTING.",
                )
                error = None
                break
            # validation failed
            else:
                error = validation["explanation"]
                # if revert is true, revert to the last version of the code
                if validation["revert"]:
                    log(
                        filename,
                        "EXPERIMENT EXPERIENCED CATASTROPHIC ERROR. REVERTING TO PREVIOUS STATE",
                    )
                    save_code(original_code, filename)
                log(
                    filename,
                    "THE EXPERIMENT FAILED TO VALIDATE. RECALIBRATING...",
                )
        else:
            break

    if retry_count < retries:
        log(filename, "GENERATION COMPLETE. GOOD LUCK.")


if __name__ == "__main__":
    # TESTS GO HERE
    pass  # replace me with tests!
