import unittest
import numpy as np
from beach import Beach
from beach.adjoint import propagate, check_gradient


class AdjointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cav = Beach().cav

    def test_forward_is_identical_to_upstream(self):
        bits = np.array([.2,.6,.3,.1,.7,.5,.4,.8])
        expected = self.cav.run(bits, source=2, steps=190)[0,:,0]
        actual, _ = propagate(self.cav, bits, source=2, steps=190)
        self.assertLess(np.max(np.abs(expected-actual)), 1e-13)

    def test_discrete_adjoint_matches_finite_difference(self):
        for src in (0,1,2):
            result = check_gradient(self.cav, seed=99+src, source=src, steps=190)
            self.assertLess(result['relative_l2_error'], 1e-5)
            self.assertGreater(result['direction_cosine'], .999999)
            self.assertLess(result['cross_identity_relative_error'], 1e-12)

if __name__ == '__main__':
    unittest.main()
