"""G6 mechanism unit tests; confirmatory seeds are never touched here."""
import unittest
import numpy as np

from beach.g6_memory import patch_energy, remember, project, single_case
from beach.energy_writer import local_flux
from beach.model import Beach


class G6MechanismTests(unittest.TestCase):
    def test_ewma_is_a_distinct_fading_memory(self):
        e = np.array([1., 4., 9.])
        theta = remember(np.zeros_like(e), e, episodes=12, alpha=.65)
        np.testing.assert_allclose(theta, e*(1-.35**12), rtol=1e-12, atol=1e-12)
        np.testing.assert_allclose(remember(theta, e, 4),
                                   e + (theta-e)*.35**4, atol=1e-12)
        np.testing.assert_array_equal(e, np.array([1.,4.,9.]))

    def test_one_exposure_leaves_signed_cross_term_after_calibration(self):
        rng = np.random.default_rng(22)
        beach = Beach()
        u = rng.normal(size=(3,96,96))
        lam = rng.normal(size=u.shape)
        b = .03
        theta = patch_energy(beach,u)
        observed = patch_energy(beach,u+b*lam) - theta
        predicted = 2*b*np.einsum("kij,tij->k", beach.counts,u*lam,
                                  optimize=True) + b*b*patch_energy(beach,lam)
        np.testing.assert_allclose(observed,predicted,rtol=1e-9,atol=1e-10)

    def test_local_flux_and_global_projection_are_distinct_but_conserve(self):
        raw = np.array([0.,4.,1.,-5.,9.,2.,-1.,7.])
        self.assertAlmostEqual(project(raw).sum(), 0., places=12)
        self.assertAlmostEqual(local_flux(raw).sum(), 0., places=12)
        self.assertGreater(np.linalg.norm(project(raw)-local_flux(raw)), 1.)

    def test_small_development_case_is_finite(self):
        r = single_case(Beach(), 41, steps=190)
        self.assertLess(r["cross_identity_error"], 1e-8)
        self.assertLess(r["max_mass_error"], 1e-10)
        self.assertTrue(np.isfinite(r["results"]["adaptive"]["loss_ratio"]))
        self.assertLess(r["drift"]["4"]["relative_baseline_error"], .05)


if __name__ == "__main__":
    unittest.main()
