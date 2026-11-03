import {test} from 'node:test';
import assert from 'node:assert/strict';
import {SEEDS,search,normalize,exact} from '../palindrome-v3/engine.mjs';
import {SearchClient} from '../palindrome-v3/client.mjs';

test('all listed accepted seeds are exact and their exposed core is exact',()=>{
  for(const seed of SEEDS) {assert(exact(seed.text));assert(exact(seed.core));}
});
test('whole-phrase search equals independent full finite grammar oracle',async()=>{
  const candidates=['Some men, if editors suss roti, define memos.'];
  const owners=["Pat's","pots'","pits'","wards'"];
  for(const verb of ['tap','top','tip','draw']) for(const owner of owners)
    candidates.push(`Some men, if editors ${verb} ${owner} roti, define memos.`);
  for(const adv of ['now','gently','softly','carefully','slowly','lightly','twice','once','here','there','today'])
    for(const prep of ['on','at']) for(const owner of owners)
      candidates.push(`Some men, if editors tap ${adv} ${prep} ${owner} roti, define memos.`);
  assert.equal(candidates.length,105);
  const expected=candidates.filter(exact).map(normalize).sort();assert.equal(expected.length,6);
  const result=await search({seedId:'tap',minLetters:1,maxDebt:4});
  assert.deepEqual(result.candidates.map(r=>r.tape).sort(),expected);
  assert.equal(result.receipt.status,'complete');assert.equal(result.receipt.pending,0);
  for(const row of result.candidates) {
    assert(exact(row.text));assert.equal(normalize(row.text),row.tape);
    assert.equal(row.human_label,SEEDS.some(s=>normalize(s.text)===row.tape)?'positive':null);
    assert.equal(row.repetition_cost,0);
  }
});
test('light debt crosses now/on grammar boundary; zero cap remains explicit control',async()=>{
  const zero=await search({seedId:'tap',minLetters:1,maxDebt:0});
  assert.deepEqual(zero.candidates.map(x=>x.text),[SEEDS[0].text,SEEDS[1].text]);
  const light=await search({seedId:'tap',minLetters:39,maxDebt:4,required:'now'});
  assert.equal(light.candidates.length,1);const row=light.candidates[0];assert.equal(row.letters,43);
  assert.equal(row.trace[0].phrase,'now ');assert.equal(row.trace[0].debt.letters,'on');
  assert(row.trace.some(s=>s.payoff?.paid===2&&s.payoff.debt_after===0));
  assert(row.trace.some(s=>s.payoff?.paid===3&&s.payoff.debt_after===0));
  assert.equal(row.human_label,null);
});
test('partial-word drawing seam closes coma without letter-changing repair',async()=>{
  const result=await search({seedId:'ward',minLetters:20,maxDebt:4});
  assert.deepEqual(result.candidates.map(r=>r.text),[SEEDS[3].text]);
  assert.equal(result.candidates[0].seed_control,false);
  assert.equal(result.candidates[0].human_label,'positive');
  assert(result.candidates[0].trace.some(s=>s.phrase==='com'));
});
test('constraints and history produce genuine empty results, never fallback',async()=>{
  const r=await search({seedId:'tap',minLetters:39});
  assert.equal((await search({seedId:'tap',minLetters:39,exclude:r.candidates.map(x=>x.id)})).candidates.length,0);
  assert.equal((await search({seedId:'tap',required:'elephant'})).candidates.length,0);
  assert.equal((await search({seedId:'tap',minLetters:200})).candidates.length,0);
  await assert.rejects(search({maxDebt:100}));await assert.rejects(search({required:'<script>'}));
});
test('cooperative abort stops worker search',async()=>{
  const controller=new AbortController();
  await assert.rejects(search({},e=>{if(e.type==='progress')controller.abort();},controller.signal),{name:'AbortError'});
});
test('client cancellation and racing responses cannot overwrite the latest result',()=>{
  const workers=[],events=[];
  const factory=()=>{const worker={postMessage(m){this.message=m;},terminate(){this.terminated=true;}};workers.push(worker);return worker;};
  const client=new SearchClient(e=>events.push(e),factory);
  const old=client.request({});const staleHandler=workers[0].onmessage;
  const latest=client.request({});assert.equal(workers[0].terminated,true);
  staleHandler({data:{id:old,type:'result',result:{candidates:[]}}});assert.equal(client.active,latest);
  const valid={text:SEEDS[0].text,tape:normalize(SEEDS[0].text)};
  workers[1].onmessage({data:{id:latest,type:'result',result:{candidates:[valid]}}});assert.equal(client.active,null);
  const results=events.filter(x=>x.type==='result');assert.equal(results.length,1);
  const id=client.request({});client.cancel();workers.at(-1).onmessage({data:{id,type:'result',result:{candidates:[valid]}}});
  assert.equal(events.filter(x=>x.type==='result').length,1);
});
test('client rejects a broken palindrome before display and handles worker error',()=>{
  let worker;const events=[];const client=new SearchClient(e=>events.push(e),()=>worker={postMessage(){},terminate(){}});
  const id=client.request({});worker.onmessage({data:{id,type:'result',result:{candidates:[{text:'not exact',tape:'notexact'}]}}});
  assert.equal(events.at(-1).type,'error');assert.equal(client.active,null);
  client.request({});worker.onerror();assert.equal(events.at(-1).type,'error');assert.equal(client.worker,null);
});
