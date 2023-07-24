
# hello world should JUST work. The project should not need to be edited, if the create handler is working correctly.
# steps
# 1. create project from command line
# 2. start loop

def test_create_hello_world_e2e():
    project = {
        "project_name": "helloworld",
        "goal": "print hello world if the main file is run",
        "project_dir": "project_data/helloworld",
        "project_path": "project_data/helloworld.json"
    }
    # create the json file
    # start autocoder in step mode
    # step autocoder one time
    # check that the project is valid