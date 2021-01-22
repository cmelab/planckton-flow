#!/usr/bin/env python
"""Initialize the project's data space.

Iterates over all defined state points and initializes
the associated job workspace directories."""
import logging
from collections import OrderedDict
from itertools import product

import signac

from planckton.utils import units


def get_parameters():

    parameters = OrderedDict()
    # Parameters used for generating the morphology
    parameters["molecule"] = [
        #"CZTPTZ8FITIC",
        #"CZTPTZITIC",
        "PCBM",
        #"P3HT_16",
        #"ITIC",
        #"ITIC-Th",
        #"IEICO",
        #"IDT-2BR",
        #"EH-IDTBR",
        #"TruxTP6FITIC",
        #"TruxTPITIC",
    ]
    parameters["n_compounds"] = [100, 1000]
    parameters["density"] = [(1.0, "g/cm**3")]
    parameters["e_factor"] = [0.5]

    # Reduced temperatures can be specified by converting from SI:
    # Assuming sulfur from opv gaff
    #ref_energy = 1.046 #* u.kJ / u.mol
    #parameters["kT_reduced"] = []
    #for T_SI in [275,300]: #[275 * u.Kelvin, 300 * u.Kelvin]:
    #    parameters["kT_reduced"].append(
    #            units.reduced_from_kelvin(T_SI, ref_energy)
    #            )
    # or manually:
    parameters["kT_reduced"] = [0.5, 0.75, 1.0]

    # Simulation parameters
    parameters["tau"] = [3]
    parameters["n_steps"] = [1e8]
    parameters["dt"] = [0.0001]
    parameters["remove_hydrogens"] = [False]  # True or False
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
    logging.basicConfig(level=logging.INFO)
    main()
