<img src="resources/autocode.jpg" width="100%">

# autocode
Code that basically writes itself.

To run with a prompt
```
python start.py
```

To run "headless" (without being prompted)
```
python3 start.py --project midi_generator
```

# Context
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
```