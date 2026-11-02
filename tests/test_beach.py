import unittest
import numpy as np
from beach import Beach
from beach.tour import pair_tour, pair_interaction


class BeachTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.beach = Beach()

    def test_exact_upstream_frozen_solver(self):
        b = self.beach; h = b.initial(12)
        expected = b.cav.run(b.kappa_bits(h), source=1, steps=140)[0,:,0]
        end, log = b.event(h, source=1, drive=1, steps=140,
                           write=False, record=True)
        self.assertTrue(np.array_equal(end, h))
        self.assertLess(np.max(np.abs(log['trace']-expected)), 3e-14)

    def test_weak_pings_do_not_write_exactly(self):
        b = self.beach
        for seed in (0,4,21):
            h, _ = b.history((0,1), seed)
            for src in range(3):
                after, log = b.event(h, src, drive=b.cfg.read_drive,
                                     steps=b.cfg.read_steps, write=True)
                self.assertTrue(np.array_equal(after, h))
                self.assertEqual(log['active_interfaces'], 0)
                self.assertEqual(log['total_transport'], 0)

    def test_mass_and_passive_coefficients(self):
        b = self.beach; h = b.initial(7)
        after, log = b.event(h, 0)
        self.assertGreater(log['total_transport'], 0)
        self.assertAlmostEqual(after.sum(), h.sum(), places=11)
        self.assertTrue(np.all(b.kappa_bits(after)>0))
        self.assertTrue(np.all(b.kappa_bits(after)<1))

    def test_order_depends_on_feedback_not_residual_waves(self):
        b = self.beach
        for seed in (0,4):
            ab,_=b.history((0,1), seed, feedback=True)
            ba,_=b.history((1,0), seed, feedback=True)
            x,_=b.history((0,1), seed, feedback=False)
            y,_=b.history((1,0), seed, feedback=False)
            self.assertGreater(np.linalg.norm(ab-ba), .04)
            self.assertLess(np.linalg.norm(x-y), 2e-12)

    def test_short_window_limits_pair_interaction(self):
        b = self.beach
        tour = pair_tour(b.cav, 0, 3, source=0)
        interaction = pair_interaction(b, b.initial(6), 0, 3, delta=.12)
        cutoff = max(1, int(np.floor(tour-40)))
        peak = np.max(np.abs(interaction))
        self.assertGreater(peak, 1e-10)
        self.assertLess(np.max(np.abs(interaction[:cutoff])), 1e-3*peak)

if __name__ == '__main__':
    unittest.main()
