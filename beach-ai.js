/* Computing Beach / Sol — Beach AI Lab.
   Four writable beaches with visible slow Fourier coefficients and fast waves.
   Effective fast-weight readout is a material projection, NOT a measured PDE echo.
   No external packages, networks, or neural claims. See BEACH_AI_LAB.md. */
(function(){
'use strict';
const N=36, COUNT=4, BANDS=[3,6,10], TAU=2*Math.PI;
const NAMES=['A / Tidal shelf','B / Long inlet','C / Reef pool','D / South harbour'];
const COLORS=['#f6c077','#6be8d9','#c6a1ed'];
const EDGES=[[0,1],[0,2],[1,3],[2,3]];
const BASIS=BANDS.map(m=>[0,1].map(ch=>Float64Array.from({length:N},(_,i)=>
  Math.sqrt(2/N)*(ch===0?Math.cos(TAU*m*i/N):Math.sin(TAU*m*i/N)))));
function beach(){
 return {h:new Float64Array(N),u:new Float64Array(N),prev:new Float64Array(N),
   next:new Float64Array(N),pulse:null,writes:0};
}
function create(){
 return {nodes:Array.from({length:COUNT},beach),selected:0,band:0,value:0,
    method:'delta',eta:.36,links:true,attention:true,relay:false,
    lastQuery:null,logs:[],ticks:0,learned:0};
}
function dot(x,y){let r=0;for(let i=0;i<N;i++)r+=x[i]*y[i];return r}
function readLocal(node,k){
 return [dot(node.h,BASIS[k][0]),dot(node.h,BASIS[k][1])];
}
function materialMatrix(node){return BANDS.map((_,k)=>readLocal(node,k))}
function writeOne(node,k,v,method,eta){
 const before=readLocal(node,k),target=v===0?[1,0]:[0,1];
 const residual=method==='delta'?[target[0]-before[0],target[1]-before[1]]:target;
 for(let i=0;i<N;i++)node.h[i]+=eta*(residual[0]*BASIS[k][0][i]+residual[1]*BASIS[k][1][i]);
 node.writes++;
 node.pulse={k,t:0,amp:1};
 const after=readLocal(node,k);
 return {before,after,residual,error:Math.hypot(target[0]-after[0],target[1]-after[1])};
}
function neighbours(i){return EDGES.flatMap(([a,b])=>a===i?[b]:b===i?[a]:[])}
function teach(state,index,k,v){
 let list=[{index,result:writeOne(state.nodes[index],k,v,state.method,state.eta)}];
 if(state.relay&&state.links){
  for(const n of neighbours(index))
   list.push({index:n,result:writeOne(state.nodes[n],k,v,state.method,state.eta*.3)});
 }
 state.learned++;
 state.lastQuery=null;
 return list;
}
function reachability(root,links){
 const visible=[0,0,0,0];visible[root]=1;
 if(!links)return visible;
 let p=[0,0,0,0];p[root]=1;
 for(let t=0;t<4;t++){
  const next=[0,0,0,0];
  for(let i=0;i<COUNT;i++){
   next[i]+=.45*p[i];
   const ns=neighbours(i);
   for(const j of ns)next[j]+=.55*p[i]/ns.length;
  }
  p=next;
  for(let i=0;i<COUNT;i++)visible[i]=Math.max(visible[i],p[i]);
 }
 return visible;
}
function query(state,root,k,links=state.links,attention=state.attention){
 const r=reachability(root,links);
 const out=state.nodes.map(n=>readLocal(n,k));
 const score=out.map((v,i)=>r[i]*(attention?
  Math.exp(5*Math.min(1.8,Math.hypot(v[0],v[1]))):1));
 const sum=score.reduce((x,y)=>x+y,0)||1;
 const weights=score.map(x=>x/sum);
 const y=[0,0];for(let i=0;i<COUNT;i++){
  y[0]+=weights[i]*out[i][0];y[1]+=weights[i]*out[i][1];
 }
 const pLeft=Math.exp(3*y[0])/(Math.exp(3*y[0])+Math.exp(3*y[1]));
 return {root,k,local:out,reach:r,weights,y,pLeft,readOnly:true};
}
function materialSignature(state){return state.nodes.map(n=>Array.from(n.h))}
function sameMaterial(a,b){return a.every((n,i)=>n.every((v,j)=>v===b[i][j]))}
function ping(state,root,k){
 const previous=materialSignature(state);
 const answer=query(state,root,k);
 state.lastQuery=answer;
 state.nodes[root].pulse={k,t:0,amp:.1};
 if(!sameMaterial(previous,materialSignature(state)))
  throw Error('Probe changed the material!');
 return answer;
}
function preset(state){
 const plan=[[0,0,0],[1,1,1],[2,2,0],[3,0,1]];
 const results=[];
 for(const [i,k,v] of plan)results.push({i,k,v,out:teach(state,i,k,v)});
 return results;
}
function abba(eta=.36){
 function trial(method,order){
  const node=beach();
  for(const target of order)writeOne(node,0,target,method,eta);
  return Array.from(node.h);
 }
 function distance(a,b){return Math.hypot(...a.map((v,i)=>v-b[i]))}
 const h1=trial('hebb',[0,1]),h2=trial('hebb',[1,0]);
 const d1=trial('delta',[0,1]),d2=trial('delta',[1,0]);
 const left1=readLocal({h:Float64Array.from(d1)},0),
       left2=readLocal({h:Float64Array.from(d2)},0);
 return {hebb:distance(h1,h2),delta:distance(d1,d2),
   deltaAB:left1,deltaBA:left2};
}
function frame(state){
 const injected=new Array(COUNT).fill(0);
 for(let b=0;b<COUNT;b++){
  const n=state.nodes[b],pulse=n.pulse;
  if(pulse){
   const omega=.16+.075*pulse.k;
   const envelope=Math.exp(-pulse.t/35);
   injected[b]+=pulse.amp*Math.sin(omega*pulse.t)*envelope;
   pulse.t++;
   if(pulse.t>145)n.pulse=null;
  }
  if(state.links){
   for(const j of neighbours(b))injected[b]+=.12*state.nodes[j].u[N-3];
  }
 }
 for(let b=0;b<COUNT;b++){
  const n=state.nodes[b];
  n.next[0]=injected[b];
  n.next[N-1]=.78*n.u[N-2];
  for(let x=1;x<N-1;x++){
   const c=.7+.09*Math.tanh(3*n.h[x]),c2=c*c*.28*.28;
   n.next[x]=2*n.u[x]-.986*n.prev[x]+c2*(n.u[x+1]-2*n.u[x]+n.u[x-1])-.014*n.u[x];
  }
 }
 for(const n of state.nodes){
  const prev=n.prev;n.prev=n.u;n.u=n.next;n.next=prev;
 }
 state.ticks++;
}
const API={N,COUNT,BANDS,BASIS,EDGES,beach,create,readLocal,materialMatrix,
 writeOne,neighbours,teach,reachability,query,ping,preset,abba,frame,
 materialSignature,sameMaterial};
if(typeof module!=='undefined'&&module.exports)module.exports=API;
if(typeof document==='undefined')return;

const $=id=>document.getElementById(id);
const S=create();
let rendered=false;
function nfmt(x){return Math.abs(x)<.0005?'0.00':x.toFixed(2)}
function log(text){S.logs.unshift(text);if(S.logs.length>6)S.logs.length=6;
 $('eventLog').textContent=S.logs.join('\n');}
function drawNode(index){
 const c=$('canvas'+index),rect=c.getBoundingClientRect(),w=Math.max(140,rect.width),h=Math.max(105,rect.height);
 const ratio=Math.min(2,window.devicePixelRatio||1);
 c.width=Math.round(w*ratio);c.height=Math.round(h*ratio);
 const ctx=c.getContext('2d');ctx.setTransform(ratio,0,0,ratio,0,0);
 const n=S.nodes[index],mid=h*.43,bed=h*.80,pad=9,W=w-2*pad;
 ctx.clearRect(0,0,w,h);
 let g=ctx.createLinearGradient(0,0,0,h);
 g.addColorStop(0,'#113742');g.addColorStop(.65,'#142e36');g.addColorStop(1,'#574331');
 ctx.fillStyle=g;ctx.fillRect(0,0,w,h);
 for(let i=1;i<4;i++){ctx.strokeStyle='#a8d8d81d';ctx.beginPath();
  ctx.moveTo(0,i*h/4);ctx.lineTo(w,i*h/4);ctx.stroke()}
 const watermax=Math.max(.3,...n.u.map(x=>Math.abs(x)));
 ctx.beginPath();
 for(let i=0;i<N;i++){
  const x=pad+W*i/(N-1),y=mid-n.u[i]*Math.min(25,22/watermax);
  if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
 }
 ctx.strokeStyle='#6eead9';ctx.shadowColor='#55e5d7';ctx.shadowBlur=7;
 ctx.lineWidth=2.3;ctx.stroke();ctx.shadowBlur=0;
 const max=Math.max(.1,...n.h.map(x=>Math.abs(x)));
 const scale=21/max;
 ctx.beginPath();ctx.moveTo(pad,h);
 for(let i=0;i<N;i++)ctx.lineTo(pad+W*i/(N-1),bed-n.h[i]*scale);
 ctx.lineTo(pad+W,h);ctx.closePath();
 let sand=ctx.createLinearGradient(0,bed-25,0,h);
 sand.addColorStop(0,'#ebbb76');sand.addColorStop(1,'#806348');
 ctx.fillStyle=sand;ctx.fill();
 ctx.beginPath();
 for(let i=0;i<N;i++){
   const x=pad+W*i/(N-1),y=bed-n.h[i]*scale;
   if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
 }
 ctx.strokeStyle='#ffd28a';ctx.lineWidth=1.8;ctx.stroke();
 ctx.fillStyle='#a9d8d5';ctx.font='10px system-ui';ctx.fillText('fast u(x,t)',12,16);
 ctx.fillStyle='#ffe0a5';ctx.fillText('material h(x)',12,bed-28);
}
function displayMatrix(){
 for(let i=0;i<COUNT;i++){
  const M=materialMatrix(S.nodes[i]);
  const holder=$('matrix'+i);holder.textContent='';
  for(let k=0;k<3;k++){
   const row=document.createElement('div');row.className='matrix-line';
   const label=document.createElement('span');label.textContent=['LONG','MID','SHORT'][k];row.append(label);
   for(let v=0;v<2;v++){
    const cell=document.createElement('span');cell.textContent=nfmt(M[k][v]);
    cell.className='matrix-cell';
    const magnitude=Math.min(.85,Math.abs(M[k][v])*.63);
    cell.style.background=M[k][v]>=0?'rgba(101,223,201,'+magnitude+')':
       'rgba(248,156,171,'+magnitude+')';
    row.append(cell);
   }
   holder.append(row);
  }
  $('writes'+i).textContent=String(S.nodes[i].writes)+' lessons';
  $('beach'+i).setAttribute('aria-pressed',String(S.selected===i));
 }
}
function renderAnswer(answer){
 const left=answer.y[0],right=answer.y[1];
 $('response').textContent='['+nfmt(left)+', '+nfmt(right)+']';
 $('prediction').textContent=left>right?'LEFT':'RIGHT';
 $('confidence').textContent=(100*Math.max(answer.pLeft,1-answer.pLeft)).toFixed(1)+'%';
 $('probLeft').style.width=(100*answer.pLeft).toFixed(1)+'%';
 $('probRight').style.width=(100*(1-answer.pLeft)).toFixed(1)+'%';
 $('pathMode').textContent=S.links?'Connected network':'Isolated beach';
 for(let i=0;i<COUNT;i++){
  $('att'+i).style.width=(100*answer.weights[i]).toFixed(1)+'%';
  $('attNum'+i).textContent=(100*answer.weights[i]).toFixed(1)+'%';
 }
 const matrix=answer.weights;
 for(const [a,b] of EDGES){
  const edge=$('edge'+a+b);
  edge.style.opacity=S.links?String(.28+.68*Math.max(matrix[a],matrix[b])):'.06';
  edge.style.strokeWidth=String(2+6*Math.max(matrix[a],matrix[b]));
 }
}
function clearReadout(){
 $('response').textContent='—';
 $('prediction').textContent='PING TO ASK';
 $('confidence').textContent='—';
 $('probLeft').style.width='50%';
 $('probRight').style.width='50%';
 $('pathMode').textContent='No weak probe launched yet';
 for(let i=0;i<COUNT;i++){
  $('att'+i).style.width='0%';
  $('attNum'+i).textContent='—';
 }
 for(const [a,b] of EDGES){
  const edge=$('edge'+a+b);
  edge.style.opacity=S.links?'.26':'.05';
  edge.style.strokeWidth='2';
 }
}
function update(){
 displayMatrix();
 if(S.lastQuery)renderAnswer(query(S,S.lastQuery.root,S.lastQuery.k));
 else clearReadout();
 $('lessons').textContent=String(S.learned);
 $('modeTitle').textContent=S.method==='delta'?'Delta rule · corrective write':'Hebbian · additive write';
 $('probeMode').textContent=S.attention?'Content-sensitive attention':'Uniform reachable mixing';
 $('gating').textContent=S.links?'Links open':'Links disconnected';
 $('etaNumber').textContent=S.eta.toFixed(2);
}
function select(index){S.selected=index;S.lastQuery=null;$('source').value=String(index);update()}
function teachClick(){
 const targets=['LEFT','RIGHT'],bands=['LONG','MID','SHORT'];
 const list=teach(S,S.selected,S.band,S.value);
 log('STRONG WRITE · '+NAMES[S.selected]+' · '+bands[S.band]+' → '+targets[S.value]+
  ' · '+S.method.toUpperCase()+' · writes '+list.length+' beach(es)');
 update();
}
function pingClick(){
 const before=materialSignature(S);
 const ans=ping(S,S.selected,S.band);
 log('WEAK PING · '+NAMES[S.selected]+' · '+['LONG','MID','SHORT'][S.band]+
  ' · output ['+nfmt(ans.y[0])+', '+nfmt(ans.y[1])+'] · material unchanged: '+
  sameMaterial(before,materialSignature(S)));
 update();
}
function demo(){
 S.nodes=Array.from({length:COUNT},beach);S.learned=0;
 const old=S.relay;S.relay=false;preset(S);S.relay=old;
 log('LOADED 4 LESSONS · frequency collisions intentional: A and D both store LONG with opposite outputs.');
 update();
}
function testABBA(){
 const x=abba(S.eta);
 $('controlResult').textContent='Matched AB vs BA (same LONG key, targets LEFT and RIGHT): Hebbian material distance '+
  x.hebb.toExponential(2)+'; delta material distance '+x.delta.toFixed(3)+
  '. Delta AB echo ['+x.deltaAB.map(nfmt).join(', ')+'], BA ['+
  x.deltaBA.map(nfmt).join(', ')+']. The old additive write commutes; the corrective write does not.';
}
$('teach').addEventListener('click',teachClick);
$('ping').addEventListener('click',pingClick);
$('demo').addEventListener('click',demo);
$('control').addEventListener('click',testABBA);
$('clear').addEventListener('click',()=>{S.nodes=Array.from({length:COUNT},beach);S.learned=0;
 S.lastQuery=null;S.logs=[];log('MATERIAL RESET · all wave and sand states cleared.');update()});
$('source').addEventListener('change',e=>select(+e.target.value));
$('band').addEventListener('change',e=>{S.band=+e.target.value;S.lastQuery=null;update()});
$('value').addEventListener('change',e=>{S.value=+e.target.value;update()});
$('method').addEventListener('change',e=>{S.method=e.target.value;update()});
$('links').addEventListener('change',e=>{S.links=e.target.checked;update()});
$('attention').addEventListener('change',e=>{S.attention=e.target.checked;update()});
$('relay').addEventListener('change',e=>{S.relay=e.target.checked;update()});
$('eta').addEventListener('input',e=>{S.eta=+e.target.value;update()});
for(let i=0;i<COUNT;i++)$('beach'+i).addEventListener('click',()=>select(i));
function tick(){
 // Numerical wave propagation is real and independent of slow h changes
 // until a strong teaching call updates the stored sand coefficients.
 for(let i=0;i<2;i++)frame(S);
 for(let i=0;i<COUNT;i++)drawNode(i);
 requestAnimationFrame(tick);
}
log('READY · strong swells write Fourier sand; weak pings only read. Try LOAD LESSONS.');
update();tick();
window.__beachAiDiagnostics=()=>({state:S,query:query(S,S.selected,S.band),
 lessons:S.learned,material:materialSignature(S),control:abba(S.eta)});
})();