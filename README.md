[![CI](https://github.com/cmelab/planckton-flow/workflows/CI/badge.svg)](https://github.com/cmelab/planckton-flow/actions?query=workflow%3ACI)
# PlanckTon-Flow

## How to use (local)

### Install

1. First download PlanckTon-flow:
```
git clone git@github.com:cmelab/planckton-flow.git
cd planckton-flow
```

2. Then install its requirements:
```
pip install -r requirements.txt
```

PlanckTon-flow is not a python package, so it does not need to be installed.
Before using PlanckTon-flow, read over [Signac and Signac-flow](http://docs.signac.io)

In order to use PlanckTon-flow, the PlanckTon container must be pulled to your machine and its location assigned the environment variable `$PLANCKTON_SIMG`.
The following example shows the container pulled to a directory called `~/images`:
```
singularity pull docker://cmelab/planckton_cpu:0.1.5
export PLANCKTON_SIMG="~/images/planckton_cpu_0.1.5.sif"
```

The basic workflow is something like this:

1. Edit the init file to define state point space
```
vim src/init.py
```
2. Run the init script to create a workspace
```
python src/init.py
```
3. Submit the project script to run your simulations
```
python src/project.py submit
```

`src/project.py` contains all of the job operations.

## How to use (cluster)

Beyond the officially supported [flow environments](https://docs.signac.io/projects/flow/en/latest/supported_environments.html#supported-environments) we support:

* Fry
* Kestrel

When working on a cluster, we will be using singularity.
Then the workflow is the same as local, except now the jobs will be submitted to the scheduler 

1. Edit the init file to define state point space
```
vim src/init.py
```
2. Run the init script to create a workspace
```
python src/init.py
```
3. Check to make sure your jobs look correct
```
python src/project.py submit --pretend 
```
4. Submit the project script to run your simulations
```
python src/project.py submit
```
