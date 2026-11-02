"""G1b: independent held-out resolution, arrival-window, common-tail tests.

No tuning on held-out seeds. Arrival is calibrated from the UNWRITTEN zero
material state only. Reader observes WML receiver traces, not the hidden bed.
"""
from __future__ import annotations
from dataclasses import asdict, replace
from pathlib import Path
import argparse, json
import numpy as np
from .model import Beach, Config

KS=(8,16,24,48)
SOURCES=(0,1,2)
READ_STEPS=510
WINDOWS={
    'prearrival':(-110,-10),
    'early':(-10,170),
    'late':(170,350),
    'whole':None,
}
HISTORIES={'AB':((0,1),(1,0)), 'ABX':((0,1,2),(1,0,2))}


def arrivals(beach):
    """Flat initial wall first 0.1%-peak crossing, never fit on test labels."""
    ans=[]
    for source in SOURCES:
        trace=beach.read(np.zeros(beach.cfg.k),source=source,steps=READ_STEPS)
        mask=np.flatnonzero(np.abs(trace)>=.001*np.max(np.abs(trace)))
        ans.append(int(mask[0]))
    return ans


def read_traces(beach,h):
    return np.stack([beach.read(h,source=s,steps=READ_STEPS) for s in SOURCES])


def build(beach,seeds,history,feedback=True):
    x=[];hidden=[];events=[]
    for seed in seeds:
        pair=[];maps=[];seen=[]
        for order in HISTORIES[history]:
            h,log=beach.history(order,seed=int(seed),feedback=feedback)
            seen.append([{'active_interfaces':a['active_interfaces'], 'total_transport':a['total_transport'], 'peak_proxy':a['peak_proxy']} for a in log])
            maps.append(h)
            pair.append(read_traces(beach,h))
        x.append(pair);hidden.append(maps);events.append(seen)
    return np.asarray(x),np.asarray(hidden),events


def window_features(x,a,name):
    if name=='whole':
        return x.reshape(x.shape[0],x.shape[1],-1)
    lo,hi=WINDOWS[name]
    feat=[x[:,:,s,max(0,a[s]+lo):min(READ_STEPS,a[s]+hi)] for s in range(3)]
    return np.concatenate(feat,axis=-1)


def predict(train,test,noise_std,seed=0):
    mu=train.mean((0,1))
    flat=train.reshape(-1,train.shape[-1])
    scale=np.maximum(flat.std(0),.03*max(np.max(flat.std(0)),1e-20))
    centroid=((train-mu)/scale).mean(0)
    direction=centroid[0]-centroid[1]
    rng=np.random.default_rng(seed)
    x=test+rng.normal(0,noise_std,size=test.shape)
    score=((x-mu)/scale)@direction
    # A zero classifier vector is an uninformed tie, not zero accuracy.
    ab=(score[:,0]>0).astype(float)+.5*(score[:,0]==0)
    ba=(score[:,1]<0).astype(float)+.5*(score[:,1]==0)
    return {'accuracy':float(np.mean(np.r_[ab,ba])), 'correct_ab':float(ab.sum()),
            'correct_ba':float(ba.sum()), 'total':int(len(ab)*2),
            'mean_abs_margin':float(np.mean(np.abs(score))),
            'scores':score.tolist()}


def evaluate(seeds_train=range(200,212),seeds_test=range(500,506),ks=KS,verbose=True):
    """Predeclared train/test seeds supplied by runner; returns raw ledger."""
    result={'config':asdict(Config()),'k_values':list(ks),
            'train_seeds':list(seeds_train),'test_seeds':list(seeds_test),
            'read_steps':READ_STEPS,'read_drive':Config().read_drive,
            'noise_scale':'4% of RMS over all training EARLY echoes at each K,history',
            'windows':WINDOWS,'histories':HISTORIES,'rows':{}}
    for k in ks:
        beach=Beach(replace(Config(),k=k,read_steps=READ_STEPS))
        a=arrivals(beach)
        row={'onsets':a,'patch_sizes':beach.weights.tolist(),
             'histories':{}}
        for hist in HISTORIES:
            train,train_h,_=build(beach,seeds_train,hist)
            test,test_h,logs=build(beach,seeds_test,hist)
            early=window_features(train,a,'early')
            noise=.04*float(np.sqrt(np.mean(early**2)))
            r={'noise_std':noise,'window_scores':{},
               'mean_map_order_distance':float(np.linalg.norm(test_h[:,0]-test_h[:,1],axis=1).mean()),
               'min_map_order_distance':float(np.linalg.norm(test_h[:,0]-test_h[:,1],axis=1).min()),
               'max_mass_difference':float(np.abs(test_h[:,0].sum(-1)-test_h[:,1].sum(-1)).max()),
               'mean_transport_per_event':float(np.mean([v['total_transport'] for group in logs for pair in group for v in pair])),
               'mean_active_interfaces_per_event':float(np.mean([v['active_interfaces'] for group in logs for pair in group for v in pair])),
               'mean_final_height_spread':float(test_h.std(axis=-1).mean())}
            for wi,wname in enumerate(WINDOWS):
                tr=window_features(train,a,wname)
                te=window_features(test,a,wname)
                r['window_scores'][wname]=predict(tr,te,noise,seed=2026+k*10+wi+(0 if hist=='AB' else 500))
            row['histories'][hist]=r
        if k in (8,48):
            control={}
            for hist in HISTORIES:
                _,hh,_=build(beach,seeds_test,hist,feedback=False)
                control[hist]={'max_AB_BA_distance':float(np.linalg.norm(hh[:,0]-hh[:,1],axis=1).max())}
            row['fixed_operator_control']=control
        result['rows'][str(k)]=row
        if verbose:
            print('K',k,{hist:{w:round(v['accuracy'],3) for w,v in row['histories'][hist]['window_scores'].items()}
                         for hist in HISTORIES},flush=True)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--phase',choices=('development','confirm'),default='development')
    p.add_argument('--out',default=None)
    args=p.parse_args()
    train=range(200,212) if args.phase=='development' else range(1100,1116)
    test=range(500,506) if args.phase=='development' else range(41000,41032)
    result=evaluate(train,test)
    dest=Path(args.out or 'results/g1b_'+args.phase+'.json')
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
