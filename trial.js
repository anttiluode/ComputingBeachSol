(function(){
'use strict';
// ComputingBeachSol browser G9: deterministic synthetic 48-node receiver-power
// trial learning. Separate from Claude's 2D hydrodynamic proxy and Sol G6-G8
// held-out Robin-wall results. No teacher or gradient is used by an agent.
const N=48, SOURCE=3, RECEIVER=44, COUPLE=.7, W2=1.43;
const SEEDS=[1001,1009,1013,1019,1021,1031,1033,1039];
const SHAPES=['smooth','storm','white','smoothConserved','stormConserved'];
const COLORS={smooth:'#81e4d1',storm:'#f2be78',white:'#f28da8',smoothConserved:'#97b1ff',stormConserved:'#c5a8f0'};
const LABELS={smooth:'Smooth noise',storm:'Wave-shaped storms',white:'White noise',smoothConserved:'Conserved smooth',stormConserved:'Conserved storms'};
function add(a,b){return [a[0]+b[0],a[1]+b[1]]}
function sub(a,b){return [a[0]-b[0],a[1]-b[1]]}
function mul(a,b){return [a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]]}
function div(a,b){const den=b[0]*b[0]+b[1]*b[1];return [(a[0]*b[0]+a[1]*b[1])/den,(a[1]*b[0]-a[0]*b[1])/den]}
function energy(x){return x[0]*x[0]+x[1]*x[1]}
function solve(h,src,loss){
 const cp=new Array(N),dp=new Array(N),c=[-COUPLE,0];
 for(let i=0;i<N;i++){
   const diag=[(i===0||i===N-1?1:2)*COUPLE+.26-W2+1.1*h[i],loss];
   const rhs=i===src?[1,0]:[0,0];
   const q=i===0?diag:sub(diag,mul(c,cp[i-1]));
   cp[i]=i<N-1?div(c,q):[0,0];
   dp[i]=div(i===0?rhs:sub(rhs,mul(c,dp[i-1])),q);
 }
 const u=new Array(N);u[N-1]=dp[N-1];
 for(let i=N-2;i>=0;i--)u[i]=sub(dp[i],mul(cp[i],u[i+1]));
 return u;
}
function seeded(seed){
 let state=seed|0;
 return function(){state=(Math.imul(state,1664525)+1013904223)|0;return (state>>>0)/4294967296}
}
function initial(seed){
 const random=seeded(seed);
 return Array.from({length:N},(_,i)=>.013*(random()-.5)+.015*Math.cos(i*.15));
}
function smooth(a){
 const n=a.length;let x=a.slice();
 for(let pass=0;pass<4;pass++){
   x=x.map((v,i)=>(x[Math.max(0,i-1)]+2*v+x[Math.min(n-1,i+1)])*.25);
 }
 return x;
}
function demean(a){const mean=a.reduce((s,v)=>s+v,0)/a.length;return a.map(v=>v-mean)}
function median(a){
 if(!a.length)return NaN;
 const s=a.slice().sort((x,y)=>x-y);let m=s.length>>1;
 return s.length%2?s[m]:(s[m-1]+s[m])/2;
}
function db(a,b){return 10*Math.log10(Math.max(a,1e-24)/Math.max(b,1e-24))}
function shapeProposal(h,kind,rand,loss){
 const base=kind.startsWith('storm')?'storm':kind.startsWith('smooth')?'smooth':'white';
 let extraSolves=0,r;
 if(base==='storm'){
   const src=2+Math.floor(rand()*(N-4));
   r=solve(h,src,loss).map(energy);
   const sign=rand()<.5?-1:1;r=r.map(x=>sign*x);extraSolves++;
 }else{
   r=Array.from({length:N},()=>rand()-.5);
   if(base==='smooth')r=smooth(r);
 }
 if(kind.endsWith('Conserved'))r=demean(r);
 return {r,extraSolves};
}
// One global better/worse judge, 200 fixed candidate evaluations.
// An agent is allowed to undo a proposed material change exactly.
function runOne(seed,task,loss,kind,trials=200,step=.0025){
 if(!SHAPES.includes(kind))throw Error('Unknown proposal '+kind);
 if(task!=='quiet'&&task!=='loud')throw Error('Unknown objective');
 const h=initial(seed),start=energy(solve(h,SOURCE,loss)[RECEIVER]);
 let value=start,accepted=0,proposalSolves=0,receiverReads=1;
 const common=kind.endsWith('Conserved')?kind.replace('Conserved',''):kind;
 const code={smooth:17,storm:29,white:43}[common];
 const rand=seeded((Math.imul(seed,811)+code)|0);
 const samples=[{trial:0,db:0,power:value,accepted:0}];
 let maxAcceptedIncrease=0;
 for(let n=1;n<=trials;n++){
   const proposal=shapeProposal(h,kind,rand,loss);proposalSolves+=proposal.extraSolves;
   const max=Math.max(...proposal.r.map(Math.abs));
   const scale=max>1e-20?step/max:0;
   const candidate=h.map((v,i)=>v+scale*proposal.r[i]);
   const trialValue=energy(solve(candidate,SOURCE,loss)[RECEIVER]);receiverReads++;
   const isBetter=task==='quiet'?trialValue<value:trialValue>value;
   if(isBetter){
     const before=value;
     for(let i=0;i<N;i++)h[i]=candidate[i];
     value=trialValue;accepted++;
     maxAcceptedIncrease=Math.max(maxAcceptedIncrease,
       task==='quiet'?value-before:before-value);
   }
   if(n%10===0||n===trials)samples.push({trial:n,db:db(value,start),power:value,accepted});
 }
 const drift=h.reduce((x,v,i)=>x+v-initialBedCache(seed)[i],0); // signed bed sum drift: not a material proof
 return {seed,task,loss,kind,trials,step,startPower:start,endPower:value,
         db:db(value,start),accepted,receiverReads,proposalSolves,
         maxAcceptedObjectiveWorsening:maxAcceptedIncrease,
         signedMaterialChange:drift,samples};
}
const initialCache=new Map();
function initialBedCache(seed){if(!initialCache.has(seed))initialCache.set(seed,initial(seed));return initialCache.get(seed)}
function summarize(rows,loss,trials,step){
 const groups={},all={};
 for(const task of ['quiet','loud']){
  groups[task]={};
  for(const shape of SHAPES){
   const rec=rows.filter(x=>x.task===task&&x.kind===shape);
   groups[task][shape]={
    medianDb:median(rec.map(x=>x.db)),
    minDb:Math.min(...rec.map(x=>x.db)),maxDb:Math.max(...rec.map(x=>x.db)),
    meanAccepted:rec.reduce((s,x)=>s+x.accepted,0)/rec.length,
    receiverReads:rec.reduce((s,x)=>s+x.receiverReads,0),
    proposalSolves:rec.reduce((s,x)=>s+x.proposalSolves,0),
    curves:Array.from({length:trials/10+1},(_,i)=>median(rec.map(r=>r.samples[i].db)))
   };
  }
 }
 return {protocol:'SITE_G9_PROTOCOL.md',model:'48-node synthetic complex wave operator; NOT Claude 2D beach',
   seeds:SEEDS,loss,trials,step,tasks:['quiet','loud'],shapes:SHAPES,groups,perSeed:rows,
   note:'An external agent evaluates receiver power after each proposal and restores rejected changes. No autonomous natural sand learning.'};
}
function runSweep(loss=0.07,trials=200,step=.0025){
 const rows=[];
 for(const task of ['quiet','loud'])
  for(const seed of SEEDS)
   for(const kind of SHAPES)
    rows.push(runOne(seed,task,loss,kind,trials,step));
 return summarize(rows,loss,trials,step);
}
const API={SEEDS,SHAPES,runOne,runSweep,median,db,initial,shapeProposal};
if(typeof module!=='undefined'&&module.exports)module.exports=API;
if(typeof document==='undefined')return;
const $=id=>document.getElementById(id);
let last=null,busy=false;
function num(x,n=2){return Number.isFinite(x)?x.toFixed(n):'—'}
function plot(canvas,group,trials){
 const r=canvas.getBoundingClientRect();let w=Math.max(300,r.width),h=Math.max(180,r.height);
 const scale=Math.min(window.devicePixelRatio||1,2);canvas.width=Math.round(w*scale);canvas.height=Math.round(h*scale);
 const ctx=canvas.getContext('2d');ctx.setTransform(scale,0,0,scale,0,0);
 ctx.clearRect(0,0,w,h);
 const L=48,R=w-15,T=16,B=h-28;
 let values=SHAPES.flatMap(s=>group[s].curves);let lo=Math.min(0,...values),hi=Math.max(0,...values);
 let margin=Math.max(1,(hi-lo)*.1);lo-=margin;hi+=margin;
 const x=i=>L+(R-L)*i/(trials/10), y=v=>B-(v-lo)/(hi-lo)*(B-T);
 ctx.lineWidth=1;ctx.font='11px ui-monospace,monospace';
 for(let j=0;j<5;j++){let v=lo+j*(hi-lo)/4,yy=y(v);ctx.strokeStyle='#31535d';ctx.beginPath();ctx.moveTo(L,yy);ctx.lineTo(R,yy);ctx.stroke();ctx.fillStyle='#b7d0d0';ctx.fillText(num(v,1),2,yy+3)}
 for(let t=0;t<=trials;t+=50){let px=L+(R-L)*t/trials;ctx.fillText(String(t),px-10,h-7)}
 for(const kind of SHAPES){let z=group[kind].curves;ctx.beginPath();for(let i=0;i<z.length;i++)i?ctx.lineTo(x(i),y(z[i])):ctx.moveTo(x(i),y(z[i]));ctx.strokeStyle=COLORS[kind];ctx.lineWidth=kind==='smooth'?3:1.7;ctx.stroke()}
}
function update(){
 if(!last)return;
 plot($('quietChart'),last.groups.quiet,last.trials);
 plot($('loudChart'),last.groups.loud,last.trials);
 let html='';
 for(const kind of SHAPES){
  const q=last.groups.quiet[kind],l=last.groups.loud[kind];
  html+='<tr><td><span style="color:'+COLORS[kind]+'">●</span> '+LABELS[kind]+'</td><td>'+num(q.medianDb)+' dB</td><td>'+num(l.medianDb)+' dB</td><td>'+num(q.meanAccepted,1)+' / '+num(l.meanAccepted,1)+'</td><td>'+q.receiverReads+' + '+q.proposalSolves+'</td></tr>';
 }
 $('benchRows').innerHTML=html;
 $('runSummary').textContent='Completed: eight fixed seeds, both tasks, '+last.trials+' trials per seed/shape. Negative dB is better for quiet; positive dB is better for loud. Every proposed material modification was actually re-solved.';
}
async function execute(){
 if(busy)return;busy=true;$('runTrial').disabled=true;$('exportTrial').disabled=true;
 try{
  const loss=Number($('lossTrial').value),step=Number($('trialStep').value),trials=200,rows=[];
  for(const task of ['quiet','loud']){
   for(let si=0;si<SEEDS.length;si++){
    let seed=SEEDS[si];
    for(const shape of SHAPES)rows.push(runOne(seed,task,loss,shape,trials,step));
    $('runSummary').textContent='Testing '+task+' harbour, seed '+seed+' ('+(rows.length/80*100).toFixed(0)+'%)…';
    await new Promise(resolve=>requestAnimationFrame(resolve));
   }
  }
  last=summarize(rows,loss,trials,step);update();$('exportTrial').disabled=false;
 }catch(e){$('runSummary').textContent='Experiment error: '+e.message;throw e}
 finally{busy=false;$('runTrial').disabled=false}
}
function exportJson(){
 if(!last)return;
 const blob=new Blob([JSON.stringify(last,null,2)],{type:'application/json'});
 const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;
 a.download='computing-beach-trial-g9.json';document.body.appendChild(a);a.click();a.remove();
 setTimeout(()=>URL.revokeObjectURL(url),1000);
}
$('runTrial').addEventListener('click',execute);
$('exportTrial').addEventListener('click',exportJson);
window.addEventListener('resize',update);
window.__trialBeachDiagnostics=()=>last?{ready:true,loss:last.loss,seeds:last.seeds,groups:last.groups}: {ready:false};
})();