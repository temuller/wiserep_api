import os
import glob
import json
import numpy as np
import wiserep_api
from wiserep_api.api import get_response

wiserep_api_path = wiserep_api.__path__[0]

spec_types_file = os.path.join(wiserep_api_path, "static", "spectral_types.json")
with open(spec_types_file, "r") as fp:
    spectral_types = json.load(fp)


def print_spectral_types():
    """Prints the spectral types as defined by Wiserep"""
    global spectral_types
    print(spectral_types)


def download_sn_list(spec_type):
    """Downloads a list of all the targets of a given spectral type.

    The spectral types are as defined by Wiserep. To list then,
    you can use ``print_spectral_types()``.

    Parameters
    ----------
    spec_type : int or str
        Spectral type, e.g. ``SN Ia`` or ``3``.
    """
    if os.path.isdir("wiserep") is False:
        os.mkdir("wiserep")

    global spectral_types
    if isinstance(spec_type, str):
        spec_type = spectral_types[spec_type]

    # search url
    url = f"https://www.wiserep.org/search?&page=0&public=all&type[]={spec_type}"

    spec_directory = os.path.join("wiserep", str(spec_type))
    # create any missing directory
    if os.path.isdir(spec_directory) is False:
        os.mkdir(spec_directory)

    # start download
    for i in range(0, 999):
        # change page
        page = f"page{i}"
        if i > 0:
            current_page = url.split("page=")[1].split("&")[0]
            url = url.replace(f"&page={current_page}", f"&page={i}")

        # get page data
        response = get_response(url)
        split_text = response.text.split('Click to Object page">')

        # get names of the SNe
        names = []
        for st in split_text:
            name = st.split("</a")[0]
            # alternative name
            alt_split = st.split('target="_blak">')
            if len(alt_split) < 2:
                alt_name = None
            else:
                alt_name = alt_split[1].split("</a")[0]

            if len(name) > 20:
                continue  # this is just text
            try:
                # this avoids some annoying lines
                # and uses the alternative name if
                # no IAU name is found
                _ = float(name)
                if alt_name is not None:
                    if "," in alt_name:
                        # Some SNe have 2+ alternative names
                        alt_name = alt_name.split(",")[0]
                    names.append(alt_name)
            except:
                if name.startswith("SN "):
                    # IAU name
                    name = name.replace("SN ", "")
                names.append(name)

        if len(names) == 0:
            # no more SNe found
            break

        # save page data
        outfile = os.path.join("wiserep", str(spec_type), page + ".txt")
        np.savetxt(outfile, np.array(names).T, fmt="%s")

    # save full list
    sne_list = []
    files = glob.glob(os.path.join("wiserep", str(spec_type), "*"))
    for file in files:
        sne_page = np.genfromtxt(file, dtype=str, delimiter="\n")
        sne_list = sne_list + list(sne_page)

    spec_type_str = [
        key for key, value in spectral_types.items() if value == spec_type
    ][0]
    np.savetxt(
        f'{spec_type_str.replace(" ", "")}_wiserep.txt', np.array(sne_list).T, fmt="%s"
    )
    print(f'{len(sne_list)} "{spec_type_str}" objects found!')
    print(f"URL used: {url}")
