"""Bounded request-scoped lexical search and licensed result-seam composition."""
import json,random,time,hashlib,re,secrets
from functools import lru_cache
from pathlib import Path
from fastapi import APIRouter,Query,HTTPException
from .experimental_search.composition_029 import grammar,GlobalSearch,memo_grammar,features,NAMES
from .experimental_search.validator import normalize,is_palindrome
from .experimental_search.shape import shape
from . import dev_seed_028
BOUNDS={'max_steps':24,'max_states':3000,'max_outputs':32,'seconds':.15}
VERSION='global-composition-029';MIN_TARGET=16;MAX_TARGET=57;DEFAULT_TARGET=51
@lru_cache(maxsize=32)
def compiled(depth,seed_actor=None,seed_verb=None,seed_object=None,outer_actor=None):
 cs=memo_grammar()if depth==0 else grammar(depth,outer=('snip',))
 if seed_actor or seed_verb or seed_object or outer_actor:
  slot=0 if depth==1 else 1
  def allowed(c):
   b=dict(c.bindings)
   if outer_actor and any(k in b and b[k]!=outer_actor for k in ('qactor0','answer_actor0')):return False
   return not(seed_actor and any(k in b and b[k]!=seed_actor for k in (f'qactor{slot}',f'answer_actor{slot}')))and not(seed_verb and f'predicate{slot}'in b and b[f'predicate{slot}']!=seed_verb)and not(seed_object and f'object{slot}'in b and b[f'object{slot}']!=seed_object)
  cs=tuple(c for c in cs if allowed(c))
 return GlobalSearch(cs)
@lru_cache(maxsize=1)
def source_hashes():
 paths=[Path(__file__),Path(__file__).parent/'experimental_search/composition_029.py',Path(__file__).parent/'experimental_search/shape.py']
 return {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}

def parse_direct_seed(text):
 words=re.findall(r'[A-Za-z]+',text);g=compiled(1);stack=[('START',0,{})]
 while stack:
  state,i,b=stack.pop()
  if state=='END'and i==len(words):return b
  for c in g.out[state]:
   w=re.findall(r'[A-Za-z]+',c.text)
   if [x.lower()for x in words[i:i+len(w)]]!=[x.lower()for x in w]:continue
   if any(k in b and b[k]!=v for k,v in c.bindings):continue
   stack.append((c.exit,i+len(w),{**b,**dict(c.bindings)}))
 return None

def component_results(row):
 b=row['bindings'];parts=[]
 for i in range(2):
  if f'qactor{i}'not in b:continue
  noun=b[f'object{i}'];det=''if noun in {'pins','parts','tops','boards','models','plans','wood'}else'a '
  text=f"Did {b[f'qactor{i}']} {b[f'predicate{i}']} {det}{noun}? {b[f'answer_actor{i}']} did."
  parts.append({'text':text,'letters':len(normalize(text)),'exact':is_palindrome(text),'source':'licensed word/role path; no answer lookup'})
 return parts

def generate(*,letters=DEFAULT_TARGET,seed=None,centre=None,seed_text=None,budget_ms=150,exclude_id=None):
 start=time.perf_counter();actual_seed=seed if seed is not None else secrets.randbits(32);rng=random.Random(actual_seed);target=max(MIN_TARGET,min(MAX_TARGET,letters));low=max(MIN_TARGET,target-10);high=min(MAX_TARGET,target+10);runs=[];found={};direct=None;legacy_seed=None
 if seed_text:
  if not is_palindrome(seed_text):return None,{'revision':VERSION,'source_hashes':source_hashes(),'status':'nonpalindromic_seed','outputs':0,'eligible_outputs':0,'answer_cache':False,'target_letters':target,'eligible_range':{'min':low,'max':high},'seed':actual_seed,'performed_search':False,'elapsed_total_ms':1000*(time.perf_counter()-start)}
  direct=parse_direct_seed(seed_text)
  if not direct:
   licensed=dev_seed_028.seed_gap(seed_text)
   if licensed and not licensed[3]:
    tokens=re.findall(r'[A-Za-z]+',seed_text);vp=tokens[3:-3];direct={'predicate0':vp[0].lower(),'object0':vp[-1].lower(),'fragment_only':True,'removed_modifiers':vp[1:-1]}
  if not direct:
   legacy_seed,receipt=dev_seed_028.generate(letters=low,seed=actual_seed,centre=centre,seed_text=seed_text,budget_ms=budget_ms)
   if legacy_seed and low<=legacy_seed['letters']<=high:
    legacy_seed.update(requested_letters=letters,target_letters=target,eligible_range={'min':low,'max':high},result_id='global-'+hashlib.sha256(normalize(legacy_seed['text']).encode()).hexdigest()[:16]);legacy_seed['shape']=shape(legacy_seed['text']);legacy_seed['search'].update(revision=VERSION,source_hashes=source_hashes(),seed=actual_seed,length_window=10,answer_cache=False)
    if legacy_seed['result_id']!=exclude_id:return legacy_seed,legacy_seed['search']
   return None,{**receipt,'revision':VERSION,'source_hashes':source_hashes(),'target_letters':target,'eligible_range':{'min':low,'max':high},'eligible_outputs':0,'seed':actual_seed,'performed_search':receipt.get('status') not in {'unlicensed_seed','nonpalindromic_seed'}}
 ct=normalize(centre or'');jobs=[]
 for depth,weight in [(0,1),(1,4),(2,4)]:
  if direct and depth!=2:continue
  kwargs={}
  if direct:
   if not direct.get('fragment_only')and direct['predicate0']=='snip'and direct['object0']=='pins':kwargs={'outer_actor':direct['qactor0']}
   else:kwargs={'seed_actor':direct.get('qactor0'),'seed_verb':direct['predicate0'],'seed_object':direct['object0']}
  g=compiled(depth,**kwargs);bounds=g.remaining('START','END')
  if bounds and low<=bounds[1]and high>=bounds[0]:jobs.append((rng.random()**(1/weight),depth,g))
 jobs.sort(reverse=True,key=lambda x:x[0])
 # Search each viable grammar only as needed; source inputs may be cached, answers never are.
 for _,depth,g in jobs:
  remaining=budget_ms/1000-(time.perf_counter()-start)
  if remaining<=0:break
  run=g.search(seed=actual_seed+depth,low=low,high=high,seconds=remaining,max_states=3000,max_steps=24,max_outputs=32,centre=ct,exclude_id=exclude_id)
  runs.append({'depth':depth,'arcs':len(g.chunks),**run['receipt']})
  for row in run['outputs']:
   row['family']='memo_statement'if depth==0 else'task_dialogue';row['depth']=depth;found[normalize(row['text'])]=row
  if found:break
 receipt={'revision':VERSION,'source_hashes':source_hashes(),'seed':actual_seed,'eligible_range':{'min':low,'max':high},'target_letters':target,'length_window':10,'runs':runs,'states_visited':sum(x['states_visited']for x in runs),'eligible_outputs':len(found),'elapsed_total_ms':1000*(time.perf_counter()-start),'budget_ms':budget_ms,'max_outputs':32,'answer_cache':False,'performed_search':bool(runs),'sampling':'weighted grammar-family traversal, seeded randomized search, uniform distinct eligible tapes within best repetition tier; not whole-language uniform'}
 if not found:return None,receipt
 rows=list(found.values());rng.shuffle(rows)
 rows.sort(key=lambda r:(features(r['text'],r['bindings'])['duplicate_utterances'],-features(r['text'],r['bindings'])['distinct_predicates']))
 row=rows[0];text=row['text'];t=normalize(text);assert is_palindrome(text)and low<=len(t)<=high
 parts=component_results(row);composition=None
 if row['depth']==2:
  assert len(parts)==2 and all(p['exact']for p in parts)
  a,b=parts;left='Did '+row['bindings']['qactor0']+' snip';right='Pins? '+row['bindings']['answer_actor0']+' did.'
  assert normalize(text)==normalize(left)+normalize(b['text'])+normalize(right)
  composition={'kind':'reopened-result-seam','components':parts,'retained_left':left,'retained_right':right,'plain_append_exact':is_palindrome(a['text']+b['text']),'whole_output_exact':True,'complete_seed_tape_preserved':bool(seed_text)and normalize(seed_text)in {normalize(p['text'])for p in parts},'contains_clarification_fragments':True,'template_reuse':'past-action question/answer and explicitly licensed echo-object clarification; no general prose claim'}
 half=len(t)//2
 return {'version':3,'result_id':row['id'],'text':text,'plain':text,'letters':len(t),'characters':len(text),'words':len(text.split()),'requested_letters':letters,'target_letters':target,'eligible_range':{'min':low,'max':high},'pairs':0,'chunks':[],'sentences':re.findall(r'[^.!?]+[.!?]',text),'hierarchical':True,'sentence_pairs':0,'distinct_chunks':len({s['chunk']['id']for s in row['trace']}),'repeats':features(text,row['bindings'])['duplicate_utterances'],'centre_is_yours':bool(ct),'seed_is_yours':bool(seed_text),'seed_semantics':('predicate/object fragments; participants and syntax recomposed'if direct and direct.get('fragment_only')else'complete normalized component retained'if direct else None),'removed_seed_modifiers':direct.get('removed_modifiers',[])if direct else[],'shape':shape(text),'family':row['family'],'construction_depth':row['depth'],'can_compose_as_component':row['family']=='task_dialogue'and row['depth']==1,'generation_method':'typed-global-result-composition'if row['depth']==2 else'typed-global-word-search','newly_searched':True,'stored_answer_sampling':False,'known_control':row['family']=='memo_statement','novelty_unverified':True,'quality_unrated':True,'search':receipt,'composition':composition,'center':{'letter_index':half,'odd':bool(len(t)%2),'character':t[half]if len(t)%2 else None,'derived_from_full_output':True,'original_seed_center_required':False},'features':features(text,row['bindings']),'derivation':{'bindings':row['bindings'],'trace':row['trace']}},receipt

def create_router(fallback):
 # Compile only immutable grammar/index inputs. No search or answer cache here.
 for depth in (0,1,2):compiled(depth)
 router=APIRouter(prefix='/api/dev/v3')
 @router.get('/health')
 def health():return {'ok':True,'version':3,'experimental':True,'revision':VERSION,'source_hashes':source_hashes(),'search':True,'bank_sampling':False,'bounds':BOUNDS,'length_window':10,'default_target':DEFAULT_TARGET,'minimum_target':MIN_TARGET,'capacity':{'novel':{'max_letters':MAX_TARGET}},'capacity_basis':'finite typed grammar bound; not a novelty or readability claim','families':['memo_statement','task_dialogue'],'quality_unrated':True}
 @router.get('/composition')
 def composition(seed:int|None=None,letters:int=DEFAULT_TARGET,centre:str|None=Query(None,max_length=200),budget_ms:int=Query(150,ge=20,le=150),fallback:bool=False,seed_text:str|None=Query(None,max_length=200),exclude_id:str|None=Query(None,max_length=64)):
  if centre and seed_text:raise HTTPException(422,'Choose a seed or a literal centre, not both.')
  for value in [centre,seed_text]:
   if value and (not normalize(value)or any(not(c.isascii()and(c.isalpha()or c.isspace()or c in "'-.,;:!?"))for c in value)):raise HTTPException(422,'Use English words and punctuation in the seed or centre.')
  result,receipt=generate(letters=letters,seed=seed,centre=centre,seed_text=seed_text,budget_ms=budget_ms,exclude_id=exclude_id)
  if result is not None:return result
  if fallback:
   result=dict(fallback_composer(seed=seed,letters=letters,chops=None,longest_first=False,centre=seed_text or centre,novel=True));result.update(generation_method='explicit-legacy-corpus-fallback',newly_searched=False,search=receipt,fallback_reason='bounded search returned no eligible exact text');return result
  raise HTTPException(409,detail={'message':'No exact result found in this length window. Try another length or seed.','generation_method':'typed-global-word-search','newly_searched':receipt.get('performed_search',True),'search':receipt})
 fallback_composer=fallback
 return router
