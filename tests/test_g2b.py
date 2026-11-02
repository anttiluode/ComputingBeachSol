"""G2b checks: material conservation and an actual gradient referee."""
import unittest
import numpy as np
from beach import Beach
from beach.adjoint import loss_and_gradient, propagate
from beach.teacher import adjoint_snapshot, flux_delta, case
from wml.cavity import C, DT, DAMP, KAPPA


class TeacherTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.beach=Beach()

    def test_adjoint_field_product_matches_exact_discrete_gradient(self):
        b=self.beach
        wall=b.kappa_bits(b.initial(31))
        target,_=propagate(b.cav,b.kappa_bits(b.initial(33)),steps=215)
        u,lam,_=adjoint_snapshot(b.cav,wall,target)
        _,g,_=loss_and_gradient(b.cav,wall,target)
        c=-(C*DT)**2*KAPPA/(1+DAMP*DT/2)
        product=c*np.einsum('kij,tij->k',b.counts,u*lam,optimize=True)
        self.assertLess(np.linalg.norm(product-g)/(np.linalg.norm(g)+1e-30),1e-10)
        self.assertGreater(np.linalg.norm(g),1e-12)

    def test_thresholded_flux_cannot_move_with_no_stress(self):
        b=self.beach
        rng=np.random.default_rng(51)
        velocity=rng.normal(0,1e-4,size=(4,96,96))
        delta,_,_,active=flux_delta(b,velocity,0.5)
        self.assertEqual(active,0)
        self.assertTrue(np.array_equal(delta,np.zeros(b.cfg.k)))

    def test_conservation_and_zero_teacher_control(self):
        b=self.beach
        record=case(b,31,threshold_fraction=.5,teacher_ratio=0.)
        self.assertEqual(record['on'],record['off'])
        self.assertIsNone(record['interference']['alignment'])
        self.assertLess(record['mass_conservation_max'],1e-10)
        self.assertLess(record['cross_identity_relative_error'],1e-10)


if __name__=='__main__':
    unittest.main()
