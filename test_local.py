from collections import OrderedDict

import signac

from src import init, project


test_params = {
    "input": [["PCBM-gaff", "P3HT-16-gaff"]],
    "n_compounds": [[5,5]],
    "density": ["1.0_g-cm**3"],
    "e_factor": [0.5],
    "forcefield": ["gaff-custom"],
    "kT_reduced": [0.5],
    "tau": [1],
    "shrink_steps": [1e3],
    "n_steps": [1e3],
    "dt": [0.0001],
    "remove_hydrogens": [False],
    "mode": ["cpu"]
}


def test():
    init.main(test_params)
    workspace = signac.get_project()
    for job in workspace:
        project.sample(job)


if __name__ == "__main__":
    test()
