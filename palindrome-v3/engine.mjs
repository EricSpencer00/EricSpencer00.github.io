/* Request-time typed phrase search. Port of bilateral_seams.py and experiment
 * 027: whole phrase anchors, center-out debt, grammar/argument closure.
 * No sentence-bank sampling, language model, or unbounded workload. */
export const normalize = text => text.toLowerCase().replace(/[^a-z]/g, '');
const reverse = text => [...text].reverse().join('');
export const exact = text => {
  const tape = normalize(text);
  if (!tape) return false;
  for (let i = 0; i < tape.length / 2; i++) if (tape[i] !== tape[tape.length - 1 - i]) return false;
  return true;
};
export const SEEDS = Object.freeze([
  {id:'tap', family:'condition', text:"Some men, if editors tap Pat's roti, define memos.", core:'tap Pat', label:'Human liked', date:'2026-10-11'},
  {id:'suss', family:'condition', text:'Some men, if editors suss roti, define memos.', core:'sus', label:'Human liked', date:'2026-10-11'},
  {id:'ward', family:'drawing', text:'Draw a ward. I draw a ward.', core:'ward. I draw', label:'Human liked', date:'2026-10-11'},
  {id:'mock', family:'drawing', text:'Draw a mock coma ward. I draw a mock coma ward.', core:'mock coma ward. I draw a mock com', label:'Human liked', date:'2026-10-11'},
]);
const adverbs = ['now','gently','softly','carefully','slowly','lightly','twice','once','here','there','today'];

function chunk(id, text, entry, exit, role, bindings = {}) {
  return {id,text,entry,exit,role,bindings};
}
export function compile(family) {
  let chunks, prefix, suffix;
  if (family === 'condition') {
    const bindings = {subject:'editors1', food:'roti1', main:'men1', document:'memos1'};
    const c = (id,text,entry,exit,role,extra={}) => chunk(id,text,entry,exit,role,{...bindings,...extra});
    chunks = [c('suss','sus','START','END','verb completed as suss by right seam')];
    for (const verb of ['tap','top','tip','draw']) {
      chunks.push(c(`${verb}:direct`,verb+' ','START','OWNER','transitive handling/depiction verb'));
      // Only tap is licensed for the contact-target PP arm.
      if (verb === 'tap') chunks.push(c('tap:pp','tap ','START','ADV','contact verb with target PP'));
    }
    for (const [root,owner] of [['Pat','Pat1'],['pot','pots1'],['pit','pits1'],['ward','wards1']])
      chunks.push(c('owner:'+root,root,'OWNER','END','possessor root; plural/possessive completed at right seam',{owner}));
    for (const word of adverbs) chunks.push(c('adv:'+word,word+' ','ADV','PREP','manner/time adverb'));
    for (const word of ['on','at']) chunks.push(c('prep:'+word,word+' ','PREP','OWNER','contact-target preposition'));
    prefix='Some men, if editors '; suffix='s roti, define memos.';
  } else if (family === 'drawing') {
    const bindings = {agent:'speaker1',object:'ward1',action:'draw'};
    const c = (id,text,entry,exit,role) => chunk(id,text,entry,exit,role,bindings);
    chunks = [c('ward','ward. ','START','CENTER','imperative object'),
      c('I','I ','CENTER','VERB','speaker subject'),c('draw','draw','VERB','END','first-person verb'),
      c('mock:left','mock ','START','COMA','object modifier'),c('coma:left','coma ','COMA','WARD','drawing subject modifier'),
      c('ward:modified','ward. ','WARD','CENTER2','imperative object'),c('I:modified','I ','CENTER2','VERB2','speaker subject'),
      c('draw:modified','draw ','VERB2','DET','first-person verb'),c('a','a ','DET','MOCK','object determiner'),
      c('mock:right','mock ','MOCK','COMA2','object modifier'),c('coma:right','com','COMA2','END','partial coma; final a completed by fixed right seam')];
    prefix='Draw a ';suffix=' a ward.';
  } else throw new Error('Unknown phrase family.');
  // Compiler gates: finite, unique IDs, licensed interfaces, no empty arcs.
  if (chunks.length > 32 || new Set(chunks.map(c=>c.id)).size !== chunks.length || chunks.some(c=>!normalize(c.text)))
    throw new Error('Invalid phrase inventory.');
  return {family,chunks,prefix,suffix};
}

function debt(left, right) {
  const k = Math.min(left.length,right.length);
  for (let i=0;i<k;i++) if (left[i]!==right[i]) return null;
  return {side:left.length>right.length?'left':right.length>left.length?'right':'none', letters:left.length>right.length?left.slice(k):right.slice(k)};
}
export function repetitionCost(text) {
  const words=text.toLowerCase().match(/[a-z]+/g)||[];let cost=0;
  for (const n of [1,2,3,4]) {
    const counts=new Map();
    for (let i=0;i<=words.length-n;i++) {const k=words.slice(i,i+n).join(' ');counts.set(k,(counts.get(k)||0)+1);}
    for (const count of counts.values()) cost+=(count-1)*(n===1?1:0.5);
  }
  return cost;
}
function render(plan, core) {
  let text=plan.prefix+core+plan.suffix;
  if (plan.family==='drawing' && core.endsWith('com')) text=plan.prefix+core+'a ward.';
  if (plan.family==='condition' && core!=='sus') text=text.replace(/(Pat)s roti/,"$1's roti").replace(/(pot|pit|ward)s roti/,"$1s' roti");
  return text;
}
function anchors(plan, maxDebt) {
  const result=[];
  for (const c of plan.chunks) {
    const tape=normalize(c.text);
    for (const width of [0,1]) for (let split=0;split<=tape.length-width;split++) {
      const anchorLeft=tape.slice(0,split),anchorRight=tape.slice(split+width);
      const d=debt(reverse(anchorLeft),anchorRight);
      if (!d || d.letters.length>maxDebt) continue;
      result.push({left:'',right:'',ls:c.entry,rs:c.exit,bindings:{...c.bindings},steps:1,debt:d,
        center:c.text,anchorLeft,anchorRight,trace:[{kind:'anchor',phrase:c.text,role:c.role,offset:[split,width],debt:{...d}}]});
    }
  }
  return result;
}
function extend(s,c,side,maxDebt) {
  const bindings={...s.bindings};
  for (const [key,value] of Object.entries(c.bindings)) {
    if (bindings[key] && bindings[key]!==value) return {error:'argument_conflict'};
    bindings[key]=value;
  }
  const left=side==='left'?c.text+s.left:s.left,right=side==='right'?s.right+c.text:s.right;
  const d=debt(reverse(normalize(left)+s.anchorLeft),s.anchorRight+normalize(right));
  if (!d) return {error:'letter_mismatch'};
  if (d.letters.length>maxDebt) return {error:'debt_cap'};
  const added=normalize(c.text).length,paid=s.debt.side!=='none'&&s.debt.side!==side?Math.min(added,s.debt.letters.length):0;
  return {left,right,ls:side==='left'?c.entry:s.ls,rs:side==='right'?c.exit:s.rs,bindings,
    steps:s.steps+1,debt:d,center:s.center,anchorLeft:s.anchorLeft,anchorRight:s.anchorRight,
    trace:[...s.trace,{kind:'extension',side,phrase:c.text,role:c.role,grammar_before:[s.ls,s.rs],grammar_after:[side==='left'?c.entry:s.ls,side==='right'?c.exit:s.rs],debt:{...d},payoff:{paid,added,ratio:paid/added,debt_before:s.debt.letters.length,debt_after:d.letters.length}}]};
}

function optionsChecked(options) {
  const seed=SEEDS.find(s=>s.id===(options.seedId||'tap'));
  if (!seed) throw new Error('Choose a listed seed.');
  const maxDebt=options.maxDebt??4,minLetters=options.minLetters??normalize(seed.text).length+1;
  if (![0,1,2,3,4,5,6,7,8].includes(maxDebt)) throw new Error('Overhang must be between zero and eight letters.');
  if (!Number.isInteger(minLetters)||minLetters<1||minLetters>200) throw new Error('Minimum length must be between 1 and 200.');
  const required=(options.required||'').trim().toLowerCase();
  if (required.length>40||!/^[a-z\s]*$/.test(required)) throw new Error('Use up to 40 letters and spaces for required words.');
  if (options.exclude && (!Array.isArray(options.exclude)||options.exclude.length>100||options.exclude.some(x=>typeof x!=='string'||x.length>200))) throw new Error('Invalid previous-result list.');
  return {seed,maxDebt,minLetters,required:required.split(/\s+/).filter(Boolean),exclude:new Set(options.exclude||[])};
}

export async function search(options={},emit=()=>{},signal) {
  const {seed,maxDebt,minLetters,required,exclude}=optionsChecked(options),plan=compile(seed.family);
  const start=performance.now(),queue=anchors(plan,maxDebt),seen=new Set(),closed=new Map();
  // Explicit accepted full-center control is preserved as control, never new output.
  if (exact(seed.core)) queue.unshift({left:'',right:'',ls:'START',rs:'END',bindings:{},steps:1,
    debt:{side:'none',letters:''},center:seed.core,anchorLeft:'',anchorRight:'',trace:[{kind:'control',phrase:seed.core}]});
  const bounds={states:3000,depth:12,searchMs:150,outputs:32};let visited=0,cursor=0,status='complete',duplicates=0;
  const failures={letter_mismatch:0,debt_cap:0,argument_conflict:0},initialSeeds=queue.length;
  emit({type:'status',phase:'searching',message:'Matching phrases around the center…'});
  while (cursor<queue.length) {
    if (signal?.aborted) throw new DOMException('Search cancelled','AbortError');
    if (visited>=bounds.states||performance.now()-start>bounds.searchMs) {status='bounded';break;}
    const s=queue[cursor++];visited++;
    const key=JSON.stringify([s.left,s.right,s.ls,s.rs,s.center,s.anchorLeft,s.anchorRight,s.bindings]);
    if (seen.has(key)) {duplicates++;continue;}seen.add(key);
    if (s.ls==='START'&&s.rs==='END'&&!s.debt.letters) {
      const core=s.left+s.center+s.right,text=render(plan,core),tape=normalize(text);
      if (!exact(text)) throw new Error('Exactness validation failed.');
      const approved=SEEDS.find(x=>normalize(x.text)===tape),control=tape===normalize(seed.text),cost=repetitionCost(text);
      // Ranking is a disclosed heuristic, not a human readability certificate.
      const rating=(approved?8:4)+(plan.family==='condition'&&/Pat/.test(text)?2:0)-cost*.15-(/pits/.test(text)?1:0)-(/now on/.test(text)?.25:0);
      if (!closed.has(tape)) closed.set(tape,{id:tape,text,tape,letters:tape.length,words:(text.match(/[a-z]+/gi)||[]).length,
        seed_control:control,human_label:approved?'positive':null,provenance:control?'accepted seed control':approved?'runtime phrase composition; matches human-liked example':'runtime phrase composition; human review pending',
        score:rating,repetition_cost:cost,trace:s.trace,bindings:s.bindings,family:seed.family});
      if (closed.size>=bounds.outputs) {status='bounded';break;}
    }
    if (s.steps>=bounds.depth) continue;
    const sides=s.debt.side==='left'?['right']:s.debt.side==='right'?['left']:['left','right'];
    for (const side of sides) for (const c of plan.chunks) {
      if ((side==='left'?c.exit:c.entry)!==(side==='left'?s.ls:s.rs)) continue;
      const next=extend(s,c,side,maxDebt);
      if (next.error) failures[next.error]++;else queue.push(next);
    }
    if (visited%24===0) {emit({type:'progress',visited,closed:closed.size});await new Promise(resolve=>setTimeout(resolve,0));}
  }
  const candidates=[...closed.values()].filter(r=>r.letters>=minLetters&&!exclude.has(r.id)&&required.every(w=>r.text.toLowerCase().match(/[a-z]+/g).includes(w))).sort((a,b)=>b.score-a.score||a.letters-b.letters||a.id.localeCompare(b.id));
  const receipt={status,visited,initialSeeds,pending:queue.length-cursor,closed:closed.size,duplicates,failures,bounds,search_ms:performance.now()-start,maxDebt,ranking:'grammar frame, known human preference, soft repetition cost; generated readability ungraded'};
  if (signal?.aborted) throw new DOMException('Search cancelled','AbortError');
  return {version:3,method:'seed-centered typed phrase expansion',seed:seed.text,candidates,receipt};
}
