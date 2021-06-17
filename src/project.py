"""Define the project's workflow logic and operation functions.

Execute this script directly from the command line, to view your project's
status, execute operations and submit them to a cluster. See also:

    $ python src/project.py --help
"""
import flow
from flow import FlowProject, directives
from flow.environment import DefaultSlurmEnvironment
from flow.environments.xsede import Bridges2Environment, CometEnvironment

class MyProject(FlowProject):
    pass


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
    from planckton.compounds import COMPOUND
    try:
        return COMPOUND[key]
    except KeyError:
        return key

def on_container(func):
        return flow.directives(
                executable='singularity exec --nv $PLANCKTON_SIMG python'
                )(func)



@MyProject.label
def rdfed(job):
    return job.isfile("rdf.txt")


def on_pflow(func):
    return flow.directives(
            executable='/jet/home/whiteg/.conda/envs/planckton-flow/bin/python')(func)


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
    from planckton.forcefields import FORCEFIELD


    with job:
        inputs = [get_paths(i) for i in job.sp.input]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            compound = [Compound(i) for i in inputs]
            packer = Pack(
                compound,
                ff=FORCEFIELD[job.sp.forcefield],
                n_compounds=job.sp.n_compounds,
                density=units.tuple_to_quantity(job.sp.density),
                remove_hydrogen_atoms=job.sp.remove_hydrogens,
            )

            system = packer.pack()
        print(f"Target length should be {packer.L:0.3f}")

        if job.isfile("restart.gsd"):
            restart = job.fn("restart.gsd")
            target_length = None
        else:
            restart = None
            target_length = packer.L

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
                target_length=target_length,
                restart=restart
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

@directives(ngpu=1)
@on_pflow
@MyProject.operation
@MyProject.post(rdfed)
@MyProject.pre(sampled)
def post_proc(job):
    from cmeutils.structure import gsd_rdf
    import numpy as np
    import os
    import matplotlib
    import matplotlib.pyplot as plt
    import freud
    import gsd
    import hoomd
    import gsd.pygsd
    import gsd.hoomd
    import signac
    hoomd.context.initialize("")
    gsdfile= job.fn('trajectory.gsd')
    rdf,norm = gsd_rdf(gsdfile,A_name='c', B_name='c', r_min=0.01, r_max=6)
    x = rdf.bin_centers
    y = rdf.rdf*norm
    save_path= os.path.join(job.ws,"rdf.txt")
    np.savetxt(save_path, np.transpose([x,y]), delimiter=',', header= "bin_centers, rdf")
    plt.xlabel("r (A.U.)", fontsize=14)
    plt.ylabel("g(r)", fontsize=14)
    plt.plot(x, y)
    save_plot= os.path.join(job.ws,"rdf.png")
    plt.savefig(save_plot)
if __name__ == "__main__":
    MyProject().main()
