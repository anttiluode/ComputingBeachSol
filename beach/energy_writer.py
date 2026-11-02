"""G2c: energy-square contrast matched to the exact Robin-wall derivative.

Contrastive E_plus - E_minus is EXTERNAL subtraction of two exposures; it is
not a physically autonomous signed sediment mechanism. No gradient is used to
construct the candidate updates; the numerical adjoint enters as the ideal
teacher field. Tests keep the original G2b transport as a negative reference.
"""
from __future__ import annotations
import numpy as np
from .model import Beach
from .adjoint import propagate, loss_and_gradient
from .teacher import adjoint_snapshot


def angle(x,y):
    return float(np.dot(x,y)/(np.linalg.norm(x)*np.linalg.norm(y)+1e-30))


def energy_delta(beach, u, lam, boost, cutoff_fraction=0):
    # The writer sees only the SUM of simultaneous field displacements in
    # each exposure. No cross term is computed explicitly by the writer.
    # E+ / E- integral over time & patch cells, not averages across patches.
    pos=np.einsum('kij,tij->k',beach.counts,(u+boost*lam)**2,optimize=True)
    neg=np.einsum('kij,tij->k',beach.counts,(u-boost*lam)**2,optimize=True)
    base=np.einsum('kij,tij->k',beach.counts,u**2,optimize=True)
    cutoff=cutoff_fraction*float(np.median(base))
    pos=np.maximum(pos-cutoff,0.)
    neg=np.maximum(neg-cutoff,0.)
    return (pos-neg)/(4*boost),base


def local_flux(delta):
    # Conserves total height. Flux goes DOWN the cross-energy gradient.
    # Divergence on cyclic wall patches = Lap(E); may oppose a gradient step.
    q=np.asarray(delta)-np.roll(delta,-1)
    return np.roll(q,1)-q


def test_case(beach,seed,ratio=.02,threshold_fraction=0,steps=310,step_norm=.025):
    h=beach.initial(seed);b=beach.kappa_bits(h)
    rng=np.random.default_rng(seed)
    target_h=h+rng.normal(0,.21,size=beach.cfg.k)
    target_h-=target_h.mean()-h.mean()
    source=seed%3
    target,_=propagate(beach.cav,beach.kappa_bits(target_h),source=source,steps=steps)
    u,lam,_=adjoint_snapshot(beach.cav,b,target,source=source)
    loss,gb,_=loss_and_gradient(beach.cav,b,target,source=source)
    gh=gb/np.cosh(h/.45)**2
    ideal=-gh+gh.mean()
    # Same transparent external calibration for every trial (not a material property).
    pu=np.einsum('kij,tij->tk',beach.counts,u,optimize=True)/beach.weights
    pl=np.einsum('kij,tij->tk',beach.counts,lam,optimize=True)/beach.weights
    boost=ratio*np.sqrt(np.mean(pu**2))/max(np.sqrt(np.mean(pl**2)),1e-30)
    raw,base=energy_delta(beach,u,lam,boost,threshold_fraction)
    minus=np.asarray(raw)-raw.mean()
    downhill=local_flux(raw) # divergence of flux toward lower cross energy
    # A single teacher exposure is a physical intensity, no subtraction.
    # Difference from natural forward-only deposition still needs external baseline.
    plus=np.einsum('kij,tij->k',beach.counts,(u+boost*lam)**2,optimize=True)
    forward_only=-base
    single_plus=-plus
    # Difference of two states isolates the signed interference cross term.
    # A real material must support reversible, signed contrast to implement it.
    def score(d):
        norm=float(np.linalg.norm(d))
        if norm<1e-19:return dict(cosine=None,ratio=None,norm=norm)
        new_h=h+step_norm*d/norm
        out,_=propagate(beach.cav,beach.kappa_bits(new_h),source=source,steps=steps)
        new_loss=.5*np.mean((out-target)**2)
        return dict(cosine=angle(d,ideal),ratio=float(new_loss/max(loss,1e-30)),norm=norm)
    return dict(seed=seed,source=source,teacher_ratio=ratio,boost=float(boost),
                threshold_fraction=threshold_fraction,loss_initial=loss,
                ideal_norm=float(np.linalg.norm(ideal)),
                unconstrained=score(raw),projected=score(minus),
                conservative_downhill=score(downhill),
                forward_only=score(forward_only),single_plus=score(single_plus),
                forward_only_conserved=score(forward_only-forward_only.mean()),
                single_plus_conserved=score(single_plus-single_plus.mean()),
                mass_change_projected=float(np.sum(minus)),
                mass_change_conservative=float(np.sum(downhill)))


def summarize(records):
    out={}
    for branch in ('unconstrained','projected','conservative_downhill','forward_only','single_plus','forward_only_conserved','single_plus_conserved'):
        c=np.array([r[branch]['cosine'] if r[branch]['cosine'] is not None else np.nan for r in records])
        l=np.array([r[branch]['ratio'] if r[branch]['ratio'] is not None else np.nan for r in records])
        out[branch]=dict(mean_cosine=float(np.nanmean(c)),median_cosine=float(np.nanmedian(c)),
                         positive=int((c>0).sum()),lower_loss=int((l<1).sum()),
                         mean_loss_ratio=float(np.nanmean(l)))
    out['median_teacher_boost']=float(np.median([r['boost'] for r in records]))
    out['max_mass_change_conservative']=float(max(abs(r['mass_change_conservative']) for r in records))
    return out


def evaluate(seeds,ratio=.02,thresholds=(0,.25,.5,.75), verbose=True):
    b=Beach()
    rows={}
    for cutoff in thresholds:
        rec=[]
        for seed in seeds:
            rec.append(test_case(b,seed,ratio,cutoff))
        rows[str(cutoff)]={'summary':summarize(rec),'per_seed':rec}
        if verbose:
            print('ENERGY cutoff',cutoff,'projected',rows[str(cutoff)]['summary']['projected'],
                  'conservative',rows[str(cutoff)]['summary']['conservative_downhill'],flush=True)
    return {'test_seeds':list(seeds),'ratio':ratio,'threshold_fractions':list(thresholds),'results':rows}

if __name__=='__main__':
    import argparse,json
    from pathlib import Path
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=('development','confirm'),default='development');p.add_argument('--out',default=None)
    a=p.parse_args()
    ids=range(31,35) if a.phase=='development' else range(900,916)
    result=evaluate(ids)
    path=Path(a.out or 'results/g2c_'+a.phase+'.json');path.parent.mkdir(exist_ok=True,parents=True);path.write_text(json.dumps(result,indent=2)+'\n')
