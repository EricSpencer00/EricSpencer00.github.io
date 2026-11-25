"""033 factored lexical continuation; frozen role facts, never stored answers."""
import json,re,random,time
from pathlib import Path
from functools import lru_cache
from .bilateral_seams import Chunk
from .composition_030 import CharacterSearch
from .validator import normalize,is_palindrome
LEXICON=json.loads(Path(__file__).with_name('continuation-lexicon.json').read_text())
FOOD=('desserts','meals','cakes','pies','bread');WRITTEN=('mail','letters','notes','reports','messages')
AFFECT=('stressed','tired','angry','sad','calm','happy');PAST=('reviled','praised','helped','warned','called','paid','repaid','rewarded','fed','met')
IMPERATIVE=('refer','help','warn','call','pay','repay','feed');INTRANSITIVE=('lived','sinned','waited','walked','ran','rested')
class FrozenResources:
 def allow(self,word,role):return word in LEXICON['role_words'].get(role,())
def grammar(depth):
 expanded=True
 resources=FrozenResources()
 names=('Noel','Leon','Anna','Eve','Liam')if not expanded else tuple(dict.fromkeys(('Liam','Leon','Noel','Tara','Nora','Tim','Sam','Dan','Ada','Eva')+('Anna','Eve','Dennis','Hannah')))
 names=tuple(w for w in names if resources.allow(w,'human_name'))
 food=tuple(w for w in (FOOD if expanded else('desserts',))if resources.allow(w,'NOUN'))
 written=tuple(w for w in (WRITTEN if expanded else('mail',))if resources.allow(w,'NOUN'))
 affect=tuple(w for w in (AFFECT if expanded else('stressed',))if resources.allow(w,'ADJ'))
 past=tuple(w for w in (PAST if expanded else('reviled',))if resources.allow(w,'VERB'))
 verbs=tuple(w for w in (IMPERATIVE if expanded else('refer',))if resources.allow(w,'VERB'))
 frames=[('recipient_food',[('human_name',names),('VERB',('deliver',)),('human_name',names),('NOUN',food)],True),('written_delivery',[('human_name',names),('VERB',('deliver',)),('NOUN',written)],True),('human_imperative',[('human_name',names),('VERB',verbs),('human_name',names)],True),('affected_reaction',[('ADJ',affect),('human_name',names),('VERB',past),('human_name',names)],False),('human_past',[('human_name',names),('VERB',past),('human_name',names)],False)]
 if expanded:
  iv=tuple(w for w in INTRANSITIVE if resources.allow(w,'VERB'));quality=tuple(w for w in ('ready','tired','angry','sad','calm','happy')if resources.allow(w,'ADJ'))
  frames.extend([('human_intransitive',[('human_name',names),('VERB',iv)],False),('human_copula',[('human_name',names),('VERB',('is',)),('ADJ',quality)],False)])
 for word in ('deliver','is'):assert resources.allow(word,'VERB')
 out=[]
 for i in range(depth):
  start='START'if i==0 else f's{i}';end='END'if i==depth-1 else f's{i+1}'
  for fi,(label,slots,vocative)in enumerate(frames):
   if any(not words for _,words in slots):continue
   for j,(role,words)in enumerate(slots):
    a=start if j==0 else f's{i}:f{fi}:slot{j}';b=end if j==len(slots)-1 else f's{i}:f{fi}:slot{j+1}'
    for word in words:
     first=word[0].upper()+word[1:]if j==0 else word
     ending=('. 'if end!='END'else'.')if j==len(slots)-1 else', 'if vocative and j==0 else' '
     out.append(Chunk('c'+str(len(out)),first+ending,a,b,f'{label}: {role}',f'032 independent lexical slots; {"expanded"if expanded else"inherited-control"}',((f'frame{i}',label),)))
 return tuple(out)

@lru_cache(maxsize=4)
def compiled(depth):return CharacterSearch(grammar(depth))

def events(row):
 sentences=[s.strip()for s in row['text'].split('.')if s.strip()];out=[]
 for i,s in enumerate(sentences):
  w=re.findall('[A-Za-z]+',s);frame=row['bindings'][f'frame{i}'];e={'frame':frame,'text':s+'.','words':w}
  if frame=='recipient_food':e.update(actor=w[0],patient=w[2],object=w[3])
  elif frame=='written_delivery':e.update(actor=w[0],object=w[2])
  elif frame=='human_imperative':e.update(actor=w[0],patient=w[2])
  elif frame=='affected_reaction':e.update(actor=w[1],patient=w[3],affect=w[0])
  elif frame=='human_past':e.update(actor=w[0],patient=w[2])
  else:e.update(actor=w[0])
  out.append(e)
 return out

def assess(row):
 es=events(row);sentences=[e['text']for e in es];self_ref=[e for e in es if e.get('patient')==e['actor']]
 requested={e['patient']for e in es if e['frame']=='recipient_food'};affected={e['actor']for e in es if e['frame']=='affected_reaction'}
 people={e['actor']for e in es}|{e['patient']for e in es if 'patient'in e}
 return {'events':es,'duplicate_sentences':len(sentences)-len(set(sentences)),'unlicensed_self_reference':self_ref,'linked_recipient_affect_pairs':len(requested&affected),'distinct_named_people':len(people),'quality_unrated':True}

def search(*,target,seed,seconds=.15,exclude_id=None):
 start=time.perf_counter();runs=[];rejected=[];found=[]
 for depth in sorted((2,4,6,8),key=lambda d:abs(d-target/24)):
  g=compiled(depth);b=g.remaining_chars('START','END')
  if b[1]<target-10 or b[0]>target+10:continue
  remaining=seconds-(time.perf_counter()-start)
  if remaining<=0:break
  run=g.search(seed=seed+depth,low_chars=max(24,target-10),high_chars=min(1200,target+10),seconds=remaining,max_states=5000,max_outputs=16,max_steps=80,exclude_id=exclude_id)
  runs.append({'depth':depth,**run['receipt']})
  for row in run['outputs']:
   f=assess(row);row.update(features=f,depth=depth)
   if f['unlicensed_self_reference']:rejected.append({'text':row['text'],'reason':'unlicensed_self_reference','events':f['unlicensed_self_reference']})
   elif f['duplicate_sentences']:rejected.append({'text':row['text'],'reason':'repeated_full_sentence'})
   else:found.append(row)
  if found:break
 rng=random.Random(seed);rng.shuffle(found)
 found.sort(key=lambda r:(-r['features']['linked_recipient_affect_pairs'],r['features']['distinct_named_people'],abs(len(r['text'])-target)))
 receipt={'method':'linked-clause-word-search033','seed':seed,'runs':runs,'rejected':rejected,'eligible_outputs':len(found),'answer_cache':False,'lexical_input_hashes':LEXICON['resource_hashes'],'quality_ranking':'prefer shared prospective recipient/affected person, fewer people, then target distance; not a human label','elapsed_ms':1000*(time.perf_counter()-start)}
 if not found:return None,receipt
 row=found[0];assert is_palindrome(row['text']);assert abs(len(row['text'])-target)<=10
 return row,receipt
