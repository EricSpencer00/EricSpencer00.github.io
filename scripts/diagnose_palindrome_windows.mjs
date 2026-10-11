import fs from 'node:fs';import crypto from 'node:crypto';import {search} from '../palindrome-v3/editable-search.mjs';import {search as baseline,exact} from '../palindrome-v3/engine.mjs';
const m=JSON.parse(fs.readFileSync(new URL('../palindrome-v3/compiled-windows.json',import.meta.url))),runs=[];
const hash=s=>crypto.createHash('sha256').update(s).digest('hex');
for(const seedId of ['tap','suss','ward','mock'])for(const grouping of ['split','constituent'])for(const maxDebt of [1,4,8]){
 const r=await search({seedId,grouping,maxDebt,minLetters:1,includeControls:true},()=>{},null,m);
 const ordered=r.candidates.slice().sort((a,b)=>hash('window-sample-20261011'+a.id).localeCompare(hash('window-sample-20261011'+b.id)));
 const sample=ordered.slice(0,Math.ceil(ordered.length*.1)).map(x=>({id:x.id,text:x.text,grammar:'grammatical in declared frame',readability:x.imported_control?'prior positive human label':'self-review: readable; possessive institutional owner needs human review',coherence:x.imported_control?'not newly rated':'self-review: possible ward food ownership; conditional relation to memos weak',repetition:x.repetition_cost,provenance:x.provenance,human_label:x.human_label,reviewer:'sole-owner qualitative self-review; not independent model/human scoring'}));
 runs.push({seedId,grouping,maxDebt,...r,sample});
}
const b=[];for(const seedId of ['tap','suss','ward','mock'])b.push(await baseline({seedId,minLetters:1,maxDebt:4}));
const occurrences=runs.reduce((n,r)=>n+r.candidates.length,0),sampled=runs.reduce((n,r)=>n+r.sample.length,0);
if(!runs.every(r=>r.candidates.every(c=>exact(c.text))))throw new Error('Exactness failed');
const proposals=[];for(const plan of m.plans){const visit=(state,core,trace)=>{if(state==='END'){const window=core.slice(plan.left_residual.length,plan.right_residual.length?-plan.right_residual.length:undefined);const text=plan.prefix+window+plan.suffix;proposals.push({seed:plan.seed_id,text,window,trace,exact:exact(text),outcome:exact(text)?'exact proposal; availability depends on debt grouping':'rejected letter mismatch'});return;}for(const c of plan.chunks)if(c.entry===state)visit(c.exit,core+c.text,[...trace,c.id]);};visit('START','',[]);if(plan.allow_empty)proposals.push({seed:plan.seed_id,text:plan.seed_text,window:'',trace:[],exact:exact(plan.seed_text),outcome:'licensed empty insertion control'});}
const result={proposals,resource_policy:'CPU-only; deterministic finite grammar; 24 declared strata; per request 3000 states/12 chunks/150ms/32 closures; seed window-sample-20261011; no paid inference',rounding:'ceil(10% of each stratum output occurrence population), then sum; duplicates retained across strata',occurrences,sampled,percent:100*sampled/occurrences,all_exact:true,runs,baseline:b};
fs.writeFileSync(process.argv[2]||'/tmp/palindrome-windows-diagnostic.json',JSON.stringify(result,null,2)+'\n');console.log({occurrences,sampled,percent:result.percent});
