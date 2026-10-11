import {normalize,exact,anchors,extend,repetitionCost} from './engine.mjs';
let manifestPromise;
export async function loadManifest() {
  return manifestPromise ??= fetch(new URL('./compiled-windows.json',import.meta.url)).then(r=>{if(!r.ok)throw new Error('Phrase inventory unavailable.');return r.json();});
}
export async function search(options={},emit=()=>{},signal,manifest) {
  manifest ??= await loadManifest();
  const source=manifest.plans.find(p=>p.seed_id===(options.seedId||'suss'));
  if(!source)throw new Error('Choose a listed seed.');
  const maxDebt=options.maxDebt??4,minLetters=options.minLetters??normalize(source.seed_text).length+1;
  if(!Number.isInteger(maxDebt)||maxDebt<0||maxDebt>8)throw new Error('Overhang must be between zero and eight letters.');
  if(!Number.isInteger(minLetters)||minLetters<1||minLetters>200)throw new Error('Minimum length must be between 1 and 200.');
  const required=(options.required||'').trim().toLowerCase();
  if(required.length>40||!/^[a-z\s]*$/.test(required))throw new Error('Use up to 40 letters and spaces for required words.');
  if(options.exclude&&(!Array.isArray(options.exclude)||options.exclude.length>100||options.exclude.some(x=>typeof x!=='string'||x.length>200)))throw new Error('Invalid previous-result list.');
  if(options.ranking&&!['shorter','longer','repetition'].includes(options.ranking))throw new Error('Unknown ranking.');
  const plan={...source,chunks:(options.grouping==='constituent'?source.grouped_chunks:source.chunks).map(c=>({...c,bindings:Object.fromEntries(c.bindings)}))};
  const start=performance.now(),queue=anchors(plan,maxDebt),seen=new Set(),closed=new Map();
  if(plan.allow_empty)queue.push({left:'',right:'',ls:'START',rs:'END',bindings:{},steps:0,debt:{side:'none',letters:''},center:'',anchorLeft:'',anchorRight:'',trace:[{kind:'empty-window',phrase:'',role:'licensed zero-width insertion'}]});
  const bounds={states:3000,depth:12,searchMs:150,outputs:32},failures={letter_mismatch:0,debt_cap:0,argument_conflict:0,depth_cap:0};
  let cursor=0,visited=0,duplicates=0,status='complete';const initialSeeds=queue.length;
  for(const s of queue){const c=plan.chunks.find(c=>c.text===s.center);if(c)s.trace[0].source=c.source;}
  emit({type:'status',phase:'searching',message:'Matching the selected editable window…'});
  while(cursor<queue.length){
    if(signal?.aborted)throw new DOMException('Search cancelled','AbortError');
    if(visited>=bounds.states||performance.now()-start>bounds.searchMs){status='bounded';break;}
    const s=queue[cursor++];visited++;
    const key=JSON.stringify([s.left,s.right,s.ls,s.rs,s.center,s.anchorLeft,s.anchorRight,s.bindings]);
    if(seen.has(key)){duplicates++;continue;}seen.add(key);
    if(s.ls==='START'&&s.rs==='END'&&!s.debt.letters){
      const core=s.left+s.center+s.right;
      if(!core.startsWith(plan.left_residual)||!core.endsWith(plan.right_residual))throw new Error('Retained seam residual failed.');
      const window=core.slice(plan.left_residual.length,plan.right_residual.length?-plan.right_residual.length:undefined);
      const text=plan.prefix+window+plan.suffix,tape=normalize(text);
      if(!exact(text))throw new Error('Exactness validation failed.');
      const imported=manifest.corpus.examples.find(r=>normalize(r.text)===tape);
      if(!closed.has(tape))closed.set(tape,{id:tape,text,tape,letters:tape.length,words:(text.match(/[a-z]+/gi)||[]).length,
        window,retained_prefix:plan.prefix,retained_suffix:plan.suffix,seam_debt:plan.seam_debt,
        seed_control:tape===normalize(plan.seed_text),human_label:imported?'positive':null,
        provenance:imported?'runtime reconstruction matching imported human-liked control':'corpus-fragment recombination; human review pending',
        repetition_cost:repetitionCost(text),trace:s.trace,bindings:s.bindings,imported_control:!!imported});
      if(closed.size>=bounds.outputs){status='bounded';break;}
    }
    if(s.steps>=bounds.depth){failures.depth_cap++;continue;}
    const sides=s.debt.side==='left'?['right']:s.debt.side==='right'?['left']:['left','right'];
    for(const side of sides)for(const c of plan.chunks){
      if((side==='left'?c.exit:c.entry)!==(side==='left'?s.ls:s.rs))continue;
      const next=extend(s,c,side,maxDebt);
      if(next.error)failures[next.error]++;
      else{next.trace[next.trace.length-1].source=c.source;queue.push(next);}
    }
    if(visited%24===0){emit({type:'progress',visited,closed:closed.size});await new Promise(r=>setTimeout(r,0));}
  }
  const all=[...closed.values()],exclude=new Set(options.exclude||[]),words=required.split(/\s+/).filter(Boolean);
  const candidates=all.filter(r=>(options.includeControls||!r.imported_control)&&r.letters>=minLetters&&!exclude.has(r.id)&&words.every(w=>(r.text.toLowerCase().match(/[a-z]+/g)||[]).includes(w)));
  candidates.sort((a,b)=>(options.ranking==='longer'?b.letters-a.letters:options.ranking==='repetition'?a.repetition_cost-b.repetition_cost:a.letters-b.letters)||a.id.localeCompare(b.id));
  if(signal?.aborted)throw new DOMException('Search cancelled','AbortError');
  return {version:3,method:'corpus-derived typed editable window',seed:plan.seed_text,candidates,
    receipt:{status,visited,initialSeeds,pending:queue.length-cursor,closed:closed.size,duplicates,failures,bounds,search_ms:performance.now()-start,maxDebt,
      corpus_unseen:all.filter(r=>!r.imported_control).length,imported_controls:all.filter(r=>r.imported_control).length,
      grouping:options.grouping||'split',window_type:plan.window_type,seam_debt:plan.seam_debt,ranking:options.ranking||'shorter',control_injection:false}};
}
