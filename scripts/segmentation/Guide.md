# Guide to Creating Scripts
## Introduction
This project provides a unique opportunity for users to create their own scripts and plugins, granting additional functionality and flexibility.

Each script you create will be represented by two main files: `app.py` and `manifest.json`. `app.py` contains Python code that performs the task required. `manifest.json` is metadata describing the function, dependencies, and parameters of the script.

All scripts should be organized in their respective folders, matching the path specified in `script_path`.

## Root manifest.json File
In the root folder of the project, there should be a `manifest.json` file that determines the order of script stages and their names.

Example:

```json
{
  "name": "Segmentation",
  "description": "",
  "order": 1,
  "stages": [
    "Loading",
    "Preprocessing",
    "Cell segmentation",
    "Post processing",
    "Feature extraction"
  ]
}
```

# Creating a Script
## app.py File

The app.py file contains Python code that performs the script's functions. This file should include a run function, which takes arguments and returns a dictionary of results.
The input arguments should match the parameters defined in the manifest.json file.
Example of run function:

```python
def run(**kwargs):
  # your code here
  return {'result': result}
```

## manifest.json File

The `manifest.json` file describes the metadata of the script, including its function, dependencies, parameters, and returned values.

The main fields in the `manifest.json` file include:

- `description`: a brief description of the script's function.
- `name`: a unique name of the script.
- `stage`: grouping of scripts by stages (e.g., preprocessing, processing, post-processing).
- `params`: a dictionary of parameters that can be passed to the script. Each parameter has the following attributes:
  - `name`: the name of the parameter.
  - `description`: a description of the parameter.
  - `type`: the data type of the parameter.
  - `hidden`: if true, the parameter is hidden from the user.
  - `default`: the default value for the parameter.
  - `required`: if true, the parameter is mandatory.
- `script_path`: the relative path to the script directory.
- `return`: a dictionary of values returned by the script.
- `depends_and_script`: a list of scripts that must be executed before this script.
- `depends_or_script`: a list of scripts, one of which must be executed before this script.
- `libs`: a list of Python libraries required to execute the script.
