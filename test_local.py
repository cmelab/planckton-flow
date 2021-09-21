from collections import OrderedDict

import signac

from src import init, project


test_params = {
    "input": [("PCBM-gaff", "P3HT-16-gaff")],
    "n_compounds": [(2,2)],
    "density": ["0.1_g-cm**3"],
    "e_factor": [0.5],
    "forcefield": ["gaff-custom"],
    "kT": [[0.5]],
    "n_steps": [[1e3]],
    "tau": [[1]],
    "r_cut":[2.5],
    "shrink_steps": [1e3],
    "shrink_kT": [10],
    "shrink_tau": [1.0],
    "dt": [0.001],
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
