import unittest
import numpy as np
from wiserep_api import get_target_class 


class TestClassification(unittest.TestCase):
    def test_classification(self):
        sn_type = get_target_class('2004eo')
        np.testing.assert_string_equal(sn_type, 'SN Ia')

if __name__ == "__main__":
    unittest.main()
