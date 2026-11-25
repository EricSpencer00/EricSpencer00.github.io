"""Additive experimental router. Legacy production composer is unchanged."""
import json,random,time,hashlib,re
from dataclasses import replace
from functools import lru_cache
from pathlib import Path
from fastapi import APIRouter,Query,HTTPException
from .experimental_search.late_center_lexical import inventory,SearchGrammar,InternalGapGrammar,geese_gap_inventory
from .experimental_search.validator import normalize,is_palindrome
from .experimental_search.shape import shape
BOUNDS={'max_steps':24,'max_states':3000,'max_outputs':32,'seconds':.15}
VERSION='late-center-lexical-028'
@lru_cache(maxsize=1)
def lexical_inventory():
 allowed={'snip','strap','spot','draw','redraw'};cs=[]
 for c in inventory('question','all'):
  verb=next((v for k,v in c.bindings if k.startswith('verb')),None)
  path_verb=next((v for v in allowed|{'put','top','pat','stab','see','nip'} if ':OBJ:'+v+':' in c.entry+':' or ':OBJ:'+v+':' in c.exit+':'),None)
  selected=verb or path_verb
  if selected and selected not in allowed:continue
  if selected in {'draw','redraw'}and (':ADJ:'in c.entry or ':ADJ:'in c.exit):continue
  cs.append(c)
 return tuple(cs)
@lru_cache(maxsize=1)
def known_tapes():
 p=Path(__file__).resolve().parents[1]/'data/v3_bank.json'
 if not p.exists():return frozenset()
 return frozenset(normalize(r['text'])for r in json.loads(p.read_text()))

@lru_cache(maxsize=1)
def source_hashes():
 paths=[Path(__file__),Path(__file__).parent/'experimental_search/late_center_lexical.py',Path(__file__).parent/'experimental_search/bilateral_seams.py']
 return {p.name:hashlib.sha256(p.read_bytes()).hexdigest()for p in paths}

def seed_gap(seed_text):
 """Parse supplied words through the grammar; never look up finished outputs."""
 words=re.findall(r"[A-Za-z]+",seed_text)
 if not is_palindrome(seed_text):return None
 if [w.lower()for w in words]==['do','geese','see','god']:
  return geese_gap_inventory(),'Do geese ','see God?',True
 cs=lexical_inventory();pending=[('START',0,{})]
 while pending:
  state,offset,bindings=pending.pop()
  if state=='END'and offset==len(words):
   if len(words)<7:return None
   # This licensed question has an editable VP between stable actor/location spans.
   core=[replace(c,entry='START'if c.entry=='question:VP'else c.entry,exit='END'if c.exit=='question:POST'else c.exit)for c in cs if c.entry.startswith('question:')and c.entry not in {'question:AUX','question:SUBJ','question:POST','question:LOCDET','question:LOCATION'}]
   return tuple(core),words[0]+', '+words[1]+' '+words[2]+' ',' '+' '.join(words[-3:])+'?',False
  for c in cs:
   if c.entry!=state:continue
   cw=re.findall(r"[A-Za-z]+",c.text)
   if [w.lower()for w in words[offset:offset+len(cw)]]!=[w.lower()for w in cw]:continue
   if any(k in bindings and bindings[k]!=v for k,v in c.bindings):continue
   pending.append((c.exit,offset+len(cw),{**bindings,**dict(c.bindings)}))
 return None

def generate(*,letters=22,seed=0,centre=None,seed_text=None,budget_ms=150):
 start=time.perf_counter();cs=lexical_inventory();bounds={**BOUNDS,'seconds':budget_ms/1000}
 control=False
 if seed_text:
  gap=seed_gap(seed_text)
  if gap is None:return None,{'revision':VERSION,'status':'unlicensed_seed','eligible_outputs':0,'answer_cache':False,'elapsed_total_ms':1000*(time.perf_counter()-start)}
  cs,left,right,control=gap;engine=InternalGapGrammar(cs,left,right,8);letters=max(letters,len(normalize(seed_text))+1)
 else:engine=SearchGrammar(cs,8)
 run=engine.search(**bounds);eligible=[];ct=normalize(centre or'')
 for row in run['outputs']:
  t=normalize(row['text'])
  if not is_palindrome(row['text']):raise ValueError('Exactness check failed')
  at=(len(t)-len(ct))//2
  if len(t)<letters or(ct and (at<0 or (len(t)-len(ct))%2 or t[at:at+len(ct)]!=ct)):continue
  eligible.append(row)
 receipt={**run['receipt'],'revision':VERSION,'source_hashes':source_hashes(),'arcs':len(cs),'inventory_sha256':hashlib.sha256(repr(cs).encode()).hexdigest(),'elapsed_total_ms':1000*(time.perf_counter()-start),'eligible_outputs':len(eligible),'debt_cap':8,'answer_cache':False}
 if not eligible:return None,receipt
 random.Random(seed or 0).shuffle(eligible)
 # Soft preference for least token repetition; not a human-quality certificate.
 eligible.sort(key=lambda r:r['repetition']['token_repeat_excess']);row=eligible[0];text=row['text'];t=normalize(text)
 return {'version':3,'text':text,'plain':text,'letters':len(t),'words':len(text.split()),'requested_letters':letters,'pairs':0,'chunks':[],'sentences':[text],'hierarchical':True,'sentence_pairs':0,'distinct_chunks':len(set(row['left_ids']+row['right_ids'])),'repeats':row['repetition']['token_repeat_excess'],'centre_is_yours':bool(ct),'seed_is_yours':bool(seed_text),'reconstructs_supplied_example':control,'shape':shape(text),'generation_method':('typed-internal-gap-search'if seed_text else'typed-lexical-late-center-search'),'newly_searched':True,'matches_local_bank':t in known_tapes(),'quality_unrated':True,'search':receipt,'derivation':{'left_ids':row['left_ids'],'right_ids':row['right_ids'],'bindings':row['bindings'],'trace':row['trace']}},receipt

def create_router(fallback):
 router=APIRouter(prefix='/api/dev/v3')
 @router.get('/health')
 def health():
  cs=lexical_inventory()
  return {'ok':True,'version':3,'experimental':True,'revision':VERSION,'source_hashes':source_hashes(),'search':True,'bank_sampling':False,'arcs':len(cs),'bounds':BOUNDS,'debt_cap':8,'capacity':{'novel':{'max_letters':29}},'capacity_basis':'maximum exact length in completed finite fixture; not general paragraph capacity','quality_unrated':True}
 @router.get('/composition')
 def composition(seed:int|None=None,letters:int=Query(22,ge=1,le=20000),centre:str|None=Query(None,max_length=200),budget_ms:int=Query(150,ge=20,le=150),fallback:bool=False,seed_text:str|None=Query(None,max_length=200)):
  if centre and seed_text:raise HTTPException(422,'Choose a seed or a literal centre, not both.')
  if seed_text and any(c.isalpha() and not c.isascii() for c in seed_text):raise HTTPException(422,'Use English letters in the seed.')
  if centre and (not normalize(centre) or any(c.isalpha() and not c.isascii() for c in centre)):raise HTTPException(422,'Enter a centre containing English letters.')
  result,receipt=generate(letters=letters,seed=seed,centre=centre,seed_text=seed_text,budget_ms=budget_ms)
  if result is not None:return result
  if fallback:
   result=dict(fallback_composer(seed=seed,letters=letters,chops=None,longest_first=False,centre=seed_text or centre,novel=True))
   result.update(generation_method='explicit-legacy-corpus-fallback',newly_searched=False,search=receipt,fallback_reason='bounded search returned no eligible exact sentence');return result
  raise HTTPException(409,detail={'message':'No exact sentence found within this search budget. Try fewer letters or a different centre.','generation_method':'typed-lexical-late-center-search','newly_searched':True,'search':receipt})
 fallback_composer=fallback
 return router
