import os

def log(filename, text):
    # if log folder doesn't exist, create it
    if not os.path.exists("logs"):
        os.makedirs("logs")
    # print to console
    print(text)
    # save to log.txt
    with open("logs/" + filename + ".log", "a") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    # TESTS GO HERE
    pass  # replace me with tests!
