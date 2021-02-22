"""Define the project's workflow logic and operation functions.

Execute this script directly from the command line, to view your project's
status, execute operations and submit them to a cluster. See also:

    $ python src/project.py --help
"""
import flow
from flow import FlowProject, directives
from flow.environment import DefaultSlurmEnvironment
from flow.environments.xsede import BridgesEnvironment, CometEnvironment, Bridges2Environment


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


class Bridges2Custom(Bridges2Environment):
    template = "bridges2custom.sh"

    @classmethod
    def add_args(cls, parser):
        super(Bridges2Environment, cls).add_args(parser)
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
    hostname_pattern = "fry.boisestate.edu"
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


def get_paths(key):
    from planckton.compounds import COMPOUND_FILE
    try:
        return COMPOUND_FILE[key]
    except KeyError:
        return key

def on_container(func):
        return flow.directives(
                executable='singularity exec --nv $PLANCKTON_SIMG python'
                )(func)


@on_container
@directives(ngpu=1)
@MyProject.operation
@MyProject.post(sampled)
def sample(job):
    import warnings

    import unyt as u

    from planckton.sim import Simulation
    from planckton.init import Compound, Pack
    from planckton.utils import units
    from planckton.force_fields import FORCE_FIELD


    with job:
        inputs = [get_paths(i) for i in job.sp.input]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            compound = [Compound(i) for i in inputs]
            packer = Pack(
                compound,
                ff=FORCE_FIELD[job.sp.forcefield],
                n_compounds=job.sp.n_compounds,
                density=units.tuple_to_quantity(job.sp.density),
                remove_hydrogen_atoms=job.sp.remove_hydrogens,
            )

            system = packer.pack()
        print(f"Target length should be {packer.L:0.3f}")

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


        my_sim.run()

        ref_distance = my_sim.ref_values.distance * u.Angstrom
        ref_energy = my_sim.ref_values.energy * u.kcal / u.mol
        ref_mass = my_sim.ref_values.mass * u.amu

        job.doc["T_SI"] =   units.quantity_to_tuple(
                units.kelvin_from_reduced(job.sp.kT_reduced, ref_energy)
                )
        job.doc["real_timestep"] = units.quantity_to_tuple(
                units.convert_to_real_time(
                    job.sp.dt,
                    ref_mass,
                    ref_distance,
                    ref_energy).to("femtosecond")
                )
        job.doc["ref_mass"] = units.quantity_to_tuple(ref_mass)
        job.doc["ref_distance"] = units.quantity_to_tuple(ref_distance)
        job.doc["ref_energy"] = units.quantity_to_tuple(ref_energy)


if __name__ == "__main__":
    MyProject().main()
