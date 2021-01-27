from collections import OrderedDict

import signac
from planckton.compounds import COMPOUND_FILE

from src import init, project


test_params = OrderedDict({
    "input": [[COMPOUND_FILE["PCBM"]]],
    "n_compounds": [5],
    "density": [(1.0, "g/cm**3")],
    "e_factor": [0.5],
    "forcefield": ["opv_gaff"],
    "kT_reduced": [0.5],
    "tau": [3],
    "shrink_steps": [1e3],
    "n_steps": [1e3],
    "dt": [0.0001],
    "remove_hydrogens": [False],
    "mode": ["cpu"]
})


def test():
    init.main(test_params)
    workspace = signac.get_project()
    for job in workspace:
        pass
    project.sample(job)


if __name__ == "__main__":
    test()
