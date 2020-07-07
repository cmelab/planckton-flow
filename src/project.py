"""Define the project's workflow logic and operation functions.

Execute this script directly from the command line, to view your project's
status, execute operations and submit them to a cluster. See also:

    $ python src/project.py --help
"""
from flow import FlowProject, directives
from flow.environment import DefaultSlurmEnvironment
from flow.environments.xsede import BridgesEnvironment, CometEnvironment


class MyProject(FlowProject):
    pass


class BridgesCustom(BridgesEnvironment):
    @classmethod
    def add_args(cls, parser):
        super(BridgesEnvironment, cls).add_args(parser)
        parser.add_argument(
            "--partition",
            default="GPU-shared",
            help="Specify the partition to submit to.",
        )


class CometCustom(CometEnvironment):
    @classmethod
    def add_args(cls, parser):
        super(CometEnvironment, cls).add_args(parser)
        parser.add_argument(
            "--partition",
            default="gpu-shared",
            help="Specify the partition to submit to.",
        )


class Fry(DefaultSlurmEnvironment):
    hostname_pattern = "fry"
    template = "fry.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition", default="batch", help="Specify the partition to submit to."
        )


class Kestrel(DefaultSlurmEnvironment):
    hostname_pattern = "kestrel"
    template = "kestrel.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition", default="batch", help="Specify the partition to submit to."
        )


# Definition of project-related labels (classification)
def current_step(job):
    import gsd.hoomd

    if job.isfile("trajectory.gsd"):
        with gsd.hoomd.open(job.fn("trajectory.gsd")) as traj:
            return traj[-1].configuration.step
    return -1


@MyProject.label
def sampled(job):
    return current_step(job) >= job.doc.steps


@MyProject.label
def initialized(job):
    return job.isfile("init.hoomdxml")


# @directives(executable="python -u")
# @MyProject.operation
# @MyProject.post(initialized)
# def initialize(job):
#   import os
#   import logging
#   from planckton.init import Compound, Pack
#   from planckton.compounds import COMPOUND_FILE
#   from planckton.force_fields import FORCE_FIELD
#
#   with job:
#       if os.path.isfile("init.hoomdxml"):
#           logging.info("File exits, skipping init")
#           return
#       compound = Compound(COMPOUND_FILE[job.sp.molecule])
#       packer = Pack(
#           compound, ff_file=FORCE_FIELD["opv_gaff"], n_compounds=1, density=0.1
#       )
#       packer.pack()


@directives(executable="python -u")
@directives(ngpu=1)
@MyProject.operation
# @MyProject.pre.after(initialize)
@MyProject.post(sampled)
def sample(job):
    from planckton.sim import Simulation
    import os
    import logging
    from planckton.init import Compound, Pack
    from planckton.compounds import COMPOUND_FILE
    from planckton.force_fields import FORCE_FIELD
    from planckton.utils import base_units, unit_conversions

    with job:
        units = base_units.base_units()
        compound = Compound(COMPOUND_FILE[job.sp.molecule])
        packer = Pack(
            compound,
            ff_file=FORCE_FIELD["opv_gaff"],
            n_compounds=job.sp.n_compounds,
            density=job.sp.density,
            remove_hydrogen_atoms=job.sp.remove_hydrogens,
        )

        if not os.path.isfile("init.hoomdxml"):
            logging.info("Creating Init")
            packer.pack()
        logging.info("target length should be", packer.L)
        L = packer.L / units["distance"]

        my_sim = Simulation(
            "init.hoomdxml",
            kT=job.sp.kT_reduced,
            gsd_write=max([int(job.sp.n_steps / 100), 1]),
            log_write=max([int(job.sp.n_steps / 10000), 1]),
            e_factor=job.sp.e_factor,
            n_steps=job.sp.n_steps,
            tau=job.sp.tau,
            dt=job.sp.dt,
            mode="gpu",
            target_length=L,
        )

        for key, pair in units.items():
            job.doc[key] = pair
        job.doc["T_SI"] = unit_conversions.kelvin_from_reduced(job.sp.kT_reduced)
        job.doc["T_unit"] = "K"
        job.doc["real_timestep"] = unit_conversions.convert_to_real_time(job.sp.dt)
        job.doc["time_unit"] = "fs"

        my_sim.run()


if __name__ == "__main__":
    MyProject().main()
