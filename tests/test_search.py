import os
import unittest
from wiserep_api import print_spectral_types, download_sn_list

if os.path.isfile("SNIa-CSM_wiserep.txt") is True:
    os.remove("SNIa-CSM_wiserep.txt")

class TestSearch(unittest.TestCase):
    def test_search(self):
        print_spectral_types()
        download_sn_list("SN Ia-CSM")

        assert os.path.isfile(
            "SNIa-CSM_wiserep.txt"
        ), "The downloaded list was not found"

if __name__ == "__main__":
    unittest.main()
