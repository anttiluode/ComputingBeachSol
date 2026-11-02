"""Fast checks for preregistered K/readout and energy-writer extension."""
import unittest
import numpy as np
from beach.model import Beach,Config
from beach.resolution import arrivals,predict
from beach.energy_writer import energy_delta,local_flux,test_case


class Round3Tests(unittest.TestCase):
    def test_arrival_calibration_is_label_free(self):
        self.assertEqual(arrivals(Beach(Config(k=8))),[122,122,122])

    def test_prearrival_no_signal_returns_chance(self):
        z=np.zeros((3,2,100))
        self.assertEqual(predict(z,z,noise_std=0)['accuracy'],.5)

    def test_conservative_flux_total(self):
        x=np.array([2.,-3.,5.,1.,4.,0.,-1.,3.])
        self.assertAlmostEqual(float(local_flux(x).sum()),0.,places=13)

    def test_energy_contrast_equals_forward_adjoint_product(self):
        rng=np.random.default_rng(12);b=Beach()
        u=rng.normal(size=(4,96,96));lam=rng.normal(size=u.shape)
        gain=.17
        delta,_=energy_delta(b,u,lam,gain,0)
        direct=np.einsum('kij,tij->k',b.counts,u*lam,optimize=True)
        self.assertLess(np.linalg.norm(delta-direct),1e-10)

    def test_projected_energy_writer_gradient_and_mass(self):
        r=test_case(Beach(),31,ratio=.02,threshold_fraction=0,steps=190)
        self.assertGreater(r['projected']['cosine'],.999)
        self.assertLess(abs(r['mass_change_projected']),1e-11)
        self.assertLess(abs(r['mass_change_conservative']),1e-11)


if __name__=='__main__':
    unittest.main()
