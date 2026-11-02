"""G2d fair conservation benchmark; locked fresh seeds 1200–1215."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from .model import Beach
from .energy_writer import test_case,summarize


def run(seeds=range(1200,1216)):
    b=Beach()
    rows=[test_case(b,int(seed),ratio=.02,threshold_fraction=0,
                    steps=310,step_norm=.025) for seed in seeds]
    summary=summarize(rows)
    wins_natural=sum(x['projected']['ratio']<x['forward_only_conserved']['ratio'] for x in rows)
    wins_single=sum(x['projected']['ratio']<x['single_plus_conserved']['ratio'] for x in rows)
    gates={
        'D1':wins_natural>=12,
        'D2':wins_single>=12,
        'D3':summary['projected']['mean_cosine']>=.999 and summary['projected']['lower_loss']>=14,
        'D4':max(abs(x['mass_change_projected']) for x in rows)<1e-10,
    }
    return {'protocol':'PREREG_G2D.md','seeds':list(seeds),
            'threshold_fraction':0,'teacher_ratio':.02,'step_norm':.025,
            'summary':summary,'projected_beats_forward_conserved':wins_natural,
            'projected_beats_single_conserved':wins_single,
            'gates':gates,'per_seed':rows}


def main():
    p=argparse.ArgumentParser();p.add_argument('--out',default='results/g2d_confirmatory.json');a=p.parse_args()
    result=run()
    dst=Path(a.out);dst.parent.mkdir(exist_ok=True,parents=True)
    dst.write_text(json.dumps(result,indent=2)+'\n')
    print('G2d',result['gates'],'contrast beats conserved natural',result['projected_beats_forward_conserved'],flush=True)

if __name__=='__main__':main()
