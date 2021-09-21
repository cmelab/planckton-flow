#!/usr/bin/env python
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories.
"""
from itertools import product

import signac


project_name = "my_project"

# Parameters used for generating the morphology
parameters = {
    # input can be the path to a molecule file or a SMILES string
    # or a key to the COMPOUND dictionary in PlanckTon (shown below)
    # The compounds ending with "-gaff" are designed to be used with the
    # "gaff-custom" forcefield; if using a smiles string, use just "gaff".
    # Mixtures can be specified like so
    # "input" = [["PCBM-gaff", "P3HT-16-gaff"]]
    # note the additional brackets
    "input": [
        #["CZTPTZ8FITIC-gaff"],
        #["CZTPTZITIC-gaff"],
        ["PCBM-gaff"],
        #["P3HT-16-gaff"],
        #["ITIC-gaff"],
        #["ITIC-Th-gaff"],
        #["IEICO-gaff"],
        #["IDT-2BR-gaff"],
        #["EH-IDTBR-gaff"],
        #["TruxTP6FITIC-gaff"],
        #["TruxTPITIC-gaff"],
        ],

    # If a mixture is used, the number of each compound in the mixture
    # needs to be specified:
    # "n_compounds" = [[100,100], [1000,500]]
    # Even if not doing a mixture, enter n_compounds as a list or tuple
    # (Example: [[100]])
    # Value for n_compounds must be an integer, not a float.
    # (Example: Use 2 instead of 2.0)
    "n_compounds": [[100]],

    # Density specified as a string, like "value_unit" replacing "/" with "-"
    "density": ["1.0_g-cm**3"],
    # Energy scaling "solvent" parameter
    "e_factor": [1.0],

    # Forcefields are specified as keys to the FORCEFIELD dictionary in
    # planckton/forcefields/__init__.py
    "forcefield": [
        "gaff-custom",
        #"gaff",
        ],

    # Simulation parameters
    # kT, tau, and n_steps must specified as a list of lists of the same length
    # Reduced temperatures specified in simulation units
    "kT": [[1.0]],
    # Thermostat coupling period
    "tau": [[1]],
    # Number of steps to run final simulation
    "n_steps": [[1e7]],

    # Timestep size
    "dt": [0.001],
    # Potential cutoff
    "r_cut": [2.5],
    # Number of steps to shrink the box
    "shrink_steps": [1e3],
    # Reduced temperature at which to shrink the box
    "shrink_kT": [10],
    # Thermostat coupling period at which to shrink the box
    "shrink_tau": [1.0],
    # Whether to remove hydrogen atoms
    "remove_hydrogens": [False],  # True or False
    "mode": ["gpu"]  # "cpu" or "gpu"
}


def get_parameters(parameters):
    return list(parameters.keys()), list(product(*parameters.values()))


def main(parameters):
    project = signac.init_project(project_name)
    param_names, param_combinations = get_parameters(parameters)
    # Create the generate jobs
    for params in param_combinations:
        parent_statepoint = dict(zip(param_names, params))
        parent_job = project.open_job(parent_statepoint)
        parent_job.init()
        parent_job.doc.setdefault("steps", sum(parent_statepoint["n_steps"]))
    project.write_statepoints()
    print(f"Initialized. ({len(param_combinations)} total jobs)")


if __name__ == "__main__":
    main(parameters)
