"""Tests for the separate, educational online learning page.

The new page is *not* the frozen Python G6-G8 experiment. These tests
check its self-contained, local-only web structure and a few illustrative
numerical consequences, rather than pretending its examples are held-out.
"""
import html.parser
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]


class Tags(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids=set()
        self.scripts=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if 'id' in d:self.ids.add(d['id'])
        if tag=='script':self.scripts.append(d.get('src',''))


class OnlineLearningPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html=(ROOT/'online.html').read_text('utf-8')
        cls.js=(ROOT/'online.js').read_text('utf-8')
        cls.index=(ROOT/'index.html').read_text('utf-8')
        cls.tags=Tags();cls.tags.feed(cls.html)

    def test_site_links_to_real_page(self):
        self.assertIn('./online.html',self.index)
        self.assertEqual(self.tags.scripts,['./online.js'])
        self.assertNotIn('https://',self.tags.scripts[0])
        self.assertNotIn('fetch(',self.js)
        self.assertNotIn('import(',self.js)

    def test_live_controls_are_not_placeholders(self):
        self.assertTrue({'task','loss','seed','step','teacher','track',
                         'run','export','epoch','bed','lossplot','cosplot','scores'}
                        <=self.tags.ids)
        for part in ('field(h,SOURCE','grad(u,G,error)','theta[i]+=',
                     'q[i]+.2*','z=relay(r,512)','teacherBeta',
                     'num(frozen.rows[10].cos','20 epochs'):
            self.assertIn(part,self.js+self.html)

    def test_javascript_syntax(self):
        node=shutil.which('node')
        if not node:self.skipTest('Node.js not installed')
        result=subprocess.run([node,'--check',str(ROOT/'online.js')],
                              capture_output=True,text=True,timeout=12)
        self.assertEqual(0,result.returncode,result.stderr)

    def test_numeric_examples_and_mass_conservation(self):
        node=shutil.which('node')
        if not node:self.skipTest('Node.js not installed')
        script=r"""
const fs=require('fs'),vm=require('vm'),assert=require('assert');
const fakeDoc={getElementById:()=>({value:'0',addEventListener(){}})};
const context={document:fakeDoc,window:{addEventListener(){}},console};
vm.runInNewContext(fs.readFileSync('online.js','utf8'),context);
const run=context.window.__onlineBeachModel.run;
const a=run(41,'quiet',0,20,.0005,.003,3);
assert(a.out.frozen.rows[0].cos>0.95);
assert(a.out.recalib.ratio<a.out.frozen.ratio);
assert(a.out.gd.ratio<=a.out.recalib.ratio);
assert(Math.abs(a.out.off.ratio-1)<1e-10);
const sum=(arr)=>arr.reduce((a,b)=>a+b,0);
for(const arm of Object.values(a.out)){
    const baseline=sum(arm.rows[0].h);
    for(const row of arm.rows)assert(Math.abs(sum(row.h)-baseline)<1e-9);
}
const lossy=run(777,'loud',.07,20,.0005,.003,3);
assert(lossy.out.frozen.rows[0].cos<0.5);
assert(lossy.out.gd.ratio<lossy.out.frozen.ratio);
console.log('online-example and zero-sum smoke tests passed');
"""
        res=subprocess.run([node,'-e',script],cwd=ROOT,capture_output=True,
                           text=True,timeout=30)
        self.assertEqual(res.returncode,0,res.stderr+res.stdout)


if __name__=='__main__':unittest.main()
