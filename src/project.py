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
            "--partition",
            default="batch",
            help="Specify the partition to submit to."
        )


class Kestrel(DefaultSlurmEnvironment):
    hostname_pattern = "kestrel"
    template = "kestrel.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="batch",
            help="Specify the partition to submit to."
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


@directives(executable="python -u")
@directives(ngpu=1)
@MyProject.operation
@MyProject.post(sampled)
def sample(job):
    import os
    import logging
    from planckton.sim import Simulation
    from planckton.init import Compound, Pack
    from planckton.utils import units
    from planckton.force_fields import FORCE_FIELD

    with job:
        compound = [Compound(i) for i in job.sp.input]
        packer = Pack(
            compound,
            ff=FORCE_FIELD[job.sp.forcefield],
            n_compounds=job.sp.n_compounds,
            density=units.tuple_to_quantity(job.sp.density),
            remove_hydrogen_atoms=job.sp.remove_hydrogens,
        )

        system = packer.pack()
        logging.info("Target length should be ", packer.L)

        my_sim = Simulation(
                system,
                kT=job.sp.kT_reduced,
                gsd_write=max([int(job.sp.n_steps / 100), 1]),
                log_write=max([int(job.sp.n_steps / 10000), 1]),
                e_factor=job.sp.e_factor,
                n_steps=job.sp.n_steps,
                shrink_steps=job.sp.shrink_steps,
                tau=job.sp.tau,
                dt=job.sp.dt,
                mode=job.sp.mode,
                target_length=packer.L,
        )

        # TODO need to add ref values to job doc
        #job.doc["T_SI"] = units.kelvin_from_reduced(job.sp.kT_reduced)
        #job.doc["real_timestep"] = units.convert_to_real_time(job.sp.dt)

        my_sim.run()


if __name__ == "__main__":
    MyProject().main()
