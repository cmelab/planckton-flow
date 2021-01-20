# PlanckTon-flow

## How to use (local)

### Install

First, install [PlanckTon](https://github.com/cmelab/planckton):

```
git clone git@github.com:cmelab/planckton.git
cd planckton
conda env create -f environment.yml
conda activate planckton
pytest
```

Now to get PlanckTon-flow:

```
git clone git@github.com:cmelab/planckton-flow.git
cd planckton-flow
```
PlanckTon-flow is not a python package, so it does not need to be installed.
Before using PlanckTon-flow, read over [Signac and Signac-flow](http://docs.signac.io)

In order to use PlanckTon-flow, the PlanckTon container must be pulled to your machine and its location assigned the environment variable `$PLANCKTON_SIMG`.
For example:
```
singularity pull docker://cmelab/planckton_cpu:0.1.4
export PLANCKTON_SIMG="/home/erjank_project/singularity_images/planckton_cpu_0.1.4.sif"
```

The basic workflow is something like this:

```
# Define state point space
vim src/init.py
# Create workspace
python src/init.py
# Simulate
python src/project.py submit
```

`src/project.py` contains all of the job operations.

## How to use (cluster)

Beyond the officially supported [flow environments](https://docs.signac.io/projects/flow/en/latest/supported_environments.html#supported-environments) we support:

* Fry
* Kestrel

When working on a cluster, we will be using singularity.
We assume the image is located `~/planckton/`.

So, `cd ~/planckton` then `singularity pull docker://cmelab/planckton:beta`
See this [wiki page](https://github.com/cmelab/getting-started/blob/master/wiki/Clusters:%20Tips%20%26%20Tricks%20(The%209th%20one%20will%20SHOCK%20you).md) for per-cluster tips.

Then the workflow is the same as local, except now the jobs will be submitted to the scheduler 
```
# Define state point space
vim src/init.py
# Create workspace
python src/init.py
# Check to make sure things look correct
python src/project.py --pretend submit
# Simulate
python src/project.py submit
```
