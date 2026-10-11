"""Compile audited corpus spans and selected-seed editable windows.
No generated complete candidate or held-out target is an input.
"""
import argparse,json,hashlib,sys
from pathlib import Path
from dataclasses import asdict
from palindrome_phrase_compiler import PhraseRule,compile_phrase_rules
ROOT=Path(__file__).resolve().parents[1]
norm=lambda s:''.join(c for c in s.lower() if 'a'<=c<='z')

def compile_all(corpus,research_root=None):
 rows={r['id']:r for r in corpus['examples']};fragments={}
 def span(key,donor,surface,role,*,lower=False,prefix=None):
  text=rows[donor]['text'];start=text.index(surface);stop=start+len(surface)
  if prefix is not None:stop=start+prefix
  original=text[start:stop];rendered=original.lower() if lower else original
  if key in ('v:rip','subject:men','subject:editors'): rendered += ' '
  fragments[key]={'id':key,'text':rendered,'source':donor,'start':start,'end':stop,'original':original,'role':role,'case_transform':'lower' if lower else 'identity','separator_after':key in ('v:rip','subject:men','subject:editors')}
  return rendered
 span('v:suss','suss','suss ','base transitive inspect verb')
 span('v:tap','tap','tap ','base contact verb')
 span('v:draw','ward','Draw ','imperative/base depict verb',lower=True)
 span('v:see','geese','see ','base perception verb')
 span('v:rip','aide','rips','third-singular tear verb; strip agreement s',prefix=3)
 for key,donor,phrase,role in [('np:Pat','tap','Pat','person name'),('np:Diana','aide','Diana','person name'),
  ('np:aide','aide','An aide','indefinite person NP'),('np:men','suss','Some men','indefinite people NP'),
  ('np:ward','ward','a ward','indefinite institution NP'),('np:mock','mock','a mock coma ward','indefinite institution NP')]:
  span(key,donor,phrase,role,lower=key in ('np:aide','np:men'))
 span('genitive','tap',"'s ",'possessive clitic; singular/irregular plural owner')
 span('prep:on','geese','on ','preposition; contact target adapter')
 span('draw:original','ward','ward. I draw ','preserved imperative object and first-person clause opening')
 span('draw:modifier','mock','mock coma ','medical institution qualifier')
 span('draw:ward','ward','ward. ','preserved imperative object and clause boundary')
 span('draw:subject','ward','I draw a ','first-person depict clause and object determiner')
 span('draw:partial','mock','mock coma','qualifier with final a borrowed from retained right seam',prefix=8)
 for key,donor,phrase in [('subject:I','ward','I '),('subject:men','suss','Some men'),('subject:editors','suss','editors')]:
  span(key,donor,phrase,'human subject compatible with retained base draw')
 plans=[];parity=[]
 for sid in ['tap','suss','ward','mock']:
  text=rows[sid]['text']
  if sid=='suss':start=text.index('suss ');end=start+len('suss ')
  elif sid=='tap':start=end=text.index('Pat')
  elif sid=='ward':start=text.index('ward.');end=text.rindex('a ward.')
  else:start=text.index('I ');end=start+2
  prefix,suffix=text[:start],text[end:];l,r=norm(prefix),norm(suffix)[::-1];matched=min(len(l),len(r))
  if l[:matched]!=r[:matched]:raise ValueError('immutable context mismatch')
  left=l[matched:];right=r[matched:][::-1]
  # Retained unequal contexts belong in the grammar, not a palindrome-only
  # requirement on the editable surface. These arcs render no new text.
  ws='W_START' if left else 'START';we='W_END' if right else 'END'
  bindings=(('subject','editors1'),('object','roti1'),('document','memos1')) if sid in ('tap','suss') else (('imperative_agent','addressee1'),('statement_agent','speaker1'),('object','ward1'))
  rules=[];path_groups=[]
  def add(entry,exit,fragment,role=None,extra=()):
   f=fragments[fragment];source=json.dumps({'donor':f['source'],'start':f['start'],'end':f['end'],'fragment':fragment},sort_keys=True)
   rule=PhraseRule(entry,exit,f['text'],role or f['role'],bindings+extra,source);rules.append(rule);return rule
  if left:rules.append(PhraseRule('START',ws,left,'retained left-context residual',bindings,json.dumps({'retained':'prefix','seed':sid})))
  if right:rules.append(PhraseRule(we,'END',right,'retained right-context residual',bindings,json.dumps({'retained':'suffix','seed':sid})))
  if sid=='suss':
   # Source verbs share base-form plural agreement. Owners are human or
   # institutional NPs; all branches still take the literal retained roti.
   for verb in ['v:suss','v:tap','v:draw','v:see','v:rip']:
    bare=add(ws,we,verb);path_groups.append([bare])
    add(ws,'OWNER',verb)
   for owner in ['np:Pat','np:Diana','np:aide','np:men','np:ward','np:mock']:
    add('OWNER','POSS',owner,extra=(('owner',owner),))
   add('POSS',we,'genitive')
   for verb in ['v:suss','v:tap','v:draw','v:see','v:rip']:
    for owner in ['np:Pat','np:Diana','np:aide','np:men','np:ward','np:mock']:
     path_groups.append([PhraseRule(ws,'OWNER',fragments[verb]['text'],fragments[verb]['role'],bindings,''),
      PhraseRule('OWNER','POSS',fragments[owner]['text'],fragments[owner]['role'],bindings+(('owner',owner),),''),
      PhraseRule('POSS',we,fragments['genitive']['text'],fragments['genitive']['role'],bindings,'')])
  elif sid=='tap':add(ws,we,'prep:on')
  elif sid=='ward':
   original=add(ws,we,'draw:original');path_groups.append([original])
   for entry,exit,f in [(ws,'D1','draw:modifier'),('D1','D2','draw:ward'),('D2','D3','draw:subject'),('D3',we,'draw:partial')]:add(entry,exit,f)
  else:
   for f in ['subject:I','subject:men','subject:editors']:add(ws,we,f)
  interfaces={(r.entry,r.exit) for r in rules}
  chunks=compile_phrase_rules(sid,rules,interfaces)
  if research_root:
   sys.path.insert(0,str(research_root))
   from llm_palindrome.typed_phrase_compiler import PhraseRule as ReferenceRule,compile_phrase_rules as reference_compile
   reference=[asdict(c) for c in reference_compile(sid,[ReferenceRule(**asdict(r)) for r in rules],interfaces)]
   assert reference==[asdict(c) for c in chunks]
   parity.append({'seed':sid,'chunks':len(chunks),'identical_to_existing_research_compiler':True})
  # Constituent regrouping is an explicit alternative, not an impossibility
  # claim inferred from a word/chunk-dependent operational debt cap.
  grouped=[]
  if sid=='suss':
   for path in path_groups:
    b={}
    for rule in path:b.update(dict(rule.bindings))
    grouped.append(PhraseRule(ws,we,''.join(r.text for r in path),'regrouped partial transitive VP; retained roti completes object',tuple(sorted(b.items())),json.dumps({'regrouped':True,'seed':sid,'leaf_fragments':[f['id'] for f in fragments.values() if any(r.text == f['text'] for r in path)]})))
   grouped=[r for r in rules if 'retained' in r.role]+grouped
  else:grouped=rules
  groups=compile_phrase_rules(sid,grouped,{(r.entry,r.exit) for r in grouped})
  plans.append({'seed_id':sid,'seed_text':text,'start':start,'end':end,'prefix':prefix,'suffix':suffix,'original_window':text[start:end],
   'left_residual':left,'right_residual':right,'seam_debt':{'side':'left' if left else 'right' if right else 'none','letters':left or right[::-1]},
   'allow_empty':sid=='tap','window_type':{'suss':'transitive action plus optional possessor; retain food and outer clause','tap':'target-preposition insertion; retain tap, Pat and roti','ward':'central drawing phrase; retain outside text and ward/I/draw roles','mock':'subject NP only; retain both mock-coma-ward clauses'}[sid],
   'chunks':[asdict(c) for c in chunks],'grouped_chunks':[asdict(c) for c in groups]})
 return {'schema':1,'corpus':corpus,'fragments':list(fragments.values()),'plans':plans,'compiler_parity':parity,
  'license':'Owner-audited source spans, narrow grammar and declared semantic adapters; not an automatic English parser or readability certificate.'}

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--research-root',type=Path);parser.add_argument('--check',action='store_true');args=parser.parse_args()
 corpus=json.loads((ROOT/'palindrome-v3/approved-corpus.json').read_text());value=compile_all(corpus,args.research_root)
 output=ROOT/'palindrome-v3/compiled-windows.json'
 if args.check:
  previous=json.loads(output.read_text());value['compiler_parity']=previous['compiler_parity'];assert previous==json.loads(json.dumps(value))
 else:output.write_text(json.dumps(value,indent=2)+'\n')
 print(json.dumps({'plans':len(value['plans']),'fragments':len(value['fragments']),'parity':value['compiler_parity']}))
if __name__=='__main__':main()
