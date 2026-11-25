"""Typed dialogue fragments plus a bounded global reverse-letter constraint.
Inputs are word senses and grammar arcs. There are no completed answer tapes.
"""
from dataclasses import asdict
from collections import defaultdict,Counter
from functools import lru_cache
import time,random,re,hashlib
from .bilateral_seams import Chunk
from .validator import normalize,is_palindrome
NAMES=('Anna','Hannah','Bob','Eve','Ava','Ada','Otto','Renner','Aviva','Nitin','Elle','Nora','Aron','Leon','Noel')
NOUNS=(('pins','thin',True),('pin','thin',False),('parts','parts',True),('part','parts',False),('tops','surface',True),('top','surface',False),('ward','building',False),('warder','person',False),('board','material',False),('boards','material',True),('wood','material',True),('model','artifact',False),('models','artifact',True),('plans','document',True),('sketch','document',False),('net','artifact',False),('pot','artifact',False))
VERBS={'snip':{'thin','material'},'strap':{'parts','artifact'},'spot':{'surface','building','person'},'draw':{'building','person','document','artifact'},'redraw':{'building','person','document','artifact'},'cut':{'thin','material'},'trim':{'thin','material'},'sand':{'material'},'fold':{'material'},'carve':{'material'},'paint':{'building','material'},'build':{'building','artifact'},'file':{'document'},'sew':{'material'},'weave':{'material'}}
OUTER={'snip':('pins','thin','intransitive cutting; echo asks which object'), 'draw':('ward','building','intransitive drawing; articleless echo names the drawing topic')}
@lru_cache(maxsize=64)
def grammar(depth=1,names=NAMES,verbs=tuple(VERBS),outer=tuple(OUTER)):
 if depth not in (1,2,3):raise ValueError('finite depth bound')
 out=[]
 def arc(a,b,text,role,bindings=()):
  out.append(Chunk('g'+str(len(out)),text,a,b,role,'independent word/role inventory029',tuple(bindings)))
 def q(i,start,end,last=False):
  p=f'q{i}:'
  arc(start,p+'NAME','Did ','past question auxiliary',(('scene','workshop task check'),))
  for name in names:arc(p+'NAME',p+'VP',name+' ','human question actor',((f'qactor{i}',name),))
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
  for name in names:arc(p+'ANSWER',p+'DID',name+' ','elliptic answer actor',((f'answer_actor{i}',name),(f'qactor{i}',name)))
  arc(p+'DID',end,'did.','affirmative/anaphoric response to this question',((f'answer_task{i}',str(i)),))
 for i in range(depth):q(i,'START'if i==0 else f'OPEN:{i}',f'OPEN:{i+1}'if i<depth-1 else f'CLOSE:{i}',i==depth-1)
 for i in reversed(range(depth-1)):
  p=f'close{i}:'
  for verb in outer:
   noun,kind,license=OUTER[verb]
   arc(f'CLOSE:{i+1}',p+'ANSWER',' '+noun.capitalize()+'? ','echo clarification of open object',((f'predicate{i}',verb),(f'object{i}',noun),(f'object_kind{i}',kind),(f'outer_topic{i}',noun)))
  for name in names:arc(p+'ANSWER',p+'DID',name+' ','answer actor for clarified task',((f'answer_actor{i}',name),(f'qactor{i}',name)))
  arc(p+'DID','END'if i==0 else f'CLOSE:{i}','did.','elliptic response with clarified object',((f'answer_task{i}',str(i)),))
 # Ensure spacing between a completed inner answer and the next echo.
 # Echo arcs already supply the one space; deepest answer supplies none.
 if depth==1:
  out=[Chunk(c.id,c.text,c.entry,'END'if c.exit=='CLOSE:0'else c.exit,c.role,c.source,c.bindings)for c in out]
 unique={ (c.text,c.entry,c.exit,c.bindings):c for c in out};return tuple(unique.values())

class GlobalSearch:
 def __init__(self,chunks):
  self.chunks=tuple(chunks);self.out=defaultdict(list);self.inc=defaultdict(list);self.units={};self.meta={};self.li=defaultdict(lambda:defaultdict(list));self.ri=defaultdict(lambda:defaultdict(list))
  if len(chunks)>512:raise ValueError('arc cap')
  for c in chunks:
   self.out[c.entry].append(c);self.inc[c.exit].append(c);self.units[c.id]=normalize(c.text);self.meta[c.id]=asdict(c);self.li[c.entry][self.units[c.id][0]].append(c);self.ri[c.exit][self.units[c.id][-1]].append(c)
  self.bounds={};self._visiting=set()
  states={'START','END'}|{c.entry for c in chunks}|{c.exit for c in chunks}
  for a in states:
   for b in states:self.remaining(a,b)
 def remaining(self,a,b):
  key=(a,b)
  if key in self.bounds:return self.bounds[key]
  if a==b:return (0,0)
  if key in self._visiting:raise ValueError('cyclic grammar forbidden in029')
  self._visiting.add(key);ranges=[]
  for c in self.out[a]:
   x=self.remaining(c.exit,b)
   if x is not None:ranges.append((len(self.units[c.id])+x[0],len(self.units[c.id])+x[1]))
  self._visiting.remove(key);r=(min(x[0]for x in ranges),max(x[1]for x in ranges))if ranges else None;self.bounds[key]=r;return r
 def search(self,*,seed=0,low=1,high=10000,seconds=.15,max_states=3000,max_steps=24,max_outputs=32,audit=False,indexed=True,centre=None,exclude_id=None):
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
   if s['total']+r[0]>high or s['total']+r[1]<low:reject('length_bound',s);continue
   if s['ls']==s['rs']and s['debt']==s['debt'][::-1]:
    text=s['left']+s['right'];t=normalize(text)
    assert is_palindrome(text)
    # Eligibility is inside the closure rule, before unique-output stopping.
    if low<=len(t)<=high:
     if centre and ((len(t)-len(centre))%2 or len(t)<len(centre)or t[(len(t)-len(centre))//2:(len(t)+len(centre))//2]!=centre):reject('centre_constraint',s);continue
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
     if any(k.startswith('outer_topic') and any(bk.startswith('outer_topic')and bk!=k and bv==v for bk,bv in b.items())for k,v in c.bindings):reject('repeated_open_topic',s,c);continue
     b.update(c.bindings);unit=self.units[c.id]if side=='left'else self.units[c.id][::-1];old=s['debt'];matched=s['matched']
     if old:
      k=min(len(old),len(unit))
      if old[:k]!=unit[:k]:reject('letter_mismatch',s,c);continue
      matched+=k
      if len(old)>len(unit):debt=old[k:];dside=s['side']
      else:debt=unit[k:];dside=side if debt else'none'
     else:debt=unit;dside=side
     if len(debt)>8:reject('debt_cap',s,c);continue
     maximum_debt=max(maximum_debt,len(debt));n={'left':s['left']+c.text if side=='left'else s['left'],'right':c.text+s['right']if side=='right'else s['right'],'ls':c.exit if side=='left'else s['ls'],'rs':c.entry if side=='right'else s['rs'],'side':dside,'debt':debt,'matched':matched,'bindings':b,'ids':s['ids']+[c.id],'trace':s['trace']+[{'side':side,'chunk':self.meta[c.id],'debt_before':{'side':s['side'],'letters':old},'debt_after':{'side':dside,'letters':debt},'paid':min(len(old),len(unit))if old else 0}],'steps':s['steps']+1,'total':s['total']+len(unit)};new.append(n)
   rng.shuffle(new);stack.extend(new)
  return {'outputs':list(outputs.values()),'failures':failures,'closed_derivations':closed,'receipt':{'status':status,'seed':seed,'low':low,'high':high,'seconds_cap':seconds,'max_states':max_states,'max_steps':max_steps,'max_outputs':max_outputs,'states_visited':visited,'proposals':proposals,'duplicate_states':duplicates,'failure_counts':dict(reasons),'pending_states':len(stack),'max_debt_seen':maximum_debt,'elapsed_ms':1000*(time.perf_counter()-start),'outputs':len(outputs),'answer_cache':False,'indexed':indexed,'traversal':'seeded randomized depth-first; uniform final draw over discovered unique eligible tapes, not whole-language uniform'}}

@lru_cache(maxsize=1)
def memo_grammar():
 """Independent declarative grammar. Its known exact control is not novel."""
 slots=[('START','SUBJ',('Some','Many','Several'),'plural quantifier'),('SUBJ','PRED',('men','editors','writers','students'),'human plural subject'),('PRED','NUM',('interpret','read','file','revise','draft','define','check'),'plural present predicate on written material'),('NUM','OBJ',('nine','ten','five','seven'),'cardinality'),('OBJ','END',('memos','notes','plans'),'plural written object')];out=[]
 for a,b,words,role in slots:
  for word in words:out.append(Chunk('m'+str(len(out)),word+('.'if b=='END'else' '),a,b,role,'independent memo word inventory029',(('frame','memo_statement'),)))
 return tuple(out)

def features(text,bindings):
 utterances=[x.strip()for x in re.split(r'[.!?]',text)if x.strip()];verbs=[v for k,v in bindings.items()if k.startswith('predicate')];actors=[v for k,v in bindings.items()if k.startswith(('qactor','answer_actor'))];counts=Counter(utterances)
 return {'utterance_count':len(utterances),'duplicate_utterances':sum(n-1 for n in counts.values()),'distinct_predicates':len(set(verbs)),'distinct_named_actors':len(set(actors)),'alternative_actor_answers':sum(bindings.get(k.replace('qactor','answer_actor'))!=v for k,v in bindings.items()if k.startswith('qactor')),'contains_clarification_fragments':any(u.lower()in {'pins','ward'}for u in utterances),'coherence_unrated':True}

def graph(depth=1):
 return _graph(depth)
@lru_cache(maxsize=4)
def _graph(depth):
 return GlobalSearch(memo_grammar()if depth==0 else grammar(depth))
