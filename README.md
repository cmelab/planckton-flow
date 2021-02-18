[![CI](https://github.com/cmelab/planckton-flow/workflows/CI/badge.svg)](https://github.com/cmelab/planckton-flow/actions?query=workflow%3ACI)
# PlanckTon-Flow

PlanckTon-flow is a lightweight dataspace manager that leverages the [Signac](https://docs.signac.io/en/latest/) framework to submit molecular dynamics simulations of organic photovoltaics using [PlanckTon](https://github.com/cmelab/planckton). PlanckTon-flow works with [Singularity](https://sylabs.io/guides/latest/user-guide/) and is designed for use on supercomputing clusters.

### Install

PlanckTon-flow uses the [conda](https://conda.io/projects/conda/en/latest/user-guide/install/index.html) package manager. Before installing PlanckTon-flow, please install Miniconda.

1. First download PlanckTon-flow:

    ```bash
    git clone git@github.com:cmelab/planckton-flow.git
    cd planckton-flow
    ```

2. Then install its requirements:

    ```bash
    conda env create -f environment.yml
    conda activate planckton-flow
    ```

    PlanckTon-flow is not a python package, so it does not need to be installed.

3. In order to use PlanckTon-flow, the PlanckTon container must be pulled to your machine and its location assigned the environment variable `$PLANCKTON_SIMG`. 
    
    The following example shows the container pulled to a directory called `~/images`:

    ```bash
    cd ~/images
    singularity pull docker://cmelab/planckton_gpu:latest
    export PLANCKTON_SIMG=$(pwd)/planckton_gpu_latest.sif
    ```

    Or you can run this command (while still in the directory where you pulled the image) to add the image location to your bashrc file so you never have to run this step again

    ```bash
    echo "export PLANCKTON_SIMG=$(pwd)/planckton_gpu_latest.sif" >> ~/.bashrc
    ```

And that's it--you are ready to run simulations!

### Run

0. Pre-run steps: 
    1. Make sure singularity is available 
        Fry:
        ```bash
        module load singularity
        ```
        Bridges2: singularity is loaded by default
    2. CUDA libraries are on your path 
        Fry:
        ```bash
        module load cuda
        ```
        Bridges2:
        ```bash
        module load cuda/10
        ```
    3. The conda environment is active 
        ```bash
        conda activate planckton-flow
        ```
    4. The `PLANCKTON_SIMG` variable is set, the basic workflow is something like this:

1. Edit the init file to define state point space

    ```bash
    vim src/init.py
    ```
    
2. Run the init script to create a workspace

    ```bash
    python src/init.py
    ```
    
3. Check to make sure your jobs look correct

    ```bash
    python src/project.py submit --pretend 
    ```

4. Submit the project script to run your simulations

    ```bash
    python src/project.py submit
    ```
    
    `src/project.py` contains all of the job operations.

## Cluster support

Beyond the officially supported [flow environments](https://docs.signac.io/projects/flow/en/latest/supported_environments.html#supported-environments) we support:

* Fry
* Kestrel
