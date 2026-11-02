"""G7 mechanism checks, with no confirmatory-seed access."""
import unittest
import numpy as np
from beach.g7_local import lap, relay, harmonic_probe


class LocalRelayTests(unittest.TestCase):
    def test_zero_rounds_are_no_op(self):
        d, potential = relay(np.array([1.,2.,-1.,3.,4.,0.,-2.,1.]),0)
        np.testing.assert_array_equal(d,0.)
        np.testing.assert_array_equal(potential,0.)

    def test_local_flux_divergence(self):
        r=np.array([5.,2.,-4.,0.,1.,-3.,3.,9.])
        d,z=relay(r,128)
        np.testing.assert_allclose(d,-(
            np.roll(z,1)+np.roll(z,-1)-2*z),atol=1e-10)
        self.assertLess(abs(d.sum()),1e-11)
        np.testing.assert_allclose(d,r-r.mean(),rtol=1e-3,atol=1e-3)

    def test_cost_increases_with_ring_size(self):
        p8=harmonic_probe(8,64)
        p48=harmonic_probe(48,64)
        self.assertGreater(p8["fraction_of_ideal"],.99)
        self.assertLess(p48["fraction_of_ideal"],.30)
        self.assertGreater(p48["relative_error"],p8["relative_error"])


if __name__=="__main__":
    unittest.main()
