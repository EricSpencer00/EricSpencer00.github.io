import test from 'node:test';import assert from 'node:assert/strict';import fs from 'node:fs';
import {search} from '../palindrome-v3/editable-search.mjs';import {exact,normalize} from '../palindrome-v3/engine.mjs';
const manifest=JSON.parse(fs.readFileSync(new URL('../palindrome-v3/compiled-windows.json',import.meta.url)));
const run=opts=>search({minLetters:1,...opts},()=>{},null,manifest);
test('held-out outputs arise without complete control injection and preserve retained context',async()=>{
 const r=await run({seedId:'suss'});assert.equal(r.receipt.status,'complete');assert.equal(r.receipt.control_injection,false);assert.equal(r.candidates.length,2);
 for(const c of r.candidates){assert.ok(exact(c.text));assert.ok(!exact(c.window));assert.ok(!manifest.corpus.examples.some(x=>normalize(x.text)===c.tape));assert.ok(c.text.startsWith(c.retained_prefix));assert.ok(c.text.endsWith(c.retained_suffix));assert.deepEqual(c.seam_debt,{side:'left',letters:'s'});assert.equal(c.human_label,null);assert.ok(c.trace.some(s=>s.source?.includes('np:ward')||s.source?.includes('np:mock')));assert.ok(c.trace.some(s=>s.source?.includes('genitive')));}
});
test('selection constrains actual retained text; imported controls require explicit inclusion',async()=>{
 for(const seedId of ['tap','ward','mock']){const r=await run({seedId});assert.equal(r.candidates.length,0);const controls=await run({seedId,includeControls:true});assert.ok(controls.candidates.length);for(const c of controls.candidates)assert.ok(c.imported_control);}
 assert.notDeepEqual(manifest.plans[0].chunks,manifest.plans[1].chunks);assert.notDeepEqual(manifest.plans[2].chunks,manifest.plans[3].chunks);
});
test('constituent grouping changes operational debt requirement, not valid language',async()=>{
 const split=await run({seedId:'suss',maxDebt:1});assert.equal(split.candidates.length,0);
 const grouped=await run({seedId:'suss',maxDebt:1,grouping:'constituent'});assert.equal(grouped.candidates.length,2);
 const wider=await run({seedId:'suss',maxDebt:8});assert.deepEqual(grouped.candidates.map(x=>x.id),wider.candidates.map(x=>x.id));
});
test('source spans, interfaces and compiler parity remain auditable',()=>{
 const rows=Object.fromEntries(manifest.corpus.examples.map(x=>[x.id,x]));for(const f of manifest.fragments){const original=rows[f.source].text.slice(f.start,f.end);assert.equal(original,f.original);assert.equal(f.text,(f.case_transform==='lower'?original.toLowerCase():original)+(f.separator_after?' ':''));}
 assert.ok(manifest.compiler_parity.every(p=>p.identical_to_existing_research_compiler));for(const p of manifest.plans)assert.equal(p.seed_text,p.prefix+p.original_window+p.suffix);
});
test('finite grammar path oracle agrees with all exact closed outputs at debt eight',async()=>{
 for(const plan of manifest.plans){const paths=[];const visit=(state,text,depth)=>{assert.ok(depth<13);if(state==='END'){paths.push(text);return;}for(const c of plan.chunks)if(c.entry===state)visit(c.exit,text+c.text,depth+1);};visit('START','',0);if(plan.allow_empty)paths.push('');
 const oracle=new Set(paths.filter(core=>!normalize(core)||exact(core)).map(core=>normalize(plan.prefix+core.slice(plan.left_residual.length,plan.right_residual.length?-plan.right_residual.length:undefined)+plan.suffix)));
 const r=await run({seedId:plan.seed_id,maxDebt:8,includeControls:true});assert.equal(r.receipt.status,'complete');assert.deepEqual(new Set(r.candidates.map(c=>c.id)),oracle);}
});
test('cancellation and bad settings cannot publish output',async()=>{
 const c=new AbortController();c.abort();await assert.rejects(search({},()=>{},c.signal,manifest),{name:'AbortError'});await assert.rejects(run({seedId:'missing'}));await assert.rejects(run({maxDebt:9}));
});
