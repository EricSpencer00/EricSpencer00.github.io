import {SEEDS,normalize} from './engine.mjs';
import {SearchClient} from './client.mjs';
const $=id=>document.getElementById(id);
const form=$('settings'),seedSelect=$('seed');let current=null,history=[],started=0;
for (const seed of SEEDS) {const option=document.createElement('option');option.value=seed.id;option.textContent=seed.id==='tap'?'Editors tap Pat’s roti':seed.id==='suss'?'Editors suss roti':seed.id==='ward'?'Draw a ward':'Draw a mock coma ward';seedSelect.append(option);}
function busy(value) {$('cancel').hidden=!value;$('generate').textContent=value?'Search again':'Expand next';$('generate').setAttribute('aria-busy',String(value));}
function seedChanged() {
  const seed=SEEDS.find(s=>s.id===seedSelect.value);$('seed-text').textContent=seed.text;
  $('min-letters').value=normalize(seed.text).length+1;$('length-hint').textContent=`seed: ${normalize(seed.text).length}`;
  history=[];current=null;$('result').hidden=true;$('empty').hidden=false;
}
function text(id,value) {$(id).textContent=value;}
function show(row,receipt) {
  current=row;history.push(row.id);if(history.length>100)history.shift();
  $('result').hidden=false;$('empty').hidden=true;
  text('sentence',row.text);text('provenance',row.seed_control?'Human-liked seed control':row.human_label?'Phrase composition matching human-liked wording':'New phrase composition; human review pending');
  text('letters',`${row.letters} letters, ${row.words} words`);text('timing',`${Math.round(performance.now()-started)} ms response`);
  const tape=$('tape');tape.replaceChildren();for(let i=0;i<row.tape.length;i++) {const span=document.createElement('span');span.textContent=row.tape[i];if(i===Math.floor(row.tape.length/2)||i===Math.ceil(row.tape.length/2)-1)span.className='center';tape.append(span);}
  text('method-note',`${receipt.visited} states searched in ${receipt.search_ms.toFixed(1)} ms. Phrases follow a finite grammar; ranking favors known reader preferences and uses a soft repetition cost. New wording has not been rated by a human.`);
  const list=$('steps');list.replaceChildren();for(const step of row.trace) {const li=document.createElement('li');
    li.textContent=step.kind==='control'?'The original human-liked seed is a control.':step.kind==='anchor'?`Start inside “${step.phrase.trim()}”: ${step.debt.letters.length} letters waiting${step.debt.letters?` (${step.debt.letters})`:''}.`:`${step.side==='left'?'Prepend':'Append'} “${step.phrase.trim()}”: repay ${step.payoff.paid} of ${step.payoff.added} added letters; ${step.payoff.debt_after} letters still waiting.`;list.append(li);}
  text('copy-status','');text('feedback-status','Feedback stays in this browser.');
  document.querySelectorAll('[data-rating]').forEach(b=>b.setAttribute('aria-pressed','false'));
  text('status',receipt.status==='complete'?'Search complete. Every letter matches.':'Search reached its limit. This result still matches exactly.');
  if(matchMedia('(max-width:760px)').matches)$('output').scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion:reduce)').matches?'auto':'smooth'});
}
const client=new SearchClient(event=>{
  if (event.type==='status') {busy(true);text('status',event.message);}
  if (event.type==='progress') text('status',`Searching phrases… ${event.visited} states checked.`);
  if (event.type==='result') {
    busy(false);const row=event.result.candidates[0];
    if(row)show(row,event.result.receipt);else {
      current=null;$('result').hidden=true;$('empty').hidden=false;
      text('status',event.result.receipt.status==='complete'?'No unseen expansion matches these settings. Lower the minimum, remove required words, change the seed, or show previous results again.':'The search limit was reached without a match. Try fewer required words or a shorter minimum.');
    }
  }
  if(event.type==='error'||event.type==='cancelled') {busy(false);text('status',event.message);}
});
form.addEventListener('submit',event=>{event.preventDefault();if(!form.reportValidity())return;
  started=performance.now();client.request({seedId:seedSelect.value,maxDebt:Number($('overhang').value),minLetters:Number($('min-letters').value),required:$('required').value,exclude:history});
});
$('cancel').addEventListener('click',()=>client.cancel());
$('next').addEventListener('click',()=>form.requestSubmit());
form.addEventListener('input',event=>{client.cancel(false);busy(false);text('debt-value',$('overhang').value);
  if(event.target===seedSelect)seedChanged();
  else {current=null;$('result').hidden=true;$('empty').hidden=false;}
  text('status','Settings changed. Expand next to search again.');
});
$('reset').addEventListener('click',()=>{client.cancel(false);busy(false);history=[];text('status','Previous results cleared. Expand next to search again.');});
$('copy').addEventListener('click',async()=>{if(!current)return;try{await navigator.clipboard.writeText(current.text);text('copy-status','Copied.');}catch{text('copy-status','Select the sentence to copy it.');}});
document.querySelectorAll('[data-rating]').forEach(button=>button.addEventListener('click',()=>{
  if(!current)return;
  try {const saved=JSON.parse(localStorage.getItem('palindrome-v3-feedback')||'[]');const rows=Array.isArray(saved)?saved:[];
    rows.push({id:current.id,text:current.text,rating:button.dataset.rating,date:new Date().toISOString(),origin:current.provenance});
    localStorage.setItem('palindrome-v3-feedback',JSON.stringify(rows.slice(-100)));
    text('feedback-status','Saved in this browser.');
  }catch{text('feedback-status','Browser storage is unavailable. Feedback was not saved.');}
  document.querySelectorAll('[data-rating]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
}));
seedChanged();
