"""Finite typed lexical search. Inventories contain words/rules, not answers."""
import time,re,random,json
from functools import lru_cache
from pathlib import Path
from .bilateral_seams import AllChunkCentersGrammar,OwedSideBilateralGrammar,Chunk
from .validator import normalize,is_palindrome
BOUNDS=dict(max_steps=24,max_states=3000,max_outputs=32,seconds=.15)
NAMES=['Eva','Ada','Anna','Bob','Dan','Eve','Nora','Otto','Pat','Sam']
PLACES=['cave','den','room','cabin','house','park']
# Object features are declared lexical senses, not an English-quality model.
NOUNS=[('ward','building',False),('warder','person',False),('tup','animal',False),('bat','animal',False),('pet','animal',False),('bee','animal',False),('pin','thin',False),('pins','thin',True),('bats','animal',True),('bees','animal',True),('pets','animal',True),('parts','loose_parts',True),('tops','surface',True),('pot','container',False),('pots','container',True),('tap','surface',False),('trap','mechanism',False)]
VERBS={'draw':{'building','person','animal','thin','loose_parts','surface','container','mechanism'},'redraw':{'building','person','animal','thin','surface'},'snip':{'thin'},'strap':{'loose_parts','thin'},'put':{'animal','thin','loose_parts','container','mechanism'},'top':{'container'},'spot':{'surface','animal','person','building'},'pat':{'animal','person','surface'},'stab':{'animal'},'see':{'animal','person','surface','building'},'nip':{'thin'}}
ADJECTIVES={'level':{'thin','surface','loose_parts'},'small':{'animal','thin','container','mechanism','building'},'red':{'container','thin','surface'},'calm':{'animal','person'},'old':{'person','building','container','mechanism'},'new':{'container','building','mechanism'}}

@lru_cache(maxsize=1)
def chunks():
 out=[]
 def arc(frame,a,b,text,role,features=()):
  out.append(Chunk(f'{frame}-{len(out)}',text,a if a=='START'else frame+':'+a,b if b=='END'else frame+':'+b,role,'curated lexical grammar v1',(('frame',frame),('agent','speaker1'))+tuple(features)))
 # Shared predicates are recompiled per sentence frame, with separate states.
 for frame in ['question','instruction_reply']:
  if frame=='question':
   for name in NAMES:arc(frame,'START','AUX',name+', ','vocative addressee')
   for aux in ['can','did','will']:arc(frame,'AUX','SUBJ',aux+' ','modal/auxiliary, base verb required')
   arc(frame,'SUBJ','VP','I ','first-person human subject')
  else:pass
  copies=1 if frame=='question'else 2
  for pos in range(copies):
   entry='VP'if frame=='question'else('START'if pos==0 else'VP2');end='POST'if frame=='question'else('REPLY'if pos==0 else'END')
   for verb,types in VERBS.items():
    if frame=='instruction_reply'and verb=='put':continue # put requires locative
    state=f'{pos}:OBJ:{verb}';arc(frame,entry,state,verb.capitalize()+' 'if frame=='instruction_reply'and pos==0 else verb+' ','base transitive verb',(('verb'+str(pos),verb),))
    for noun,kind,plural in NOUNS:
     if kind not in types:continue
     feature=(('object_type'+str(pos),kind),)
     if plural:arc(frame,state,end,noun,'plural direct object',feature)
     else:
      det=f'{state}:{kind}:DET'
      # Add determiner once per type, not once per noun.
      if not any(c.entry==frame+':'+state and c.exit==frame+':'+det for c in out):arc(frame,state,det,'a ','singular indefinite determiner')
      arc(frame,det,end,noun,'singular direct object',feature)
     base=state if plural else det
     for adjective,allowed in (ADJECTIVES.items() if frame=='question' else []):
      if kind not in allowed:continue
      target=f'{base}:ADJ:{adjective}'
      if not any(c.entry==frame+':'+base and c.exit==frame+':'+target for c in out):arc(frame,base,target,adjective+' ','licensed physical attribute')
      arc(frame,target,end,noun,'modified direct object',feature)
  if frame=='question':
   for prep in ['in','near']:arc(frame,'POST','LOCDET', ' '+prep+' ','locative of the action')
   arc(frame,'LOCDET','LOCATION','a ','location determiner')
   for place in PLACES:arc(frame,'LOCATION','END',place+'?','physical location')
  else:arc(frame,'REPLY','VP2','. I ','instruction followed by first-person execution')
 # Compiler's existing inventory bound is512; duplicate identical arcs collapse.
 unique={ (c.text,c.entry,c.exit,c.bindings):c for c in out}
 return tuple(unique.values())

class SearchGrammar(OwedSideBilateralGrammar):
 """Outside-in grammar search; the literal centre is determined at closure.
 Debt may cross token/phrase seams. Only the owed side is extended.
 """
 def __init__(self,chunks,max_debt=8):
  super().__init__(chunks);self.max_debt=max_debt
 def extend(self,s,c,side):
  n,error=super().extend(s,c,side)
  if n is not None and len(n['debt']['letters'])>self.max_debt:return None,{'reason':'debt_cap'}
  return n,error



def inventory(family='question',split='all'):
 """Lexical holdout fixed before runs. No withheld sentence answers loaded."""
 cs=[c for c in chunks() if dict(c.bindings)['frame']==family]
 heldout={'snip','strap','spot'}
 if split!='all':
  def admit(c):
   verb=next((v for k,v in c.bindings if k.startswith('verb')),None)
   # Object states are verb-specific; remove their arcs together.
   path_verb=next((v for v in VERBS if (':OBJ:'+v) in c.entry or (':OBJ:'+v) in c.exit),None)
   selected=verb or path_verb
   return selected is None or ((selected in heldout)==(split=='heldout'))
  cs=[c for c in cs if admit(c)]
 return tuple(cs)

def oracle(cs,limit=200000):
 """Complete independent forward grammar enumeration; no palindrome pruning."""
 from collections import defaultdict
 outgoing=defaultdict(list)
 for c in cs:outgoing[c.entry].append(c)
 stack=[('START','',{},[])];paths=[]
 while stack:
  state,text,bindings,ids=stack.pop()
  if state=='END':
   paths.append({'text':text,'ids':ids,'exact':is_palindrome(text)})
   if len(paths)>limit:raise ValueError('oracle path budget exceeded')
   continue
  for c in outgoing[state]:
   b=dict(bindings)
   if any(k in b and b[k]!=v for k,v in c.bindings):continue
   b.update(c.bindings);stack.append((c.exit,text+c.text,b,ids+[c.id]))
 return paths

def paragraph_inventory(sentences=3):
 """Finite same-speaker/addressee/location dialogue. Separate predicate slots.
 Narrow diagnostic vocabulary keeps the full forward oracle below 200k paths.
 """
 from dataclasses import replace
 if sentences not in (2,3,4):raise ValueError('paragraph sentence bound')
 base=[]
 for c in inventory('question','heldout'):
  if ':ADJ:'in c.entry or ':ADJ:'in c.exit:continue
  if c.entry=='START'and c.text!='Eva, ':continue
  if c.role.startswith('modal')and c.text!='can ':continue
  if c.role=='locative of the action'and c.text!=' in ':continue
  if c.role=='physical location'and c.text!='cave?':continue
  base.append(c)
 out=[]
 for i in range(sentences):
  def state(s):
   if s=='START':return 'START'if i==0 else f'seam:{i}'
   if s=='END':return 'END'if i==sentences-1 else f'seam:{i+1}'
   return f'clause:{i}:{s}'
  for c in base:
   bindings=tuple((f'clause:{i}:{k}'if k.startswith(('verb','object_type'))else k,v)for k,v in c.bindings)+(('addressee','Eva'),('location','cave'))
   text=c.text+(' 'if c.exit=='END'and i<sentences-1 else'')
   out.append(replace(c,id=f'clause:{i}:{c.id}',entry=state(c.entry),exit=state(c.exit),text=text,bindings=bindings))
 return tuple(out)

def geese_gap_inventory():
 """A small PP argument grammar; the user supplied the successful example.
 This is a control reconstruction, not held-out or novel discovery.
 """
 result=[]
 for state,next_state,words,role in [
  ('START','DET',['on','in','near'],'location preposition'),
  ('DET','MATERIAL',['a','the'],'singular determiner'),
  ('MATERIAL','PURPOSE',['cedar','oak','pine','ash'],'boat material modifier'),
  ('PURPOSE','HEAD',['trade','fishing','racing','touring'],'boat use modifier'),
  ('HEAD','END',['canoe','boat','kayak','raft'],'singular floating location')]:
  for word in words:result.append(Chunk('gap:'+state+':'+word,word+' ',state,next_state,role,'user-example-informed lexical PP control',(('subject','geese'),('location_kind','boat'))))
 return tuple(result)

class InternalGapGrammar(SearchGrammar):
 """Hold grammatical outer spans, search the gap with asymmetric debt.
 There is no requirement that the gap, or an original centre, be a palindrome.
 """
 def __init__(self,cs,left,right,max_debt=8):
  super().__init__(cs,max_debt);self.fixed_left=left;self.fixed_right=right;self.seed_rejections=[]
 def initial(self):
  from .bilateral_seams import debt
  s=super().initial();s.update(left=self.fixed_left,right=self.fixed_right,debt=debt(self.fixed_left,self.fixed_right))
  if not s['debt']['compatible']:raise ValueError('immutable endpoint mismatch')
  return s

 def initial_states(self):
  s=self.initial()
  if len(s['debt']['letters'])>self.max_debt:self.seed_rejections.append({'reason':'initial_debt_cap','debt':s['debt']})
  else:yield s
