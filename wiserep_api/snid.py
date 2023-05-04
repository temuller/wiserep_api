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
        with open(file, 'r') as f:
            first_line = f.readlines()[0]
            if 'wave' not in first_line or 'flux' not in first_line:
                # this is not a spectrum
                continue
            
        sn_df = pd.read_csv(file)
        snid_df = sn_df[["wave", "flux"]]
        outfile = os.path.splitext(file)[0] + ".snid"
        snid_df.to_csv(outfile, header=False, index=False, sep="\t")


def run_snid(directory, command=None, skip_fits=False):
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
    skip_fits: bool, ``False``
        Whether to skip files that were already run with SNID.
    """
    create_snid_inputs(directory)

    if command is None:
        command = "snid inter=0 plot=0 aband=0"

    # get SNID input files
    all_directory_files = glob.glob(os.path.join(directory, "*"))
    snid_files = [file for file in all_directory_files if file.endswith(".snid")]

    for file in snid_files:
        # get output file name
        basename = os.path.basename(file)
        print_file = os.path.splitext(basename)[0]
        snid_output = os.path.join(directory, f"{print_file}_snid.output")
        
        if skip_fits is True and os.path.isfile(snid_output) is True:
            # skip this file that was previously fitted with SNID
            continue

        # go to the SN directory, run SNID and come back
        os.chdir(directory)
        os.system(f"{command} {basename}")
        os.chdir("../..")

        # remove temporary files
        os.remove(file) 
        snid_param_file = os.path.join(directory, "snid.param")
        os.remove(snid_param_file)
        
        # check SNID output file
        if os.path.isfile(snid_output) is False:
            print(f"\nNo SNID output found for {print_file}! Probably a failed fit...")
            
            continue

        # get SNID output and "clean" it
        with open(snid_output) as f:
            skiprows = 0
            for i, line in enumerate(f.readlines()):
                if line.startswith("#no. sn type"):
                    break
                skiprows += 1

        # save new output
        output_df = pd.read_csv(snid_output, skiprows=skiprows, delim_whitespace=True)
        output_df = output_df[output_df.grade == "good"]  # keep only the good fits
        output_df.to_csv(snid_output, index=False)
