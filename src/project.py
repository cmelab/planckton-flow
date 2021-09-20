"""Define the project's workflow logic and operation functions.

Execute this script directly from the command line, to view your project's
status, execute operations and submit them to a cluster. See also:

    $ python src/project.py --help
"""
import flow
from flow import FlowProject, directives
from flow.environment import DefaultSlurmEnvironment
from flow.environments.xsede import Bridges2Environment
from os import path


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


class Borah(DefaultSlurmEnvironment):
    hostname_pattern = "borah"
    template = "borah.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="gpu",
            help="Specify the partition to submit to."
        )


class R2(DefaultSlurmEnvironment):
    hostname_pattern = "r2"
    template = "r2.sh"

    @classmethod
    def add_args(cls, parser):
        parser.add_argument(
            "--partition",
            default="gpuq",
            help="Specify the partition to submit to."
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
        parser.add_argument(
            "--nodelist",
            help="Specify the node to submit to."
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
@MyProject.label
def sampled(job):
    return job.doc.get("done")


def get_paths(key, job):
    from planckton.compounds import COMPOUND
    try:
        return COMPOUND[key]
    except KeyError:
        # job.ws will be the path to the job e.g.,
        # path/to/planckton-flow/workspace/jobid
        # this is the planckton root dir e.g.,
        # path/to/planckton-flow
        file_path = path.abspath(path.join(job.ws, "..", "..", key))
        if path.isfile(key):
            print(f"Using {key} for structure")
            return key
        elif path.isfile(file_path):
            print(f"Using {file_path} for structure")
            return file_path
        else:
            print(f"Using {key} for structure--assuming SMILES input")
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
    import glob
    import warnings

    import unyt as u

    from planckton.sim import Simulation
    from planckton.init import Compound, Pack
    from planckton.utils import units
    from planckton.forcefields import FORCEFIELD


    with job:
        inputs = [get_paths(i,job) for i in job.sp.input]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            compound = [Compound(i) for i in inputs]
            packer = Pack(
                compound,
                ff=FORCEFIELD[job.sp.forcefield],
                n_compounds=list(job.sp.n_compounds),
                density=units.string_to_quantity(job.sp.density),
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
            r_cut=job.sp.r_cut,
            dt=job.sp.dt,
            mode=job.sp.mode,
            target_length=target_length,
            restart=restart
        )


        job.doc["done"] = my_sim.run()

        ref_distance = my_sim.ref_values.distance * u.Angstrom
        ref_energy = my_sim.ref_values.energy * u.kcal / u.mol
        ref_mass = my_sim.ref_values.mass * u.amu

        job.doc["T_SI"] = units.quantity_to_string(
            units.kelvin_from_reduced(job.sp.kT_reduced, ref_energy)
            )
        job.doc["real_timestep"] = units.quantity_to_string(
            units.convert_to_real_time(
                job.sp.dt, ref_mass, ref_distance, ref_energy
            ).to("femtosecond")
        )
        job.doc["ref_mass"] = units.quantity_to_string(ref_mass)
        job.doc["ref_distance"] = units.quantity_to_string(ref_distance)
        job.doc["ref_energy"] = units.quantity_to_string(ref_energy)

        outfiles = glob.glob(f"{job.ws}/job*.o")
        if outfiles:
            tps,time = get_tps_time(outfiles)
            job.doc["average_TPS"] = tps
            job.doc["total_time"] = time


def get_tps_time(outfiles):
    import numpy as np

    times = []
    for ofile in outfiles:
        with open(ofile) as f:
            lines = f.readlines()
            try:
                # first value is TPS for shrink, second value is for sim
                tpsline = [l for l in lines if "Average TPS" in l][-1]
                tps = tpsline.strip("Average TPS:").strip()

                t_lines = [l for l in lines if "Time" in l]
                h,m,s = t_lines[-1].split(" ")[1].split(":")
                times.append(int(h)*3600 + int(m)*60 + int(s))
            except IndexError:
                # This will catch outputs from failures or non-hoomd operations
                # (e.g. analysis) in the job dir
                pass
    # total time in seconds
    total_time = np.sum(times)
    hh = total_time // 3600
    mm = (total_time - hh*3600) // 60
    ss = total_time % 60
    return tps, f"{hh:02d}:{mm:02d}:{ss:02d}"


if __name__ == "__main__":
    MyProject().main()
