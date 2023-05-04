import os
import glob
import pandas as pd


def create_snid_inputs(directory):
    """Creates input files with the spectra for SNID.

    Parameters
    ----------
    directory : str
        Target's directory, e.g. ``spectra/2004eo``.
    """
    # get every single file for this SN
    all_directory_files = glob.glob(os.path.join(directory, "*"))

    # get only the text files, excluding SNID outputs from previous runs
    sn_files = [
        file
        for file in all_directory_files
        if file.endswith(".fits") is False
        and "snid" not in file
        and "output" not in file
    ]

    # create a new file in the format that SNID likes
    for file in sn_files:
        sn_df = pd.read_csv(file)
        snid_df = sn_df[["wave", "flux"]]
        outfile = os.path.splitext(file)[0] + ".snid"
        snid_df.to_csv(outfile, header=False, index=False, sep="\t")


def run_snid(directory, command=None):
    """Runs SNID on the given directory.

    SNID is run on all the files with spectra in the given directory.
    For more information, check the SNID website:
    https://people.lam.fr/blondin.stephane/software/snid/howto.html

    Parameters
    ----------
    directory : str
        Target's directory, e.g. ``spectra/2004eo``.
    command : str, optional
        SNID command. By default, ``snid inter=0 plot=0 aband=0`` is used.
    """
    create_snid_inputs(directory)

    if command is None:
        command = "snid inter=0 plot=0 aband=0"

    # get SNID input files
    all_directory_files = glob.glob(os.path.join(directory, "*"))
    snid_files = [file for file in all_directory_files if file.endswith(".snid")]

    for file in snid_files:
        # go to the SN directory, run SNID and come back
        basename = os.path.basename(file)
        os.chdir(directory)
        os.system(f"{command} {basename}")
        os.chdir("../..")

        # get SNID output file
        print_file = os.path.splitext(basename)[0]
        snid_output = os.path.join(directory, f"{print_file}_snid.output")
        if os.path.isfile(snid_output) is False:
            print(f"No SNID output found for {print_file}! Probably a failed fit...")
            continue

        with open(snid_output) as f:
            skiprows = 0
            for i, line in enumerate(f.readlines()):
                if line.startswith("#no. sn type"):
                    break
                skiprows += 1

        output_df = pd.read_csv(snid_output, skiprows=skiprows, delim_whitespace=True)
        output_df = output_df[output_df.grade == "good"]  # keep only the good fits
        # outfile = os.path.join(directory, f'output_{basename.split(".")[0]}.txt')
        output_df.to_csv(snid_output, index=False)

        # clean directory:
        os.remove(file)
        snid_param_file = os.path.join(directory, "snid.param")
        os.remove(snid_param_file)
