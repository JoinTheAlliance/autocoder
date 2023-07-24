# autocoder <a href="https://discord.gg/qetWd7J9De"><img style="float: right" src="https://dcbadge.vercel.app/api/server/qetWd7J9De" alt=""></a>

Code that basically writes itself.

<img src="resources/image.jpg" width="100%">

# Quickstart

To run with a prompt

```
python start.py
```

To use autocoder inside other projects and agents

```python
from autocoder import autocoder
data = {
    "project_name": "random_midi_generator", # name of the project
    "goal": "Generate a 2 minute midi track with multiple instruments. The track must contain at least 500 notes, but can contain any number of notes. The track should be polyphonic and have multiple simultaneous instruments", # goal of the project
    "project_dir": "random_midi_generator", # name of the project directory
    "log_level": "normal", # normal, debug, or quiet
    "step": False, # whether to step through the loop manually, False by default
    "model": "gpt-3.5-turbo", # default
    "api_key": <your openai api key> # can also be passed in via env var OPENAI_API_KEY
}

autocoder(project_data)
```

# Core Concepts

Autocoder is a ReAct-style python coding agent. It is designed to be run standalone with a CLI or programmatically by other agents.

More information on ReAct (Reasoning and Acting) agents can be found <a href="https://ai.googleblog.com/2022/11/react-synergizing-reasoning-and-acting.html">here</a>.

## Loop

Autocoder works by looping between a "reason"" and "act" step until the project is validated and tested. The loop runs forever but you can enable "step" mode in options to step through the loop manually.

## Actions

Autocoder uses OpenAI function calling to select and call what we call _actions_. Actions are functions that take in a context object and return a context object. They are called during the "act" step of the loop.

## Context

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

# Added by reasoning step
context = {
    reasoning,
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

# Action step context
context = {
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
    available_actions, # list of available actions
    available_action_names, # list of just the action names
    project_code_formatted, # formatted for prompt template
    action_name,
    reasoning, # formatted for prompt template
    project_code: [{
        rel_path,
        file_path,
        content,
        validation_success,
        validation_error,
        test_success,
        test_error,
        test_output,
    }]
}
```

<img src="resources/youcreatethefuture.jpg" width="100%">
