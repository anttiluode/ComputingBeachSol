"""Verified discrete adjoint for frozen WML Robin coefficients.

This is a new derivative, NOT a copy of ArborVerb's edge-gain derivative.
The sensitivity field is a computational backward recurrence, not yet a
demonstration that a physical time-reversed teacher wave can implement it.
"""
import numpy as np
from wml.cavity import C, DT, DAMP, KAPPA, SIGMA


def propagate(cav, bits, source=0, steps=190, store_states=False):
    bits = np.asarray(bits, dtype=np.float64)
    robin = KAPPA*np.einsum('k,kij->ij', bits, cav.counts, optimize=True)
    sy, sx = cav.sources[source]
    ins = cav.inside.astype(float)
    u = np.exp(-((cav.x-sx)**2+(cav.y-sy)**2)/(2*SIGMA**2))*ins
    prev = np.zeros_like(u)
    a = 1 + DAMP*DT/2
    b = 1 - DAMP*DT/2
    c2 = (C*DT)**2
    states = [u.copy()] if store_states else None
    out = np.empty(steps)
    for t in range(steps):
        lap = -(cav.neigh+robin)*u
        for ax, sign, nb in cav._nbr:
            lap += np.roll(u, sign, axis=ax)*nb
        nxt = (2*u-b*prev+c2*lap)/a
        nxt *= ins
        prev, u = u, nxt
        out[t] = u[cav.receiver]
        if store_states:
            states.append(u.copy())
    return out, (np.asarray(states) if store_states else None)


def loss_and_gradient(cav, bits, target, source=0):
    """0.5*mean-squared echo loss and exact discrete reverse gradient wrt bits."""
    target = np.asarray(target, dtype=np.float64)
    T = len(target)
    out, states = propagate(cav, bits, source=source, steps=T, store_states=True)
    residual = (out-target)/T
    loss = .5*np.mean((out-target)**2)
    robin = KAPPA*np.einsum('k,kij->ij', np.asarray(bits), cav.counts, optimize=True)
    a = 1+DAMP*DT/2
    b = 1-DAMP*DT/2
    c2 = (C*DT)**2
    adj = np.zeros_like(states)
    g = np.zeros(cav.K, dtype=float)
    cross = np.zeros(cav.K, dtype=float)
    for t in range(T-1, -1, -1):
        adj[t+1][cav.receiver] += residual[t]
        lam = adj[t+1]*cav.inside
        local = np.einsum('kij,ij->k', cav.counts, states[t]*lam, optimize=True)
        cross += local
        g += -(c2*KAPPA/a)*local
        lap = -(cav.neigh+robin)*lam
        for ax, sign, nb in cav._nbr:
            lap += np.roll(lam, sign, axis=ax)*nb
        adj[t] += (2*lam+c2*lap)/a
        if t>0:
            adj[t-1] -= (b/a)*lam
    return float(loss), g, cross


def check_gradient(cav, seed=99, source=0, steps=190, eps=2e-4):
    rng = np.random.default_rng(seed)
    bits = .5+rng.normal(0,.09,size=cav.K)
    target_bits = .5+rng.normal(0,.11,size=cav.K)
    target, _ = propagate(cav, target_bits, source=source, steps=steps)
    J, g, cross = loss_and_gradient(cav, bits, target, source=source)
    fd = np.empty_like(g)
    for k in range(cav.K):
        b0=bits.copy(); b1=bits.copy()
        b0[k]-=eps; b1[k]+=eps
        y0,_=propagate(cav,b0,source=source,steps=steps)
        y1,_=propagate(cav,b1,source=source,steps=steps)
        fd[k] = (.5*np.mean((y1-target)**2) -
                 .5*np.mean((y0-target)**2))/(2*eps)
    relative_l2 = np.linalg.norm(g-fd)/(np.linalg.norm(fd)+1e-30)
    cosine = float(np.dot(g,fd)/(np.linalg.norm(g)*np.linalg.norm(fd)+1e-30))
    factor = -(C*DT)**2*KAPPA/(1+DAMP*DT/2)
    cross_error = np.linalg.norm(g-factor*cross)/(np.linalg.norm(g)+1e-30)
    return {
        'loss': J, 'analytic': g.tolist(), 'finite_difference': fd.tolist(),
        'relative_l2_error': float(relative_l2), 'direction_cosine': cosine,
        'cross_identity_relative_error': float(cross_error),
        'statement': ('The gradient is computed in the discrete model. '
                      'The interference identity is NOT evidence of a physical sediment writer.'),
    }


if __name__ == '__main__':
    from .model import Beach
    import json
    print(json.dumps(check_gradient(Beach().cav), indent=2))
