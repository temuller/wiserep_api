import os
import glob
import shutil
import unittest
import numpy as np
import warnings
from astropy.utils.exceptions import AstropyWarning
from wiserep_api import download_target_spectra

if os.path.isdir('spectra') is True:
    shutil.rmtree('spectra')

class TestDownloadSpectra(unittest.TestCase):
    def test_download_spectra(self):
        target = "ASASSN-14jg"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", AstropyWarning)
            download_target_spectra(target)
        files = glob.glob(os.path.join("spectra", target, "*"))

        txt_files = [file for file in files if ".fits" not in file]
        err_msg = "Number of files does not match (ASCII)"
        np.testing.assert_equal(len(txt_files), 5, err_msg)

        fits_files = [file for file in files if ".fits" in file]
        err_msg = "Number of files does not match (FITS)"
        np.testing.assert_equal(len(fits_files), 3, err_msg)

    def test_exclude(self):
        target = "2017ixi"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", AstropyWarning)
            download_target_spectra(target, exclude=["PESSTO"])
        files = glob.glob(os.path.join("spectra", target, "*"))

        txt_files = [file for file in files if ".fits" not in file]
        err_msg = "There should be no files downloaded (ASCII)"
        np.testing.assert_equal(len(txt_files), 0, err_msg)

        fits_files = [file for file in files if ".fits" in file]
        err_msg = "There should be no files downloaded (FITS)"
        np.testing.assert_equal(len(fits_files), 0, err_msg)

    def test_include(self):
        target = "ASASSN-14hr"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", AstropyWarning)
            download_target_spectra(target, include=["WiFeS"])
        files = glob.glob(os.path.join("spectra", target, "*"))

        txt_files = [file for file in files if ".fits" not in file]
        err_msg = "Number of files does not match (ASCII)"
        np.testing.assert_equal(len(txt_files), 2, err_msg)

        fits_files = [file for file in files if ".fits" in file]
        err_msg = "Number of files does not match (FITS)"
        np.testing.assert_equal(len(fits_files), 2, err_msg)


if __name__ == "__main__":
    unittest.main()
