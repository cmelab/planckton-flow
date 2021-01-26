#!/usr/bin/env python
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories."""
from collections import OrderedDict
from itertools import product
import warnings

import signac

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from planckton.compounds import COMPOUND_FILE
from planckton.utils import units


def get_parameters():
    # Parameters used for generating the morphology
    parameters = OrderedDict()

    # input can be the path to a molecule file or a SMILES string
    # COMPOUND_FILE is a dictionary of paths
    # Mixtures can be specified like so
    # parameters["input"] = [[COMPOUND_FILE["PCBM"],COMPOUND_FILE["P3HT_16"]]]
    # note the additional brackets
    parameters["input"] = [
        #[COMPOUND_FILE["CZTPTZ8FITIC"]],
        #[COMPOUND_FILE["CZTPTZITIC"]],
        [COMPOUND_FILE["PCBM"]],
        #[COMPOUND_FILE["P3HT_16"]],
        #[COMPOUND_FILE["ITIC"]],
        #[COMPOUND_FILE["ITIC-Th"]],
        #[COMPOUND_FILE["IEICO"]],
        #[COMPOUND_FILE["IDT-2BR"]],
        #[COMPOUND_FILE["EH-IDTBR"]],
        #[COMPOUND_FILE["TruxTP6FITIC"]],
        #[COMPOUND_FILE["TruxTPITIC"]],
    ]

    # If a mixture is used, the number of each compound in the mixture
    # needs to be specified:
    # parameters["n_compounds"] = [(100,100), (1000,500)]
    parameters["n_compounds"] = [500, 100]

    # Density must be specified as a pair containing (value, unit)
    parameters["density"] = [(1.0, "g/cm**3")]
    # Energy scaling "solvent" parameter
    parameters["e_factor"] = [0.5]

    # Force fields are specified as keys to the FORCE_FIELD dictionary in
    # planckton/force_fields/__init__.py
    parameters["forcefield"] = ["opv_gaff"]

    # Reduced temperatures specified in simulation units
    parameters["kT_reduced"] = [0.5, 0.75, 1.0]

    # Simulation parameters
    # Thermostat coupling
    parameters["tau"] = [3]
    # Number of steps to shrink the box
    parameters["shrink_steps"] = [1e3]
    # Number of steps to run final simulation
    parameters["n_steps"] = [1e3]
    # Timestep size
    parameters["dt"] = [0.0001]
    # Whether to remove hydrogen atoms
    parameters["remove_hydrogens"] = [False]  # True or False
    parameters["mode"] = ["cpu"]  # "cpu" or "gpu"
    return list(parameters.keys()), list(product(*parameters.values()))


def main():
    project = signac.init_project("debug")
    param_names, param_combinations = get_parameters()
    # Create the generate jobs
    for params in param_combinations:
        parent_statepoint = dict(zip(param_names, params))
        parent_job = project.open_job(parent_statepoint)
        parent_job.init()
        parent_job.doc.setdefault("steps", parent_statepoint["n_steps"])
    project.write_statepoints()


if __name__ == "__main__":
    main()
