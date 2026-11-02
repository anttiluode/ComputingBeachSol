/* Plain Node regression tests for Beach AI's actual computational mechanisms. */
'use strict';
const assert=require('node:assert/strict');
const A=require('../beach-ai.js');
function almost(a,b,tol=1e-10){assert.ok(Math.abs(a-b)<tol,a+' != '+b)}
function norm(a){return Math.hypot(...a)}
function diff(a,b){return Math.hypot(...a.map((x,i)=>x-b[i]))}

// Six Fourier grating axes are orthonormal on 36 cells; no invisible weight state.
const axes=A.BASIS.flat();
for(let i=0;i<axes.length;i++)
 for(let j=0;j<axes.length;j++){
   let d=0;for(let k=0;k<A.N;k++)d+=axes[i][k]*axes[j][k];
   almost(d,i===j?1:0);
 }
const state=A.create();
assert.equal(state.nodes.length,4);
let before=A.materialSignature(state);
const x=A.writeOne(state.nodes[0],0,0,'delta',.36);
almost(x.after[0],.36);almost(x.after[1],0);
for(let k=1;k<3;k++)for(const a of A.readLocal(state.nodes[0],k))almost(a,0);
for(let i=1;i<4;i++)assert.deepEqual(Array.from(state.nodes[i].h),before[i]);
// A weak ping invokes no material writing and is strictly nondestructive.
before=A.materialSignature(state);
let ans=A.ping(state,0,0);
assert.ok(A.sameMaterial(before,A.materialSignature(state)));
assert.equal(ans.readOnly,true);
assert.ok(ans.y[0]>.05 && ans.y[0]<=x.after[0]+1e-10 && Math.abs(ans.y[1])<1e-10);
// Linked waves can interrogate remote beach material; disconnected cannot.
const net=A.create();
A.writeOne(net.nodes[3],2,1,'delta',.9);
const isolated=A.query(net,0,2,false,true);
const linked=A.query(net,0,2,true,true);
almost(norm(isolated.y),0);
assert.ok(linked.y[1]>.1);
assert.ok(linked.weights[3]>0);
// Optional teaching relays to immediate neighbours only.
const relayed=A.create();relayed.relay=true;
const affected=A.teach(relayed,0,1,1).map(r=>r.index).sort();
assert.deepEqual(affected,[0,1,2]);
assert.ok(A.readLocal(relayed.nodes[1],1)[1]>0);
almost(norm(A.readLocal(relayed.nodes[3],1)),0);
// Same-key additive Hebbian writes commute; predictive delta writes do not.
const order=A.abba(.36);
assert.ok(order.hebb<1e-11,JSON.stringify(order));
assert.ok(order.delta>.1,JSON.stringify(order));
assert.ok(order.deltaAB[1]>order.deltaBA[1]);
assert.ok(order.deltaBA[0]>order.deltaAB[0]);
// Hebbian repetition unbounded; delta approaches its teacher.
const h=A.beach(),d=A.beach();
for(let n=0;n<10;n++){
 A.writeOne(h,0,0,'hebb',.36);
 A.writeOne(d,0,0,'delta',.36);
}
assert.ok(A.readLocal(h,0)[0]>3.5);
assert.ok(A.readLocal(d,0)[0]>.98 && A.readLocal(d,0)[0]<1.001);
// 2D sine+cavity motion integrates without material write or NaNs.
const physical=A.create();physical.nodes[0].pulse={k:0,t:0,amp:1};
const sand=A.materialSignature(physical);
for(let t=0;t<350;t++)A.frame(physical);
assert.ok(A.sameMaterial(sand,A.materialSignature(physical)));
for(const n of physical.nodes)for(const f of n.u)assert.ok(Number.isFinite(f));

// Browser runtime smoke test: real event handlers + canvas draw with a mocked DOM.
const vm=require('node:vm'),fs=require('node:fs'),path=require('node:path');
const elements=new Map();
function mockElement(){
 const listeners={},children=[];
 return {listeners,children,style:{},textContent:'',value:'0',checked:false,
  append(...xs){children.push(...xs)},setAttribute(){},
  addEventListener(type,cb){listeners[type]=cb},
  getBoundingClientRect(){return {width:260,height:140}},
  getContext(){return {
    setTransform(){},clearRect(){},fillRect(){},beginPath(){},moveTo(){},
    lineTo(){},stroke(){},fill(){},fillText(){},createLinearGradient(){
      return {addColorStop(){}};
    }
  }};
 }
}
function el(id){if(!elements.has(id))elements.set(id,mockElement());return elements.get(id)}
for(const id of ['links','attention'])el(id).checked=true;
el('eta').value='.36';el('method').value='delta';
const dom={getElementById:el,createElement:mockElement};
const win={devicePixelRatio:1,addEventListener(){}};
const context={document:dom,window:win,requestAnimationFrame(){},
  console,Float64Array,Array,Math,Number};
vm.createContext(context);
vm.runInContext(fs.readFileSync(path.join(__dirname,'../beach-ai.js'),'utf8'),context);
assert.ok(win.__beachAiDiagnostics,'browser diagnostic missing');
assert.equal(el('prediction').textContent,'PING TO ASK');
el('teach').listeners.click();
assert.equal(el('prediction').textContent,'PING TO ASK');
const materialBefore=win.__beachAiDiagnostics().material;
el('ping').listeners.click();
assert.equal(el('prediction').textContent,'LEFT');
assert.ok(A.sameMaterial(materialBefore,win.__beachAiDiagnostics().material));
el('demo').listeners.click();
assert.equal(win.__beachAiDiagnostics().lessons,4);
el('control').listeners.click();
assert.ok(el('controlResult').textContent.includes('Delta'));

console.log('BEACH_AI_TEST_PASS',JSON.stringify({
 basis:axes.length,localWrite:x.after,abba:order,
 remoteLinked:linked.y,remoteDisconnected:isolated.y,
 affected,hebRepeated:A.readLocal(h,0),deltaRepeated:A.readLocal(d,0)
}));
