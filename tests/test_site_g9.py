"""G9 browser-agent and active-rest numerical integrity checks."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which("node"), "Node is optional in local Python installations")
class SiteG9Tests(unittest.TestCase):
    def js(self, code):
        p=subprocess.run(["node","-e",code],cwd=ROOT,
                         capture_output=True,text=True,timeout=45)
        self.assertEqual(p.returncode,0,p.stdout+"\n"+p.stderr)
        return json.loads(p.stdout.strip())

    def test_agent_keep_revert_and_material_conservation(self):
        data=self.js(r"""
const a=require('./trial.js');
const v=[
 a.runOne(1001,'quiet',.07,'smooth',40,.0025),
 a.runOne(1001,'loud',.07,'storm',40,.0025),
 a.runOne(1001,'quiet',.07,'smoothConserved',40,.0025),
 a.runOne(1001,'loud',.07,'stormConserved',40,.0025),
];
console.log(JSON.stringify(v.map(r=>({
 start:r.startPower,end:r.endPower,reads:r.receiverReads,solves:r.proposalSolves,
 worsening:r.maxAcceptedObjectiveWorsening,mass:r.signedMaterialChange,
 accepted:r.accepted,history:r.samples
}))));
""")
        self.assertEqual(len(data),4)
        for i,r in enumerate(data):
            self.assertEqual(r["reads"],41)
            self.assertEqual(r["solves"],40 if i in (1,3) else 0)
            self.assertLessEqual(r["worsening"],1e-12)
            self.assertEqual(r["history"][0]["trial"],0)
            self.assertEqual(r["history"][-1]["trial"],40)
            if i%2==0:self.assertLessEqual(r["end"],r["start"]+1e-12)
            else:self.assertGreaterEqual(r["end"],r["start"]-1e-12)
            if i in (2,3): self.assertLess(abs(r["mass"]),1e-10)

    def test_seed_sweep_is_fixed_and_all_shapes_reported(self):
        r=self.js(r"""
const a=require('./trial.js');
const x=a.runSweep(.07,20,.0025);
console.log(JSON.stringify({seeds:x.seeds,rows:x.perSeed.length,
q:Object.keys(x.groups.quiet),l:Object.keys(x.groups.loud),
n:x.groups.quiet.storm.receiverReads,s:x.groups.quiet.storm.proposalSolves,
zero:x.perSeed.every(r=>r.maxAcceptedObjectiveWorsening<=1e-12)}));
""")
        self.assertEqual(r["seeds"],[1001,1009,1013,1019,1021,1031,1033,1039])
        self.assertEqual(r["rows"],80)
        self.assertEqual(len(r["q"]),5)
        self.assertEqual(len(r["l"]),5)
        self.assertEqual(r["n"],8*21)
        self.assertEqual(r["s"],8*20)
        self.assertTrue(r["zero"])

    def test_online_page_has_distinct_active_rest(self):
        # Run exact browser script in a mocked DOM using Node vm.
        r=self.js(r"""
const vm=require('node:vm'),fs=require('node:fs');
const elements=new Map();
function get(id){
 if(!elements.has(id))elements.set(id,{
  value:id==='epoch'?'20':'0',checked:false,disabled:false,textContent:'',
  style:{},addEventListener(){},getBoundingClientRect(){return {width:300,height:220}},
  getContext(){return {setTransform(){},clearRect(){},beginPath(){},moveTo(){},
  lineTo(){},stroke(){},fillText(){},setLineDash(){}}}
 });
 return elements.get(id);
}
const window={addEventListener(){}},document={getElementById:get};
const context={window,document,console,Float64Array,Math,Number,Array,JSON,Promise};
vm.createContext(context);
vm.runInContext(fs.readFileSync('./online.js','utf8'),context);
const r=window.__onlineBeachModel.run(41,'quiet',0,20,.0005,.003,3);
console.log(JSON.stringify({
 keys:Object.keys(r.out),
 changes:r.out.restPhysical.rows[20].h.some((x,i)=>Math.abs(x-r.out.recalib.rows[20].h[i])>1e-10),
 finite:Number.isFinite(r.out.restPhysical.rows[20].J),
 first:r.out.restPhysical.rows[0].J,
 last:r.out.restPhysical.rows[20].J
}));
""")
        self.assertIn("restPhysical",r["keys"])
        self.assertTrue(r["changes"])
        self.assertTrue(r["finite"])
        self.assertGreater(r["first"],0)
        self.assertGreater(r["last"],0)

if __name__=="__main__":
    unittest.main()
