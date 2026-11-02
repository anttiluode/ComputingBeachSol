"""Reproduce G2b's locked teacher-wave/signed-transport comparison.

Protocol: PREREG_G2B.md. All seeds are paired: same target and material
for forward-only, teacher-alone, phase-reversed, and every threshold.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from .model import Beach
from .teacher import case

FRACTIONS=(0.,.25,.5,1.,2.)


def summarize(cases):
    def col(branch,key):
        return np.array([x[branch][key] if x[branch][key] is not None
                         else np.nan for x in cases],dtype=float)
    out={}
    for branch in ('on','off','teacher_only','interference'):
        align=col(branch,'alignment')
        ratio=col(branch,'loss_ratio')
        out[branch]={
            'mean_alignment':float(np.nanmean(align)) if np.any(np.isfinite(align)) else None,
            'median_alignment':float(np.nanmedian(align)) if np.any(np.isfinite(align)) else None,
            'count_positive_alignment':int(np.sum(align>0)),
            'count_improved_loss':int(np.sum(ratio<1)),
            'mean_loss_ratio':float(np.nanmean(ratio)) if np.any(np.isfinite(ratio)) else None,
            'count_nonzero':int(np.sum(np.isfinite(align))),
        }
    out['on_beats_off_count']=int(sum(
        x['on']['loss_ratio'] is not None and x['off']['loss_ratio'] is not None
        and x['on']['loss_ratio']<x['off']['loss_ratio'] for x in cases))
    out['largest_mass_error']=float(max(x['mass_conservation_max'] for x in cases))
    out['largest_cross_identity_error']=float(
        max(x['cross_identity_relative_error'] for x in cases))
    out['teacher_boost_median']=float(np.median(
        [x['teacher_boost'] for x in cases]))
    return out


def run(start=800,count=16):
    beach=Beach()
    primary=[]
    reverse=[]
    zero=[]
    curve={str(frac):[] for frac in FRACTIONS}
    for seed in range(start,start+count):
        for frac in FRACTIONS:
            c=case(beach,seed,threshold_fraction=frac,teacher_ratio=1.,
                   phase_sign=1,steps=310,step_norm=.025)
            curve[str(frac)].append(c)
            if frac==.5: primary.append(c)
        reverse.append(case(beach,seed,threshold_fraction=.5,
                            teacher_ratio=1.,phase_sign=-1,steps=310,
                            step_norm=.025))
        zero.append(case(beach,seed,threshold_fraction=.5,
                         teacher_ratio=0.,phase_sign=1,steps=310,
                         step_norm=.025))
        print('seed',seed,'complete',flush=True)
    prim=summarize(primary)
    rev=summarize(reverse)
    zer=summarize(zero)
    reverse_cross=rev['interference']['mean_alignment']
    primary_cross=prim['interference']['mean_alignment']
    gates={
        'P1_teacher_on_cosine_positive_count':prim['on']['count_positive_alignment']>=12,
        'P2_mean_teacher_on_cosine':prim['on']['mean_alignment']>=.5,
        'P2_teacher_on_loss_improvements':prim['on']['count_improved_loss']>=12,
        'P3_teacher_beats_forward_only_count':prim['on_beats_off_count']>=12,
        'P4_interference_mean_cosine':primary_cross>=.3,
        'P4_interference_exceeds_reversed_by_0p2':
            (primary_cross-reverse_cross)>=.2,
        'P5_mass_conserved':prim['largest_mass_error']<=1e-10,
        'P5_gradient_cross_identity':
            prim['largest_cross_identity_error']<=1e-10,
        'zero_teacher_matches_off':all(
            z['off']==z['on'] and z['interference']['alignment'] is None
            for z in zero),
    }
    result={
        'protocol':'PREREG_G2B.md',
        'model':'numerical adjoint field + unchanged G1 signed velocity transport',
        'seed_range':[start,start+count-1],
        'primary_threshold_relative':.5,'teacher_wall_rms_ratio':1.,
        'common_update_norm':.025,
        'primary':prim,'reverse_phase':rev,'zero_teacher':zer,
        'curve':{k:summarize(v) for k,v in curve.items()},
        'gates':gates,
        'writer_pass':bool(all(gates.values())),
        'per_seed':{'primary':primary,'reverse_phase':reverse,
                    'zero_teacher':zero,'threshold_curve':curve},
        'caveats':[
            'Computed exact adjoint used as idealized teacher, not a proven physical reversed-wave injection',
            'Amplified teacher by global RMS factor; external calibration not intrinsic to sand',
            'Fixed-operator single-episode exposure; not the fully coupled G1 online transport',
            'Transport is signed patch velocity proxy, not hydrodynamic shear or Shields/Exner sediment',
            'Losses compared at equal material update norm, not equal forcing energy or actual sediment displacement',
        ],
    }
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--start',type=int,default=800)
    parser.add_argument('--count',type=int,default=16)
    parser.add_argument('--out',default='results/g2b_confirmatory.json')
    args=parser.parse_args()
    r=run(args.start,args.count)
    path=Path(args.out)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(r,indent=2)+'\n',encoding='utf8')
    print('G2b',('PASS' if r['writer_pass'] else 'FAIL'),json.dumps(r['gates'],indent=2))


if __name__=='__main__':
    main()
