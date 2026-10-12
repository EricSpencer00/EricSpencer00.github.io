"""030 finite layered word grammar and reverse-letter debt search.
Every full result is searched and verified. Long nested dialogues remain quality-unrated.
"""
from dataclasses import asdict
from collections import defaultdict,Counter
import random,time,hashlib,threading
from .composition_029 import NAMES,NOUNS,VERBS,OUTER as OUTER029
from .bilateral_seams import Chunk
from .validator import normalize,is_palindrome
OUTER={**OUTER029,'strap':('parts','parts','object omitted in question and clarified in answer'),'redraw':('warder','person','object omitted in question and clarified in answer')}
def grammar030(depth=1,names=NAMES,verbs=tuple(VERBS),outer=tuple(OUTER),actors=None,paragraph_break=False):
 if not 1<=depth<=40:raise ValueError('finite depth bound')
 out=[]
 def arc(a,b,text,role,bindings=()):
  out.append(Chunk('g'+str(len(out)),text,a,b,role,'independent word/role inventory030',tuple(bindings)))
 def q(i,start,end,last=False):
  p=f'q{i}:'
  arc(start,p+'NAME','Did ','past question auxiliary',(('scene','workshop task check'),))
  for name in (actors[i] if actors else names):arc(p+'NAME',p+'VP',name+' ','human question actor',((f'qactor{i}',name),))
  if last:
   for verb in verbs:
    for noun,kind,plural in NOUNS:
     if kind not in VERBS[verb]:continue
     state=p+'OBJ:'+verb+':'+noun
     arc(p+'VP',state,verb+' ','base transitive predicate',((f'predicate{i}',verb),(f'object_kind{i}',kind)))
     if not plural:
      arc(state,state+':N','a ','singular object determiner');state+=':N'
     arc(state,p+'ANSWER',noun+'? ','question object',((f'object{i}',noun),))
  else:
   for verb in outer:
    noun,kind,license=OUTER[verb]
    arc(p+'VP',end,verb+'? ','open task question: '+license,((f'predicate{i}',verb),(f'object{i}',noun),(f'object_kind{i}',kind),(f'outer_topic{i}',noun)))
   return
  for name in (actors[i] if actors else names):arc(p+'ANSWER',p+'DID',name+' ','elliptic answer actor',((f'answer_actor{i}',name),(f'qactor{i}',name)))
  arc(p+'DID',end,'did.','affirmative/anaphoric response to this question',((f'answer_task{i}',str(i)),))
 for i in range(depth):q(i,'START'if i==0 else f'OPEN:{i}',f'OPEN:{i+1}'if i<depth-1 else f'CLOSE:{i}',i==depth-1)
 for i in reversed(range(depth-1)):
  p=f'close{i}:'
  for verb in outer:
   noun,kind,license=OUTER[verb]
   arc(f'CLOSE:{i+1}',p+'ANSWER',('\n\n' if paragraph_break and i==depth-2 else ' ')+noun.capitalize()+'? ','echo clarification of open object',((f'predicate{i}',verb),(f'object{i}',noun),(f'object_kind{i}',kind),(f'outer_topic{i}',noun)))
  for name in (actors[i] if actors else names):arc(p+'ANSWER',p+'DID',name+' ','answer actor for clarified task',((f'answer_actor{i}',name),(f'qactor{i}',name)))
  arc(p+'DID','END'if i==0 else f'CLOSE:{i}','did.','elliptic response with clarified object',((f'answer_task{i}',str(i)),))
 # Ensure spacing between a completed inner answer and the next echo.
 # Echo arcs already supply the one space; deepest answer supplies none.
 if depth==1:
  out=[Chunk(c.id,c.text,c.entry,'END'if c.exit=='CLOSE:0'else c.exit,c.role,c.source,c.bindings)for c in out]
 unique={ (c.text,c.entry,c.exit,c.bindings):c for c in out};return tuple(unique.values())

class CharacterSearch:
 def __init__(self,chunks):
  self.chunks=tuple(chunks);self.out=defaultdict(list);self.inc=defaultdict(list);self.units={};self.meta={};self.li=defaultdict(lambda:defaultdict(list));self.ri=defaultdict(lambda:defaultdict(list))
  if len(chunks)>6000:raise ValueError('arc cap')
  for c in chunks:
   self.out[c.entry].append(c);self.inc[c.exit].append(c);self.units[c.id]=normalize(c.text);self.meta[c.id]=asdict(c);self.li[c.entry][self.units[c.id][0]].append(c);self.ri[c.exit][self.units[c.id][-1]].append(c)
  self.bounds={};self._local=threading.local()
  self.char_bounds={}
 def remaining(self,a,b):
  key=(a,b)
  if key in self.bounds:return self.bounds[key]
  if a==b:return (0,0)
  if not hasattr(self._local,'visiting'):self._local.visiting=set()
  if key in self._local.visiting:raise ValueError('cyclic grammar forbidden in030')
  self._local.visiting.add(key);ranges=[]
  for c in self.out[a]:
   x=self.remaining(c.exit,b)
   if x is not None:ranges.append((len(self.units[c.id])+x[0],len(self.units[c.id])+x[1]))
  self._local.visiting.remove(key);r=(min(x[0]for x in ranges),max(x[1]for x in ranges))if ranges else None;self.bounds[key]=r;return r
 def remaining_chars(self,a,b):
  key=(a,b)
  if key in self.char_bounds:return self.char_bounds[key]
  if a==b:return (0,0)
  if not hasattr(self._local,'char_visiting'):self._local.char_visiting=set()
  if key in self._local.char_visiting:raise ValueError('cyclic grammar')
  self._local.char_visiting.add(key);ranges=[]
  for c in self.out[a]:
   x=self.remaining_chars(c.exit,b)
   if x is not None:ranges.append((len(c.text)+x[0],len(c.text)+x[1]))
  self._local.char_visiting.remove(key)
  value=(min(x[0]for x in ranges),max(x[1]for x in ranges))if ranges else None
  self.char_bounds[key]=value;return value

 def search(self,*,low_chars=1,high_chars=1200,seed=0,low=1,high=10000,seconds=.15,max_states=3000,max_steps=24,max_outputs=32,audit=False,indexed=True,centre=None,exclude_id=None):
  start=time.perf_counter();rng=random.Random(seed);stack=[dict(left='',right='',ls='START',rs='END',side='none',debt='',matched=0,bindings={},ids=[],trace=[],steps=0,total=0)];seen=set();outputs={};failures=[];reasons=Counter();closed=[];visited=0;duplicates=0;proposals=0;status='complete';maximum_debt=0
  def reject(reason,s,c=None):
   reasons[reason]+=1
   if audit:failures.append({'reason':reason,'state':s['ls']+':'+s['rs'],'chunk':c.id if c else None,'side':s['side'],'debt':s['debt'],'ids':s['ids']})
  while stack:
   if visited>=max_states or time.perf_counter()-start>=seconds:status='resource_truncated';break
   s=stack.pop();visited+=1
   key=(s['ls'],s['rs'],s['left'],s['right'],tuple(sorted(s['bindings'].items())))
   if key in seen:duplicates+=1;continue
   seen.add(key);r=self.remaining(s['ls'],s['rs'])
   if r is None:reject('grammar_order',s);continue
   cr=self.remaining_chars(s['ls'],s['rs'])
   if cr is None or len(s['left'])+len(s['right'])+cr[0]>high_chars or len(s['left'])+len(s['right'])+cr[1]<low_chars:reject('displayed_length_bound',s);continue
   if s['total']+r[0]>high or s['total']+r[1]<low:reject('length_bound',s);continue
   if s['ls']==s['rs']and s['debt']==s['debt'][::-1]:
    text=s['left']+s['right'];t=normalize(text)
    assert is_palindrome(text)
    # Eligibility is inside the closure rule, before unique-output stopping.
    if low<=len(t)<=high and low_chars<=len(text)<=high_chars:
     if centre and ((len(t)-len(centre))%2 or len(t)<len(centre)or t[(len(t)-len(centre))//2:(len(t)+len(centre))//2]!=centre):reject('centre_constraint',s);continue
     tasks=[(v,s['bindings'].get('predicate'+k[6:]))for k,v in s['bindings'].items()if k.startswith('qactor')]
     identity='global-'+hashlib.sha256(t.encode()).hexdigest()[:16]
     if identity==exclude_id:reject('excluded_previous_result',s);continue
     if audit:closed.append({'text':text,'ids':s['ids'],'debt':s['debt']})
     if t not in outputs:outputs[t]={'id':'global-'+hashlib.sha256(t.encode()).hexdigest()[:16],'text':text,'letters':len(t),'bindings':s['bindings'],'trace':s['trace'],'family':'typed-dialogue','quality_unrated':True}
     if len(outputs)>=max_outputs:status='output_truncated';break
   if s['steps']>=max_steps:continue
   sides=['right']if s['side']=='left'else['left']if s['side']=='right'else['left','right'];rng.shuffle(sides);new=[]
   for side in sides:
    all_options=self.out[s['ls']]if side=='left'else self.inc[s['rs']]
    proposals+=len(all_options)
    if s['debt'] and indexed:
     options=list(self.li[s['ls']][s['debt'][0]]if side=='left'else self.ri[s['rs']][s['debt'][0]])
     excluded=len(all_options)-len(options);reasons['letter_mismatch']+=excluded
     if audit and excluded:
      allowed_ids={c.id for c in options};failures.append({'reason':'indexed_letter_mismatch','state':s['ls']+':'+s['rs'],'side':side,'debt':s['debt'],'candidate_ids':[c.id for c in all_options if c.id not in allowed_ids],'count':excluded,'ids':s['ids']})
    else:options=list(all_options)
    rng.shuffle(options)
    for c in options:
     b=dict(s['bindings'])
     if any(k in b and b[k]!=v for k,v in c.bindings):reject('argument_conflict',s,c);continue
     b.update(c.bindings)
     tasks=[(v,b['predicate'+k[6:]])for k,v in b.items()if k.startswith('qactor') and 'predicate'+k[6:] in b]
     unit=self.units[c.id]if side=='left'else self.units[c.id][::-1];old=s['debt'];matched=s['matched']
     if old:
      k=min(len(old),len(unit))
      if old[:k]!=unit[:k]:reject('letter_mismatch',s,c);continue
      matched+=k
      if len(old)>len(unit):debt=old[k:];dside=s['side']
      else:debt=unit[k:];dside=side if debt else'none'
     else:debt=unit;dside=side
     if len(debt)>8:reject('debt_cap',s,c);continue
     maximum_debt=max(maximum_debt,len(debt));n={'left':s['left']+c.text if side=='left'else s['left'],'right':c.text+s['right']if side=='right'else s['right'],'ls':c.exit if side=='left'else s['ls'],'rs':c.entry if side=='right'else s['rs'],'side':dside,'debt':debt,'matched':matched,'bindings':b,'ids':s['ids']+[c.id],'trace':s['trace']+[{'side':side,'chunk':self.meta[c.id],'debt_before':{'side':s['side'],'letters':old},'debt_after':{'side':dside,'letters':debt},'paid':min(len(old),len(unit))if old else 0}],'steps':s['steps']+1,'total':s['total']+len(unit)};new.append(n)
   rng.shuffle(new)
   # Retain repeats as possible continuations, but visit diverse task bindings first.
   def repetition(n):
    b=n['bindings'];tasks=[(v,b['predicate'+k[6:]])for k,v in b.items()if k.startswith('qactor')and 'predicate'+k[6:]in b]
    return len(tasks)-len(set(tasks))
   new.sort(key=repetition,reverse=True);stack.extend(new)
  return {'outputs':list(outputs.values()),'failures':failures,'closed_derivations':closed,'receipt':{'status':status,'seed':seed,'low':low,'high':high,'seconds_cap':seconds,'max_states':max_states,'max_steps':max_steps,'max_outputs':max_outputs,'states_visited':visited,'proposals':proposals,'duplicate_states':duplicates,'failure_counts':dict(reasons),'pending_states':len(stack),'max_debt_seen':maximum_debt,'elapsed_ms':1000*(time.perf_counter()-start),'outputs':len(outputs),'answer_cache':False,'indexed':indexed,'traversal':'seeded randomized depth-first; uniform final draw over discovered unique eligible tapes, not whole-language uniform'}}

def verified_insertion(base,left,right,left_index,right_index):
 """Verification primitive, not a grammar licence or a sentence-boundary guess.
 Raw offsets may be inside words: the caller must separately license the resulting
 two forward-readable derivations. This retains partial-word overhang capability.
 """
 if not is_palindrome(base):raise ValueError('base must be exact')
 if not 0<=left_index<=right_index<=len(base):raise ValueError('offset order')
 n=len(normalize(base));a=len(normalize(base[:left_index]));b=len(normalize(base[:right_index]))
 if a+b!=n:raise ValueError('offsets must mirror in normalized coordinates')
 if normalize(left)!=normalize(right)[::-1]:raise ValueError('inserted chunks must reverse-match')
 text=base[:left_index]+left+base[left_index:right_index]+right+base[right_index:]
 if not is_palindrome(text):raise ValueError('whole-output check failed')
 return {'text':text,'exact':True,'left_normalized_offset':a,'right_normalized_offset':b,'kind':'symmetric-end-to-end-blocks'if normalize(left)==normalize(right)else'asymmetric-partials','grammar_verified':False}
