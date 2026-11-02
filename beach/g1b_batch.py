"""Deterministically cache G1b seeded worlds and aggregate without tuning.

The batched reads call the ORIGINAL WallMemoryLaw Cavity.run with all written
material states together. An exact-parity smoke test against Beach.read gave 0.
"""
import argparse, json
from pathlib import Path
import numpy as np
from dataclasses import replace, asdict
from .model import Beach, Config
from .resolution import (READ_STEPS, WINDOWS, HISTORIES, KS, arrivals,
                         build, window_features, predict)


def batch(k,split,hist,offset,count,outdir='results/g1b_batches'):
    start=1100 if split=='train' else 41000
    seeds=list(range(start+offset,start+offset+count))
    b=Beach(replace(Config(),k=k,read_steps=READ_STEPS))
    hidden=[];logs=[]
    for seed in seeds:
        pair=[];logs_pair=[]
        for order in HISTORIES[hist]:
            h,lg=b.history(order,seed=int(seed))
            pair.append(h)
            logs_pair.append([{'active_interfaces':r['active_interfaces'],
                               'total_transport':r['total_transport'],
                               'peak_proxy':r['peak_proxy']} for r in lg])
        hidden.append(pair);logs.append(logs_pair)
    hidden=np.asarray(hidden)
    bits=b.kappa_bits(hidden.reshape(-1,k))
    traced=[]
    for src in range(3):
        y=b.cav.run(bits,source=src,steps=READ_STEPS)[:,:,0]*b.cfg.read_drive
        traced.append(y.reshape(len(seeds),2,READ_STEPS))
    traces=np.stack(traced,axis=2)
    p=Path(outdir);p.mkdir(parents=True,exist_ok=True)
    f=p/f'K{k}_{split}_{hist}_{offset:02}.npz'
    np.savez_compressed(f,traces=traces,maps=hidden,seeds=np.array(seeds),
                        activity=np.asarray([[[(item['active_interfaces'],
                                              item['total_transport'],
                                              item['peak_proxy']) for item in pair]
                                               for pair in seed] for seed in logs]),
                        arrival=np.asarray(arrivals(b)))
    print(f,'saved',len(seeds),flush=True)


def gather(outdir='results/g1b_batches'):
    p=Path(outdir)
    out={'protocol':'PREREG_ROUND3.md',
         'train_seeds':list(range(1100,1116)),
         'test_seeds':list(range(41000,41032)),
         'windows':WINDOWS,'k_values':list(KS),
         'histories':{},'model':asdict(Config())}
    for k in KS:
        row={'histories':{}}
        for hist in HISTORIES:
            split={}
            for typ,n in [('train',16),('test',32)]:
                fs=list(p.glob(f'K{k}_{typ}_{hist}_*.npz'))
                assert fs,(k,typ,hist)
                group=[]
                for f in fs:
                    with np.load(f) as z:
                        group.append((z['seeds'],z['traces'],z['maps'],
                                      z['activity'],z['arrival']))
                group.sort(key=lambda v:int(v[0][0]))
                seeds=np.concatenate([z[0] for z in group])
                expected=np.arange(1100,1116) if typ=='train' else np.arange(41000,41032)
                assert np.array_equal(seeds,expected),(k,typ,seeds.tolist())
                assert all(np.array_equal(z[4],group[0][4]) for z in group)
                split[typ]=(np.concatenate([z[1] for z in group]),
                            np.concatenate([z[2] for z in group]),
                            np.concatenate([z[3] for z in group]),group[0][4])
            train,_,_,a=split['train']
            test,hidden,activity,_=split['test']
            noise=.04*np.sqrt(np.mean(window_features(train,a,'early')**2))
            r={'arrival_steps':a.tolist(),'noise_std':float(noise),
               'mean_map_order_distance':float(np.linalg.norm(hidden[:,0]-hidden[:,1],axis=1).mean()),
               'min_map_order_distance':float(np.linalg.norm(hidden[:,0]-hidden[:,1],axis=1).min()),
               'mean_transport_per_event':float(activity[...,1].mean()),
               'mean_active_interfaces_per_event':float(activity[...,0].mean()),
               'mean_final_height_spread':float(hidden.std(-1).mean()),'window_scores':{}}
            for wi,w in enumerate(WINDOWS):
                r['window_scores'][w]=predict(window_features(train,a,w),
                         window_features(test,a,w),noise,
                         seed=2026+k*10+wi+(0 if hist=='AB' else 500))
            row['histories'][hist]=r
        out['histories'][str(k)]=row
    return out


def main():
    pa=argparse.ArgumentParser()
    pa.add_argument('--k',type=int)
    pa.add_argument('--split',choices=['train','test'])
    pa.add_argument('--hist',choices=['AB','ABX'])
    pa.add_argument('--offset',type=int,default=0)
    pa.add_argument('--count',type=int,default=8)
    pa.add_argument('--gather',action='store_true')
    pa.add_argument('--out',default='results/g1b_confirmatory.json')
    a=pa.parse_args()
    if a.gather:
        r=gather()
        path=Path(a.out);path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(r,indent=2)+'\n')
        for k,v in r['histories'].items():
            for h,record in v['histories'].items():
                print('K',k,h,{w:round(z['accuracy'],4)
                              for w,z in record['window_scores'].items()})
    else:
        batch(a.k,a.split,a.hist,a.offset,a.count)

if __name__=='__main__':
    main()
