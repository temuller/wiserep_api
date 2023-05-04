import unittest
import numpy as np
from wiserep_api import get_target_property, get_target_class


class TestProperties(unittest.TestCase):
    def test_properties(self):
        target = '2004eo'
        properties_dict = {'type':'SN Ia',
                           'redshift':'0.015718',
                           'host':'NGC6928',
                           'coords':'20:32:54.190 +09:55:42.71',
                           'coords_deg':'308.22579 +9.92853',
                          } 
        for prop, value in properties_dict.items():
            result = get_target_property(target, prop)
            np.testing.assert_string_equal(str(result), value)

class TestClassification(unittest.TestCase):
    def test_classification(self):
        sn_type = get_target_class("2004eo")
        np.testing.assert_string_equal(sn_type, "SN Ia")


if __name__ == "__main__":
    unittest.main()
