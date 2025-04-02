# Documentation: File and Folder Structure

Below is a description of the general file and folder structure in the project, along with how conda environments can be used, and how each element is typically utilized. **All executable scripts for stages should be named `app.py`** to maintain consistency.

## Project Structure

- **Project root**
    - `manifest.json` — The main project manifest (if used). It may contain common settings or link individual pipeline stages.
    - Other files not related to a specific stage.

- **Stage folders** (for example, `load_anndata`, `clustering`, `dimensionality_reduction`)
    1. **`manifest.json`** (inside the stage folder)
        - Describes the key parameters required by this stage.
        - Contains the stage name, its description, execution order (`stage`), types and requirements of input parameters (`params`), and information about returned data (`return`).
        - May specify dependencies (e.g., `depends_and_script` or `depends_or_script`) and the environments used (`conda`, `libs`, `conda_pip`).
            - **Conda usage**: If `conda` is specified, the system creates or uses a conda environment with the requested Python version and installs the listed libraries (`libs` via conda, `conda_pip` via pip in that conda environment). This isolation helps avoid library conflicts.

    2. **`app.py`** (the executable script for this stage)
        - This file name should **always** be `app.py` to maintain a consistent structure.
        - It contains the core business logic: reading data, transforming it, analyzing it, and producing output.
        - Typically, it defines a function (often `run(**kwargs)`) that:
            1. **Imports the necessary dependencies** (e.g., `scanpy`, `scvi`, `numpy`).
            2. **Reads parameters** from `kwargs`, which are provided from `manifest.json` (e.g., file path, analysis method, metrics).
            3. **Calls a helper function** or a series of functions that perform the main logic (e.g., data loading, clustering, dimensionality reduction, etc.).
            4. **Returns the result** in the format described in the manifest (usually a dictionary where the keys match the fields in `return`).

### Example `app.py` Structure

1. **Import libraries**
   ```python
   import scanpy as sc
   import numpy as np
   import pandas as pd
   # ...
   ```
2. **Define helper functions** (e.g., `reduce_dimensionality`, `cluster`, `load_data`)
   ```python
   def reduce_dimensionality(adata, method='pca', ...):
       # Dimensionality reduction logic
       return adata
   ```
3. **`run(**kwargs)` function**
   ```python
   def run(**kwargs):
       # Read arguments
       adata = kwargs.get('adata')
       method = kwargs.get('method', 'pca')
       # ...
       # Call a helper function
       out = reduce_dimensionality(adata, method=method)
       # Return the result
       return { 'adata': out }
   ```

## Main Purpose

1. **`manifest.json`** in each folder:
    - Defines which parameters the stage requires and what data it returns.
    - Specifies the execution order in the pipeline.
    - Allows you to determine which libraries (conda or pip) are needed for the stage.
    - May include version constraints for packages.
    - **Conda Environments**: If `conda` is specified, the system will create/use the indicated environment (for example, `python=3.11`) and install the specified libraries.

2. **`app.py`**:
    - Performs the main work — processes data using parameters obtained from `manifest.json`.
    - Produces output that subsequent stages can access.
    - Has a structure consisting of several steps:
        - Imports
        - Helper functions
        - `run(**kwargs)` function — the entry point.

## Example Project Structure

```text
project_root/
├── manifest.json               # Main (root) manifest, if present
├── load_anndata/
│   ├── manifest.json           # Manifest for the loading stage
│   └── app.py                  # Script performing data loading
├── clustering/
│   ├── manifest.json           # Manifest for the clustering stage
│   └── app.py                  # Script for clustering data
├── dimensionality_reduction/
│   ├── manifest.json           # Manifest for the dimensionality reduction stage
│   └── app.py                  # Script performing the analysis
└── other_folders_or_files      # Other files/folders in the project
```

## Usage Recommendations
- Store a maximum of one stage in **each folder** (with its own `manifest.json` and `app.py`).
- The **main manifest** can set the overall pipeline logic or serve as the entry point for the entire system.
- Each `app.py` should be as focused as possible, making the stage easier to test, modify, and reuse.
- Parameters in `manifest.json` should be described in as much detail as possible so that users understand what is required as input and what will be returned as output.
- **Conda Environments**: When `conda` is specified, each stage can be isolated in its own environment to avoid library version conflicts across different scripts.
