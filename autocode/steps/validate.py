from agentevents import (
    get_epoch,
    increment_epoch,
)

def validate(context):
    """
    This function serves as the 'Orient' stage in the OODA loop. It uses the current context data to summarize the previous epoch and formulate a plan for the next steps.

    Args:
        context (dict): The dictionary containing data about the current state of the system.

    Returns:
        dict: The updated context dictionary after the 'Orient' stage, including the summary of the last epoch, relevant knowledge, available actions, and so on.
    """
    epoch = increment_epoch()

    if epoch == 1:
        print("Starting code generation.")

    context["epoch"] = get_epoch()
    context["last_epoch"] = str(get_epoch() - 1)
    
    # TODO: run project-wide validation

    # TODO: if no files, just skip directly to create entrypoint

    # if files, run validation on each file, then run tests, then run main on the entrypoint

    # store text for any files that changed this epoch

    # 
    
    return context
