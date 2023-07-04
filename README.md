<img src="resources/autocode.png" width="100%">

# autocode
Code that basically writes itself.

To run with a prompt
```
python start.py
```

To run "headless" (without being prompted)
```
python start.py --filename hello_wikipedia.py --goal "Write a program that searches wikipedia for Hello World and saves the article to hello_world.txt"
```

To run from a shell script (convenient!)
```
# edit the start.sh file to change the filename and goal
bash start.sh
```

To run with a different model
```
# available models are gpt-3.5-turbo-0613 or gpt-4-0613, 3.5 or 4 will work as args, too
python start.py --model <model_name>
```

Type in the name of the file -- you can select one that exists, or a new file. Give instructions for what you want to do-- either improvements to an existing file, or instructions for a new file. Let it cook for a while, then give it a try once the task is done.

To self-improve autocode
```
python start.py --filename core/utils.py --goal "Improve the autocode program by adding robust tests for each function, as well as descriptive docstrings."
```

If your improvements are good, please submit a pull request.
