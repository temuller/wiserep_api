import os
import pandas as pd
from astropy.io import fits
from wiserep_api.api import get_response, get_object_id


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
        If True, print some of the extra information

    Returns
    -------
    target_class: str
        The target's classification. Returns 'Unknown' if not found.
    """
    if os.path.isdir("spectra") is False:
        os.mkdir("spectra")

    assert file_type in [None, "ascii", "fits"], "not a valide file type"

    # look for the target ID in the search webpage
    obj_id = get_object_id(iau_name, verbose)
    if (obj_id is None) or (obj_id == "Unknown"):
        return obj_id

    # target's webpage
    target_url = f"https://www.wiserep.org/object/{obj_id}"
    response = get_response(target_url)
    if response is None:
        return None

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

    # download ASCII spectra
    if file_type == "ascii" or file_type is None:
        for url in txt_urls:
            # skip files
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
                delim_whitespace=True,
                names=["wave", "flux", "flux_err"],
                comment="#",
                skiprows=skiprows,
            )
            spec_df.to_csv(outfile, index=False)

    # download FITS spectra
    if file_type == "fits" or file_type is None:
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
