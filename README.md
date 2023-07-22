# autocoder <a href="https://discord.gg/qetWd7J9De"><img style="float: right" src="https://dcbadge.vercel.app/api/server/qetWd7J9De" alt=""></a>
Code that basically writes itself.

# IN PROGRESS - v2 coming soon

<img src="resources/image.jpg" width="100%">

To run with a prompt
```
python start.py
```

To run "headless" (without being prompted)
```
python3 start.py --project midi_generator
```

# Context
Over the course of the loop, a context object gets built up which contains all of the data from the previous steps. This can be injeced into prompt templates using the `compose_prompt` function.

Here is the data that is available in the context object at each step:
```python
# Initial context object
context = {
    epoch,
    name,
    goal,
    project_dir,
    project_path
}

# Added by orient step
context = {
    file_count,
    filetree,
    filetree_formatted,
    python_files,
    main_success,
    main_error,
    backup,
    project_code: [{
        rel_path,
        file_path,
        content,
        validation_success,
        validation_error,
        test_success,
        test_error,
        test_output,
    }],
    project_code_formatted
}

# Added by decide step
context = {
    action_name,
    reasoning
}

# Final context for actions
context = {
    epoch, # current iteration of the loop
    name, # project name
    goal, # project goal
    project_dir,
    project_path,
    file_count,
    filetree,
    filetree_formatted, # formatted for prompt template
    python_files,
    main_success, # included in project_code_formatted
    main_error, # included in project_code_formatted
    backup,
    project_code: [{
        rel_path,
        file_path,
        content,
        validation_success,
        validation_error,
        test_success,
        test_error,
        test_output,
    }],
    project_code_formatted, # formatted for prompt template
    action_name,
    reasoning # formatted for prompt template
}
```

<img src="resources/youcreatethefuture.jpg" width="100%">
