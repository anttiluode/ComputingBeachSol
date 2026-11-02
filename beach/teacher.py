"""G2b: test if G1's signed threshold transport follows an adjoint teacher wave.

The exact adjoint is calculated numerically; this is a *favorable* ideal
coherent exposure, NOT real sediment or verified physical reverse propagation.
The physical writer is the existing, target-blind signed patch flux.
"""
from __future__ import annotations
import numpy as np
from .model import Beach
from .adjoint import propagate, loss_and_gradient
from wml.cavity import C, DT, DAMP, KAPPA


def adjoint_snapshot(cav, bits, target, source=0):
    """Forward u[t] and precise reverse-time lambda[t+1] wave fields."""
    target = np.asarray(target, dtype=float)
    T = len(target)
    output, states = propagate(cav, bits, source=source, steps=T, store_states=True)
    residual = (output - target)/T
    robin = KAPPA*np.einsum('k,kij->ij', bits, cav.counts, optimize=True)
    a=1+DAMP*DT/2; b=1-DAMP*DT/2; c2=(C*DT)**2
    adj=np.zeros_like(states)
    teacher=np.zeros_like(states[:-1])
    for t in range(T-1,-1,-1):
        adj[t+1,cav.receiver[0],cav.receiver[1]] += residual[t]
        lam=adj[t+1]*cav.inside
        teacher[t]=lam
        lap=-(cav.neigh+robin)*lam
        for axis,sign,nb in cav._nbr:
            lap+=np.roll(lam,sign,axis=axis)*nb
        adj[t]+=(2*lam+c2*lap)/a
        if t>0: adj[t-1]-=(b/a)*lam
    return states[:-1],teacher,output


def flux_delta(beach, wall_velocity, stress_threshold):
    """Same effective G1 law, but a fixed-operator teaching exposure."""
    means=np.einsum('kij,tij->tk',beach.counts,wall_velocity,
                    optimize=True)/beach.weights
    stress=np.roll(means,-1,axis=1)-means
    excess=np.maximum(np.abs(stress)-stress_threshold,0.0)
    q=np.sign(stress)*excess**1.5
    dh=beach.cfg.rate*np.sum(np.roll(q,1,axis=1)-q,axis=0)
    return dh,float(np.mean(np.abs(stress))),float(np.max(np.abs(stress))),int(np.count_nonzero(q))


def cosine(a,b):
    return float(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)+1e-30))


def case(beach,seed,threshold_fraction=.5,teacher_ratio=1.,steps=310,
         phase_sign=1,step_norm=.025):
    """Single predetermined seed, with no gradient used to form material flux."""
    cav=beach.cav
    rng=np.random.default_rng(seed)
    h=beach.initial(seed)
    bits=beach.kappa_bits(h)
    target_h=h+rng.normal(0,.21,size=beach.cfg.k)
    target_h-=target_h.mean()-h.mean()
    target,_=propagate(cav,beach.kappa_bits(target_h),
                       source=seed%3,steps=steps)
    source=seed%3
    u,lam,out=adjoint_snapshot(cav,bits,target,source=source)
    loss,g_bits,_=loss_and_gradient(cav,bits,target,source=source)
    grad_h=g_bits/np.cosh(h/.45)**2
    descent=-grad_h+np.mean(grad_h)
    wall_u=np.einsum('kij,tij->tk',beach.counts,u,
                      optimize=True)/beach.weights
    wall_l=np.einsum('kij,tij->tk',beach.counts,lam,
                      optimize=True)/beach.weights
    u_rms=float(np.sqrt(np.mean(wall_u**2)))
    l_rms=float(np.sqrt(np.mean(wall_l**2)))
    # External amplifier, NOT an autonomous passive property of the beach.
    boost=teacher_ratio*u_rms/max(l_rms,1e-30)
    fwd_vel=(u[1:]-u[:-1])/DT
    teacher_vel=phase_sign*boost*(lam[1:]-lam[:-1])/DT
    threshold=flux_delta(beach,fwd_vel,0)[1]*threshold_fraction
    dh_off,_,_,active_off=flux_delta(beach,fwd_vel,threshold)
    dh_teacher,_,_,active_teacher=flux_delta(beach,teacher_vel,threshold)
    dh_on,_,_,active_on=flux_delta(beach,fwd_vel+teacher_vel,threshold)
    dh_interference=dh_on-dh_off-dh_teacher

    def evaluate(dh):
        norm=float(np.linalg.norm(dh))
        if norm<1e-15:
            return {'alignment':None,'loss_ratio':None,'delta_norm':norm}
        trial=h+(step_norm/norm)*dh
        y,_=propagate(cav,beach.kappa_bits(trial),source=source,steps=steps)
        return {'alignment':cosine(descent,dh),
                'loss_ratio':float((.5*np.mean((y-target)**2))/loss),
                'delta_norm':norm}
    local_cross=np.einsum('kij,tij->k',beach.counts,u*lam,optimize=True)
    gradient_from_cross=-(C*DT)**2*KAPPA/(1+DAMP*DT/2)*local_cross
    cross_error=float(np.linalg.norm(gradient_from_cross-g_bits)/
                      (np.linalg.norm(g_bits)+1e-30))
    return {
        'seed':seed,'source':source,'threshold_fraction':threshold_fraction,
        'teacher_ratio':teacher_ratio,'phase_sign':phase_sign,
        'threshold_absolute':threshold,'forward_wall_rms':u_rms,
        'teacher_boost':float(boost),'loss_initial':loss,
        'gradient_norm':float(np.linalg.norm(descent)),
        'cross_identity_relative_error':cross_error,
        'off':evaluate(dh_off),'on':evaluate(dh_on),
        'teacher_only':evaluate(dh_teacher),
        'interference':evaluate(dh_interference),
        'active':{'off':active_off,'on':active_on,'teacher_only':active_teacher},
        'mass_conservation_max':float(max(abs(np.sum(d)) for d in
               (dh_off,dh_on,dh_teacher,dh_interference))),
    }
