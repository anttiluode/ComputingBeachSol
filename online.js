(function(){
'use strict';
const N=48;
function add(a,b){return [a[0]+b[0],a[1]+b[1]]}
function sub(a,b){return [a[0]-b[0],a[1]-b[1]]}
function mul(a,b){return [a[0]*b[0]-a[1]*b[1],a[0]*b[1]+a[1]*b[0]]}
function div(a,b){const d=b[0]*b[0]+b[1]*b[1];return [(a[0]*b[0]+a[1]*b[1])/d,(a[1]*b[0]-a[0]*b[1])/d]}
function cmul(a,s){return [a[0]*s,a[1]*s]}
function energy(a){return a[0]*a[0]+a[1]*a[1]}
function dotre(a,b){return a[0]*b[0]+a[1]*b[1]}
const SOURCE=3,RECEIVER=N-4,COUPLE=.7,W2=1.43;
function solve(h,force,loss){let n=h.length,c=[],d=[],k=[];for(let i=0;i<n;i++){const diag=(i===0||i===n-1?1:2)*COUPLE+0.26-W2+1.1*h[i];d.push([diag,loss]);c.push([-COUPLE,0]);k.push([-COUPLE,0])}let cp=new Array(n),dp=new Array(n);cp[0]=div(c[0],d[0]);dp[0]=div(force[0],d[0]);for(let i=1;i<n;i++){let q=sub(d[i],mul(k[i],cp[i-1]));cp[i]=i<n-1?div(c[i],q):[0,0];dp[i]=div(sub(force[i],mul(k[i],dp[i-1])),q)}let u=new Array(n);u[n-1]=dp[n-1];for(let i=n-2;i>=0;i--)u[i]=sub(dp[i],mul(cp[i],u[i+1]));return u}
function field(h,src,amp,loss){const f=Array.from({length:h.length},()=>[0,0]);f[src]=amp;return solve(h,f,loss)}
function l2(x){return Math.sqrt(x.reduce((a,v)=>a+v*v,0))}
function demean(a){const m=a.reduce((x,y)=>x+y,0)/a.length;return a.map(x=>x-m)}
function cosine(a,b){return a.reduce((s,x,i)=>s+x*b[i],0)/Math.max(1e-30,l2(a)*l2(b))}
function grad(u,G,error){return u.map((z,i)=>-1.1*dotre(mul(G[i],z),error))}
function residual(u,tau,theta){return u.map((z,i)=>energy(add(z,tau[i]))-theta[i])}
function lap(a){const n=a.length;return a.map((v,i)=>2*v-a[(i+n-1)%n]-a[(i+1)%n])}
function relay(r,rounds=512){const n=r.length,q=new Float64Array(n);for(let t=0;t<rounds;t++){let next=new Float64Array(n);for(let i=0;i<n;i++)next[i]=q[i]+.2*((r[i]-r[(i+1)%n])-(2*q[i]-q[(i+n-1)%n]-q[(i+1)%n]));q.set(next)}return Array.from(q,(v,i)=>v-q[(i+n-1)%n])}
function rng(seed){return()=>{let x=seed|0;x=(x*1664525+1013904223)|0;seed=x;return (x>>>0)/4294967296}}
function init(seed){let rand=rng(seed);return Array.from({length:N},(_,i)=>.013*(rand()-.5)+.015*Math.cos(i*.15))}
function run(seed=41,task='quiet',loss=0,epochs=20,step=.0005,teacherBeta=.003,trackingT=3){
 let initial=init(seed),u0=field(initial,SOURCE,[1,0],loss),baseOutput=u0[RECEIVER];
 let target=task==='quiet'?[0,0]:cmul(baseOutput,2.0),out={};
 for(const kind of ['frozen','track3','recalib','restPhysical','natural','gd','off','twoPhase']){
  let h=initial.slice(),theta=u0.map(energy),rows=[],firstCos=null;
  for(let e=0;e<=epochs;e++){
   let u=field(h,SOURCE,[1,0],loss),G=field(h,RECEIVER,[1,0],loss),
       error=sub(u[RECEIVER],target),g=grad(u,G,error),ideal=demean(g.map(x=>-x));
   let J=.5*energy(error),normErr=Math.sqrt(2*J);
   if(e===epochs){rows.push({e,J,normErr,h:h.slice(),cos:null});break}
   let teacher=G.map(z=>cmul(mul(z,error),teacherBeta)),r=residual(u,teacher,theta),z;
   if(kind==='gd')z=ideal;
   else if(kind==='natural')z=relay(u.map(energy),512);
   else if(kind==='twoPhase')z=teacherBeta<=0?new Array(N).fill(0):relay(u.map((v,i)=>{let tp=add(v,teacher[i]),tn=sub(v,teacher[i]);return (energy(tp)-energy(tn))/(4*Math.max(teacherBeta,1e-30))}),512);
   else if(kind==='off')z=relay(u.map((v,i)=>energy(v)-theta[i]),512);
   else z=relay(r,512);
   let co=cosine(z,ideal);if(firstCos===null)firstCos=co;
   rows.push({e,J,normErr,cos:co,h:h.slice(),rmsStress:l2(r),bedNorm:l2(h)});
   const max=Math.max(...z.map(Math.abs)),rate=max>1e-30?step/max:0;
   // The only material redistribution is conservative edge flux from the relay.
   for(let i=0;i<N;i++)h[i]+=rate*z[i];
   if(kind==='track3'){
    let up=field(h,SOURCE,[1,0],loss),Gp=field(h,RECEIVER,[1,0],loss),
        ep=sub(up[RECEIVER],target),tp=Gp.map(v=>cmul(mul(v,ep),teacherBeta));
    for(let i=0;i<N;i++)theta[i]+=(energy(add(up[i],tp[i]))-theta[i])/trackingT;
   }
   if(kind==='recalib'){
    // Privileged reference: an extra measurement exactly replaces theta
    // while the bed is frozen. This is NOT passive physical resting.
    let uFree=field(h,SOURCE,[1,0],loss);
    for(let i=0;i<N;i++)theta[i]=energy(uFree[i]);
   }
   if(kind==='restPhysical'){
    // Distinct physically coupled rest: the teacher is switched OFF by an
    // external gate. The forward-only rest can move the bed before theta
    // adapts. The baseline does not magically reset without material cost.
    let uFree=field(h,SOURCE,[1,0],loss);
    let restDelta=relay(uFree.map((v,i)=>energy(v)-theta[i]),512);
    let restMax=Math.max(...restDelta.map(Math.abs));
    let restRate=restMax>1e-30?step/restMax:0;
    for(let i=0;i<N;i++)h[i]+=restRate*restDelta[i];
    let uAfter=field(h,SOURCE,[1,0],loss);
    for(let i=0;i<N;i++)theta[i]+=(energy(uAfter[i])-theta[i])/Math.max(1,trackingT);
   }
  }
  out[kind]={rows,firstCos,ratio:rows.at(-1).J/rows[0].J,improve:(rows[0].J-rows.at(-1).J)/rows[0].J};
 }
 return {seed,task,loss,teacherBeta,trackingT,step,target,baseOutput,out};
}
const $=id=>document.getElementById(id);
const colors={frozen:'#65e5d1',track3:'#ffcc79',recalib:'#a6a6ff',restPhysical:'#ffa9a0',gd:'#9af0a6',natural:'#ef8da4',off:'#7a9ca5',twoPhase:'#d4bcf9'};
const labels={frozen:'Frozen θ',track3:'Teacher-tracking θ',recalib:'Privileged θ reset (bed frozen)',restPhysical:'Active rest (bed moves; T tracking)',gd:'Exact gradient (oracle)',natural:'Plain field energy',off:'Teacher off',twoPhase:'External two-phase subtraction'};
let latest=null;
function num(v,d=3){return Number.isFinite(v)?v.toFixed(d):'—'}
function canvas(canvas){let rect=canvas.getBoundingClientRect(),width=Math.max(1,rect.width),height=Math.max(1,rect.height),dpr=Math.min(2,window.devicePixelRatio||1);canvas.width=Math.floor(width*dpr);canvas.height=Math.floor(height*dpr);let cx=canvas.getContext('2d');cx.setTransform(dpr,0,0,dpr,0,0);return {ctx:cx,w:width,h:height}}
function graph(axis,rows,isCos){
 let {ctx,w,h}=canvas($(axis));ctx.clearRect(0,0,w,h);let L=39,R=w-12,T=16,B=h-29;
 let dataset=Object.entries(rows.out).map(([k,v])=>({k,v:v.rows.map(r=>isCos?r.cos:r.J/v.rows[0].J)}));
 const values=dataset.flatMap(d=>d.v.filter(v=>Number.isFinite(v)));
 let min=isCos?-1:Math.min(0.0,...values),max=isCos?1:Math.max(1.05,...values);
 if(!isCos)max=Math.min(4,max*1.07);if(max===min)max=min+1;
 const yy=v=>B-(Math.max(min,Math.min(max,v))-min)/(max-min)*(B-T),xx=i=>L+(R-L)*i/20;
 ctx.lineWidth=1;ctx.font='10px ui-monospace,monospace';
 for(let j=0;j<=4;j++){let v=min+(max-min)*j/4,y=yy(v);ctx.strokeStyle='#42616c88';ctx.beginPath();ctx.moveTo(L,y);ctx.lineTo(R,y);ctx.stroke();ctx.fillStyle='#9cb6b6';ctx.fillText(num(v,isCos?1:2),2,y+3)}
 for(const t of [0,5,10,15,20]){let x=xx(t);ctx.fillStyle='#96b5ba';ctx.fillText(String(t),x-5,h-9)}
 const active=+$('epoch').value;ctx.setLineDash([4,5]);ctx.strokeStyle='#d8d8d8a0';ctx.beginPath();ctx.moveTo(xx(active),T);ctx.lineTo(xx(active),B);ctx.stroke();ctx.setLineDash([]);
 for(const d of dataset){ctx.beginPath();let initialized=false;for(let i=0;i<d.v.length;i++){let v=d.v[i];if(!Number.isFinite(v)){initialized=false;continue}let x=xx(i),y=yy(v);if(!initialized){ctx.moveTo(x,y);initialized=true}else ctx.lineTo(x,y)}ctx.strokeStyle=colors[d.k];ctx.lineWidth=d.k==='frozen'||d.k==='recalib'||d.k==='restPhysical'?2.7:1.3;ctx.globalAlpha=d.k==='twoPhase'?.55:1;ctx.stroke();ctx.globalAlpha=1;}
}
function bedplot(data){
 let {ctx,w,h}=canvas($('bed'));ctx.clearRect(0,0,w,h);const epoch=+$('epoch').value;
 let L=44,R=w-18,T=18,B=h-28,keys=['frozen','track3','recalib','restPhysical','gd'],max=1e-6;
 for(const key of keys)for(const x of data.out[key].rows[epoch].h)max=Math.max(max,Math.abs(x));
 max*=1.15;let xx=i=>L+(R-L)*i/(N-1),yy=v=>(T+B)/2-v/max*(B-T)/2;
 for(let i=0;i<5;i++){let y=T+(B-T)*i/4;ctx.strokeStyle='#4e677651';ctx.beginPath();ctx.moveTo(L,y);ctx.lineTo(R,y);ctx.stroke();}
 ctx.font='10px ui-monospace,monospace';ctx.fillStyle='#9dbdc1';ctx.fillText('+'+num(max,3),4,T+3);ctx.fillText('0',5,yy(0)+3);ctx.fillText('-'+num(max,3),4,B);ctx.fillText('west/source',L,B+17);ctx.fillText('harbour →',R-72,B+17);
 for(const key of keys){let arr=data.out[key].rows[epoch].h;ctx.beginPath();for(let i=0;i<N;i++){let x=xx(i),y=yy(arr[i]);i?ctx.lineTo(x,y):ctx.moveTo(x,y)}ctx.strokeStyle=colors[key];ctx.lineWidth=key==='frozen'||key==='recalib'||key==='restPhysical'?2.2:1.2;ctx.stroke()}
 let f=data.out.frozen.rows[epoch],c=data.out.recalib.rows[epoch];
 $('inspect').textContent=`Epoch ${epoch}: frozen-baseline receiver loss ${num(f.J/data.out.frozen.rows[0].J)}, teacher-free recalibration ${num(c.J/data.out.recalib.rows[0].J)}. All curves show actual material heights, not simulated sand photos.`;
}
function table(data){let html='';for(const [key,run] of Object.entries(data.out)){const start=run.rows[0],mid=run.rows[10],last=run.rows[20];html+=`<tr><td><span style="color:${colors[key]}">●</span> ${labels[key]}</td><td>${num(last.J/start.J,4)}</td><td>${num(start.cos,3)}</td><td>${num(mid.cos,3)}</td></tr>`}$('scores').innerHTML=html}
function draw(){if(!latest)return;graph('lossplot',latest,false);graph('cosplot',latest,true);bedplot(latest);table(latest)}
function resetStatus(){
 const frozen=latest.out.frozen,recalib=latest.out.recalib;
 $('best').textContent=num(recalib.ratio,3);$('frozen').textContent=num(frozen.ratio,3);$('alignment').textContent=num(frozen.rows[10].cos,3);
 let note=latest.loss>=.07?' Strong damping: the injected teacher is not the true adjoint.':' Watch when frozen θ loses alignment; this is not proof of naturally self-training sediment.';
 $('status').textContent=`Numerical solver finished · 20 epochs · K=48 · 8 different writer branches.${note}`;
}
async function execute(){
 let runButton=$('run');runButton.disabled=true;$('export').disabled=true;$('status').textContent='Solving a new wave operator at every material update…';
 await new Promise(resolve=>requestAnimationFrame(resolve));
 try{let result=run(Number($('seed').value),$('task').value,Number($('loss').value),20,Number($('step').value),Number($('teacher').value),Number($('track').value));latest=result;$('epoch').disabled=false;$('export').disabled=false;$('epoch').value='20';$('epochOut').textContent='20';resetStatus();draw()}
 catch(error){$('status').textContent='Experiment failed: '+String(error);throw error}
 finally{runButton.disabled=false}
}
function exportData(){
 if(!latest)return;
 const notes={model:'48-node, steady-state complex tridiagonal wave operator',teacher:'receiver-launched reciprocal numerical field, not verified physical adjoint at loss',projection:'G8 neighbour-edge relay, 512 rounds per writer update; externally norm-matched steps; restPhysical has extra forward measurements and a second bed update per epoch',limitations:'Synthetic diagnostic, not the preregistered Python or Claude numerical benchmark; no real sand.'};
 const blob=new Blob([JSON.stringify({...latest,notes},null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');
 a.href=url;a.download='beach-online-memory.json';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
for(const [id,out,digits,suffix] of [['step','stepOut',4,''],['teacher','teacherOut',4,''],['track','trackOut',0,' epochs']]){$(id).addEventListener('input',()=>$(out).textContent=Number($(id).value).toFixed(digits)+suffix)}
$('run').addEventListener('click',execute);$('export').addEventListener('click',exportData);$('epoch').addEventListener('input',()=>{$('epochOut').textContent=$('epoch').value;draw()});window.addEventListener('resize',draw);
window.__onlineBeachDiagnostics=()=>({ready:!!latest,task:latest?.task,loss:latest?.loss,seed:latest?.seed,step:latest?.step,teacherBeta:latest?.teacherBeta,trackingT:latest?.trackingT,ratios:latest?Object.fromEntries(Object.entries(latest.out).map(([key,v])=>[key,v.ratio])):null,epoch:Number($('epoch').value)});
window.__onlineBeachModel={run};
})();
