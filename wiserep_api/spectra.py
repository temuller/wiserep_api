import os
import pandas as pd
from io import StringIO
from astropy.io import fits
from wiserep_api.api import get_response, get_target_response


def exclude_include(url, exclude=None, include=None):
    """Either includes or excludes the given URL according to the
    given patterns.

    Note: only one of the parameters ('exclude' or 'include') can be
    given at a time, not both

    Parameters
    ----------
    url : str
        URL string.
    exclude : list, optional
        Patterns to exclude URL.
    include : _type_, optional
        Patterns to include URL.

    Returns
    -------
    skip: bool
        Whether to exclude/include the given URL.
    """
    err_msg = "'exclude' and 'include' cannot be given at the same time!"
    assert exclude is None or include is None, err_msg

    if exclude is not None:
        skip = False
        for pattern in exclude:
            if pattern in url:
                skip = True

    if include is not None:
        skip = True
        for pattern in include:
            if pattern in url:
                skip = False

    if exclude is None and include is None:
        skip = False

    return skip


def download_target_spectra(
    iau_name, file_type=None, exclude=None, include=None, verbose=False
):
    """Downloads the target's spectra from Wiserep.

    Parameters
    ----------
    iau_name: str
        IAU name of the target (e.g. 2020xne).
    file_type: str
        File format: either 'ascii' or 'fits'. By default,
        both formats are downloaded.
    exclude: list, default 'None'
        Files with the given string patterns are excluded.
        Cannot be given together with 'include'.
    include: list, default 'None'
        Files with the given string patterns are inxcluded.
        Cannot be given together with 'exclude'.
    verbose: bool, default 'False'
        If 'True', print some of the extra information.

    Returns
    -------
    target_class: str
        The target's classification. Returns 'Unknown' if not found.
    """
    if os.path.isdir("spectra") is False:
        os.mkdir("spectra")

    assert file_type in [None, "ascii", "fits"], "not a valide file type"

    # target's url
    response = get_target_response(iau_name, verbose)

    # search for spectra URLs
    # ASCII
    txt_urls = []
    split_text = response.text.split("asciifile=https%3A//")
    for st in split_text:
        url = st.split('"')[0]
        if (url not in txt_urls) and ("&amp" not in url) and ("DOCTYPE" not in url):
            txt_urls.append(url)
    if verbose is True:
        print(f"Found {len(txt_urls)} URLs with spectra (ASCII): {txt_urls}")
        
    # FITS
    fits_urls = []
    split_text = response.text.split("https://")
    for st in split_text:
        url = st.split('"')[0]
        if (url not in fits_urls) and (".fits" in url) and ("rel-file" not in url):
            fits_urls.append(url)
    if verbose is True:
        print(f"Found {len(fits_urls)} URLs with spectra (FITS): {fits_urls}")

    # retrieve table with spectra information
    spec_table = pd.read_html(StringIO(response.text), match='Spec. ID')[0]
    if isinstance(spec_table['Spec. ID'], pd.core.frame.DataFrame) is True:
        # from multi-index to the usual dataframe
        spec_table = pd.DataFrame({col[0]:spec_table[col[0]][col[1]].values for col in spec_table.columns})
    
    # download ASCII spectra
    if file_type == "ascii" or file_type is None:
        ascii_files = []
        for url in txt_urls:
            # skip filesspec_df = spec_df[::2]  # every other row is just crap

            skip = exclude_include(url, exclude, include)
            if skip is True:
                if verbose is True:
                    print(f"Skipping {url}")
                continue

            # check url
            response = get_response("http://" + url)
            if response is None:
                print(f"Nothing found in {url}")

            # get spectrum
            basename = os.path.basename(url)
            obj_dir = os.path.join("spectra", iau_name)
            if os.path.isdir(obj_dir) is False:
                os.mkdir(obj_dir)
            outfile = os.path.join(obj_dir, basename)

            with open(outfile, "w") as file:
                file.write(response.text)

            if response.text.startswith("BITPIX") or response.text.startswith("SIMPLE"):
                # file includes header
                for i, line in enumerate(response.text.split("\n")):
                    split_line = line.split()
                    try:
                        _ = float(split_line[0])
                        _ = float(split_line[1])
                        skiprows = i
                        break
                    except:
                        continue
            else:
                skiprows = None
            spec_df = pd.read_csv(
                outfile,
                sep='\s+',
                names=["wave", "flux", "flux_err"],
                comment="#",
                skiprows=skiprows,
            )
            spec_df.to_csv(outfile, index=False)

            ascii_files.append(basename)
        # update table with the extracted files online
        spec_table = spec_table[spec_table['Spectrum ascii File'].isin(ascii_files)]

    # download FITS spectra
    if file_type == "fits" or file_type is None:
        fits_files = []
        for url in fits_urls:
            # skip files
            skip = exclude_include(url, exclude, include)
            if skip is True:
                if verbose is True:
                    print(f"Skipping {url}")
                continue

            # download file
            print(url)
            hdu = fits.open("http://" + url)

            basename = os.path.basename(url)
            obj_dir = os.path.join("spectra", iau_name)
            if os.path.isdir(obj_dir) is False:
                os.mkdir(obj_dir)
            outfile = os.path.join(obj_dir, basename)
            if os.path.isfile(outfile) is True:
                overwrite = True
            else:
                overwrite = False

            hdu.writeto(outfile, overwrite=overwrite, output_verify="ignore")

            fits_files.append(basename)
        # The fits files are not always available, so only update the table
        # according to these if the ascii files were not downloaded
        if 'ascii_files' not in locals():
            spec_table = spec_table[spec_table['Spectrum fits File'].isin(fits_files)]

    # save spectra information
    # if 'obj_dir' variable is not defined, it means that no spectrum was
    # downloaded
    if 'obj_dir' in locals():
        spec_file = os.path.join(obj_dir, 'downloaded_spectra_info.csv') 
        # remove crap | sort_index is to avoid warning
        spec_table = spec_table.drop(columns=['Select'], axis=1) 
        spec_table.to_csv(spec_file, index=False)
