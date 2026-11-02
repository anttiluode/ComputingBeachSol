"""G8 edge-relay tests; no preregistered held-out material seeds."""
import unittest
import numpy as np
from beach.g8_edge import edge_relay, divergence
from beach.g7_local import relay


class EdgeGaugeTests(unittest.TestCase):
    def test_edge_update_matches_potential_at_every_round(self):
        rng=np.random.default_rng(14)
        for k in (8,48):
            r=rng.normal(size=k)+20.
            for rounds in (0,1,4,16,64,1024):
                dz,z=relay(r,rounds)
                de,q,_=edge_relay(r,rounds)
                np.testing.assert_allclose(de,dz,rtol=1e-9,atol=1e-9)
                np.testing.assert_allclose(q,z-np.roll(z,-1),rtol=1e-9,atol=1e-9)
                self.assertLess(abs(de.sum()),1e-10)

    def test_edge_state_does_not_store_zero_mode(self):
        r=np.full(48,80.)
        d,q,_=edge_relay(r,1024)
        np.testing.assert_array_equal(d,np.zeros(48))
        np.testing.assert_array_equal(q,np.zeros(48))
        dz,z=relay(r,1024)
        self.assertGreater(z.mean(),100.)
        np.testing.assert_allclose(dz,np.zeros(48),atol=1e-8)

    def test_clips_remain_conservative_and_enforced(self):
        r=np.linspace(-1,1,48)
        cap=.2
        d,q,info=edge_relay(r,100,cap=cap)
        self.assertGreater(info['clips'],0)
        self.assertLessEqual(float(np.max(np.abs(q))),cap+1e-12)
        self.assertLess(abs(d.sum()),1e-12)

    def test_analytical_spectral_bound(self):
        rng=np.random.default_rng(19)
        for k in (8,48):
            r=rng.normal(size=k)
            _,q,_=edge_relay(r,4096)
            bound=1/(2*np.sin(np.pi/k))
            self.assertLessEqual(np.linalg.norm(q)/np.linalg.norm(r),bound+1e-8)


if __name__=="__main__":
    unittest.main()
