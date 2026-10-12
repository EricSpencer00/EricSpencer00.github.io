"""Iterative bilateral phrase FSA with asymmetric reverse-letter debt.
Invariant: normalize(L)=matched+dL and reverse(normalize(R))=matched+dR,
with at most one nonempty debt. Every extension must preserve that prefix
compatibility. Closure requires meeting grammar states and palindromic debt.
"""
from dataclasses import dataclass,asdict
from collections import defaultdict,deque
import time,hashlib
from .admission import normalize_letters as norm,ALLOWED_RENDERING

@dataclass(frozen=True)
class Chunk:
 id:str
 text:str
 entry:str
 exit:str
 role:str
 source:str
 bindings:tuple=()

def debt(left,right):
 l=norm(left);r=norm(right)[::-1];k=min(len(l),len(r))
 for i in range(k):
  if l[i]!=r[i]:return dict(compatible=False,offset=i,left=l[i],mirrored_right=r[i])
 return dict(compatible=True,matched=k,side='left' if len(l)>len(r) else ('right' if len(r)>len(l) else 'none'),letters=l[k:] if len(l)>len(r) else r[k:],closure_exact=(l+r[::-1])==(l+r[::-1])[::-1])

def payoff(previous,extension_side,extension_letters,next_debt):
 if not previous['compatible'] or not next_debt['compatible']:return dict(paid=0,added=extension_letters,ratio=0,valid=False)
 old=len(previous['letters']);paid=min(old,extension_letters) if previous['side'] not in ('none',extension_side) else 0
 return dict(paid=paid,added=extension_letters,ratio=paid/max(1,extension_letters),debt_before=old,debt_after=len(next_debt['letters']),valid=True)

def phrase_payoff_utility(payoff_info,text):
 """Fixed per-chunk overhead avoids rewarding one-letter maximal ratios.
 Raw payoff remains auditable; this never changes letter compatibility.
 """
 import re
 words=re.findall(r"[a-z]+",text.lower());coverage=min(len(words),3)/3
 return payoff_info['paid']/(payoff_info['added']+4)*coverage

class BilateralGrammar:
 def __init__(self,chunks,start='START',end='END'):
  self.chunks=tuple(chunks);self.start=start;self.end=end;self.out=defaultdict(list);self.inc=defaultdict(list)
  if len(chunks)>512:raise ValueError('chunk inventory bound')
  if len({c.id for c in chunks})!=len(chunks):raise ValueError('duplicate chunk IDs')
  for c in chunks:
   if not norm(c.text) or len(norm(c.text))>160 or not c.role or not c.source:raise ValueError('invalid chunk')
   if any(not x.isascii() or not(x.isalpha() or x.isspace() or x in "'-.,;:!?") for x in c.text):raise ValueError('unsupported rendering')
   self.out[c.entry].append(c);self.inc[c.exit].append(c)

 def extend(self,state,c,side):
  required=state['left_state'] if side=='left' else state['right_state']
  if (c.entry if side=='left' else c.exit)!=required:return None,dict(reason='grammar_state')
  bindings=dict(state['bindings'])
  for k,v in c.bindings:
   if k in bindings and bindings[k]!=v:return None,dict(reason='actor_conflict',variable=k,existing=bindings[k],proposed=v)
   bindings[k]=v
  l=state['left']+c.text if side=='left' else state['left'];r=c.text+state['right'] if side=='right' else state['right'];d=debt(l,r)
  if not d['compatible']:return None,dict(reason='letter_mismatch',mismatch=d)
  score=payoff(state['debt'],side,len(norm(c.text)),d)
  ids=state['left_ids']+state['right_ids'];repeat=ids.count(c.id)
  new=dict(left=l,right=r,left_state=c.exit if side=='left' else state['left_state'],right_state=c.entry if side=='right' else state['right_state'],left_ids=state['left_ids']+[c.id] if side=='left' else state['left_ids'],right_ids=[c.id]+state['right_ids'] if side=='right' else state['right_ids'],bindings=bindings,debt=d,steps=state['steps']+1,repeat_cost=state['repeat_cost']+repeat,trace=state['trace']+[dict(side=side,chunk=asdict(c),debt=d,payoff=score,repeat_increment=repeat)])
  return new,None

 def initial(self):return dict(left='',right='',left_state=self.start,right_state=self.end,left_ids=[],right_ids=[],bindings={},debt=debt('',''),steps=0,repeat_cost=0,trace=[])

 def closed(self,s):return s['left_state']==s['right_state'] and s['debt']['closure_exact']

 def render(self,s):return s['left']+s['right']

 def candidates(self,s):return [('left',self.out[s['left_state']]),('right',self.inc[s['right_state']])]

 def initial_states(self):return iter([self.initial()])

 def search(self,max_steps=16,max_states=5000,max_outputs=100,seconds=3):
  start=time.monotonic();q=deque();seen=set();outputs={};failures=[];visits=0;cycles=0;duplicate_states=0;status='complete_bounded_depth';seeds=0
  for seed in self.initial_states():
   if seeds>=getattr(self,'max_seeds',10000) or time.monotonic()-start>seconds:
    status='seed_truncated';break
   q.append(seed);seeds+=1
  seed_status=status
  while q:
   if visits>=max_states or time.monotonic()-start>seconds:status='resource_truncated';break
   s=q.popleft();visits+=1
   if s['steps']>max_steps:continue
   key=(s['left_state'],s['right_state'],s['left'],s['right'],tuple(s['left_ids']),tuple(s['right_ids']),tuple(sorted(s['bindings'].items())),tuple(s.get('center_ids',[])),tuple(s.get('center_offset',[])))
   if key in seen:duplicate_states+=1;continue
   seen.add(key)
   if self.closed(s):
    text=self.render(s);t=norm(text)
    if t and ALLOWED_RENDERING.fullmatch(text):
     assert t==t[::-1]
     if t not in outputs:outputs[t]=dict(id='bilateral-'+hashlib.sha256(t.encode()).hexdigest()[:16],text=text,tape=t,letters=len(t),**{k:s[k] for k in ['left_ids','right_ids','bindings','repeat_cost','trace']},quality_unrated=True,center_ids=s.get('center_ids',[]),center_offset=s.get('center_offset'),repetition=rendered_repetition(text,[step['chunk']['text'] for step in s['trace']]+s.get('center_texts',[])))
     if len(outputs)>=max_outputs:status='output_truncated';break
   if s['steps']>=max_steps:continue
   proposals=[]
   for side,cs in self.candidates(s):
    for c in cs:
     new,reason=self.extend(s,c,side)
     if reason:failures.append(dict(left_ids=s['left_ids'],right_ids=s['right_ids'],side=side,chunk=c.id,**reason));continue
     # Cycle handling never collapses different texts; repeats penalized,
     # bounds protect execution. A repeated grammar/debt signature is marked.
     signature=(new['left_state'],new['right_state'],new['debt']['side'],new['debt']['letters'])
     prior={(self.start,self.end,'none','')}
     for step in s['trace']:
      # Explicit state history stored below gives productive diagnostics.
      if 'signature' in step:prior.add(tuple(step['signature']))
     if signature in prior:cycles+=1;new['trace'][-1]['cycle_signature_revisited']=True
     new['trace'][-1]['signature']=signature
     proposals.append(new)
   proposals.sort(key=lambda n:(-phrase_payoff_utility(n['trace'][-1]['payoff'],n['trace'][-1]['chunk']['text']),n['repeat_cost']+rendered_repetition(self.render(n),[step['chunk']['text'] for step in n['trace']]+n.get('center_texts',[]))['token_repeat_excess'],len(n['debt']['letters']),n['left_ids'],n['right_ids']));q.extend(proposals)
  return dict(outputs=list(outputs.values()),failures=failures,receipt=dict(status=status,seed_status=seed_status,seeds=seeds,max_steps=max_steps,max_states=max_states,max_outputs=max_outputs,seconds_cap=seconds,states_visited=visits,duplicate_states=duplicate_states,cycle_signatures=cycles,outputs=len(outputs),failures=len(failures),pending_states=len(q),elapsed_seconds=time.monotonic()-start),infinite_claim='No infinite coherent/nonrepeating claim; productive unbounded family requires a separate cycle certificate.')

class CenterOutGrammar(BilateralGrammar):
 """Paper Section2 direction: prepend L, append R, close on empty debt.
 Reuses legacy consume for debt-paying placements. Center is an explicit
 licensed chunk path, not an unexplained character inserted to repair text.
 """
 def __init__(self,chunks,center_ids,start='START',end='END',center_state=None):
  super().__init__(chunks,start,end);by={c.id:c for c in chunks};self.center_chunks=[by[i] for i in center_ids]
  if not self.center_chunks and center_state is None:raise ValueError('explicit center chunk path or boundary state required')
  self.center_state=center_state
  for a,b in zip(self.center_chunks,self.center_chunks[1:]):
   if a.exit!=b.entry:raise ValueError('center grammar seam')
  self.center=''.join(c.text for c in self.center_chunks)
  if norm(self.center)!=norm(self.center)[::-1]:raise ValueError('center must be exact')

 def initial(self):
  s=super().initial();s['left_state']=self.center_chunks[0].entry if self.center_chunks else self.center_state;s['right_state']=self.center_chunks[-1].exit if self.center_chunks else self.center_state
  for c in self.center_chunks:
   for k,v in c.bindings:
    if k in s['bindings'] and s['bindings'][k]!=v:raise ValueError('center actor conflict')
    s['bindings'][k]=v
  return s

 def candidates(self,s):
  # Paper/legacy centerout pays the owed side; overflow legitimately flips
  # debt. Growing the already-long side only postpones the same obligation.
  if s['debt']['side']=='left':return [('right',self.out[s['right_state']])]
  if s['debt']['side']=='right':return [('left',self.inc[s['left_state']])]
  return [('left',self.inc[s['left_state']]),('right',self.out[s['right_state']])]
 def render(self,s):return s['left']+s.get('center_text',self.center)+s['right']
 def closed(self,s):return s['left_state']==self.start and s['right_state']==self.end and not s['debt']['letters']

 def extend(self,state,c,side):
  from .search import consume
  if (c.exit if side=='left' else c.entry)!=(state['left_state'] if side=='left' else state['right_state']):return None,dict(reason='grammar_state')
  bindings=dict(state['bindings'])
  for k,v in c.bindings:
   if k in bindings and bindings[k]!=v:return None,dict(reason='actor_conflict',variable=k,existing=bindings[k],proposed=v)
   bindings[k]=v
  l=c.text+state['left'] if side=='left' else state['left'];r=state['right']+c.text if side=='right' else state['right']
  # Compare from center toward outer edges: reverse(L) versus R.
  d=debt((norm(l)+state.get('anchor_left',''))[::-1],(state.get('anchor_right','')+norm(r))[::-1])
  if d['compatible']:
   d['palindromic_residual']=bool(d['letters']==d['letters'][::-1]);d['closure_exact']=not d['letters']
  if not d['compatible']:return None,dict(reason='letter_mismatch',mismatch=d)
  old=state['debt'];unit=norm(c.text)[::-1] if side=='left' else norm(c.text)
  if old['side'] not in ('none',side):assert consume(unit,old['letters']) is not None
  score=payoff(old,side,len(unit),d);repeat=(state['left_ids']+state['right_ids']+state.get('center_ids',[c.id for c in self.center_chunks])).count(c.id)
  new=dict(left=l,right=r,left_state=c.entry if side=='left' else state['left_state'],right_state=c.exit if side=='right' else state['right_state'],left_ids=[c.id]+state['left_ids'] if side=='left' else state['left_ids'],right_ids=state['right_ids']+[c.id] if side=='right' else state['right_ids'],bindings=bindings,debt=d,steps=state['steps']+1,repeat_cost=state['repeat_cost']+repeat,trace=state['trace']+[dict(side=side,chunk=asdict(c),debt=d,payoff=score,repeat_increment=repeat,growth='prepend_L' if side=='left' else 'append_R')])
  for k in ('anchor_left','anchor_right','center_text','center_texts','center_ids','center_offset'):
   if k in state:new[k]=state[k]
  return new,None


def rendered_repetition(text,chunk_texts):
 """Report token and rendered-phrase repeats even when chunk IDs differ."""
 import re
 from collections import Counter
 words=Counter(re.findall(r"[a-z]+",text.lower()))
 phrases=Counter(norm(t) for t in chunk_texts)
 return dict(repeated_tokens={w:n for w,n in words.items() if n>1},
             token_repeat_excess=sum(n-1 for n in words.values()),
             repeated_phrases={w:n for w,n in phrases.items() if n>1})

class OwedSideBilateralGrammar(BilateralGrammar):
 """Outside-in oracle: extend only the side paying existing letter debt."""
 def candidates(self,s):
  if s['debt']['side']=='left':return [('right',self.inc[s['right_state']])]
  if s['debt']['side']=='right':return [('left',self.out[s['left_state']])]
  return super().candidates(s)

class WholeChunkCenterGrammar(CenterOutGrammar):
 """One intact licensed chunk spans an internal letter or boundary center."""
 def __init__(self,chunks,anchor_id,split,width,start='START',end='END'):
  BilateralGrammar.__init__(self,chunks,start,end)
  anchor=next(c for c in chunks if c.id==anchor_id);t=norm(anchor.text)
  if width not in (0,1) or not 0<=split<=len(t)-width:raise ValueError('invalid center offset')
  self.anchor_left=t[:split];self.anchor_right=t[split+width:]
  self.seed_debt=debt(self.anchor_left[::-1],self.anchor_right[::-1])
  if not self.seed_debt['compatible']:raise ValueError('anchor conflicts across its own center')
  self.seed_debt['closure_exact']=not self.seed_debt['letters']
  self.center_chunks=[anchor];self.center=anchor.text;self.center_state=None
  self.anchor_offset=(split,width)
 def initial(self):
  s=BilateralGrammar.initial(self);a=self.center_chunks[0]
  s.update(left_state=a.entry,right_state=a.exit,bindings=dict(a.bindings),
           debt=dict(self.seed_debt),steps=1,anchor_left=self.anchor_left,
           anchor_right=self.anchor_right,center_text=a.text,center_texts=[a.text],
           center_ids=[a.id],center_offset=self.anchor_offset)
  return s

class AllChunkCentersGrammar(CenterOutGrammar):
 """Shared queue and one aggregate budget over all intact-chunk centers.
 Anchor counts toward chunk depth; no offsets change the rendered text.
 """
 def __init__(self,chunks,start='START',end='END',max_seeds=10000):
  BilateralGrammar.__init__(self,chunks,start,end)
  if not 1<=max_seeds<=100000:raise ValueError('seed bound')
  self.max_seeds=max_seeds;self.center='';self.center_chunks=[]
 def initial_states(self):
  for c in self.chunks:
   for width in (0,1):
    for split in range(len(norm(c.text))+1-width):
     try:g=WholeChunkCenterGrammar(self.chunks,c.id,split,width,self.start,self.end)
     except ValueError as e:
      if str(e)!='anchor conflicts across its own center':raise
      continue
     yield g.initial()

def screen_fixed_endpoints(left,right,*,previous=None,extension_side=None,extension_text=''):
 """Reject immutable outer-prefix mismatches before expanding the interior.
 The caller must supply nonoverlapping fixed prefix/suffix chunks. Admission
 is necessary, never sufficient: nonpalindromic debt may still be completed.
 Payoff is diagnostic/ranking only; no threshold or repetition veto applies.
 """
 l=''.join(c.text for c in left);r=''.join(c.text for c in right)
 bindings={}
 for c in tuple(left)+tuple(right):
  for k,v in c.bindings:
   if k in bindings and bindings[k]!=v:return dict(admitted=False,reason='actor_conflict',variable=k)
   bindings[k]=v
 d=debt(l,r)
 if not d['compatible']:return dict(admitted=False,reason='immutable_endpoint_mismatch',debt=d)
 score=None;utility=None
 if previous is not None:
  if extension_side not in ('left','right'):raise ValueError('extension_side required for payoff')
  score=payoff(previous,extension_side,len(norm(extension_text)),d)
  utility=phrase_payoff_utility(score,extension_text)
 return dict(admitted=True,debt=d,payoff=score,payoff_utility=utility,bindings=bindings,closure_claim=False)
