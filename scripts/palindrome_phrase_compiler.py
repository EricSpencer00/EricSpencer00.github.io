"""Small standalone port of the existing research typed_phrase_compiler.
Original: palindrome-sentence-generator/llm_palindrome/typed_phrase_compiler.py.
The build verifies parity against that implementation when --research-root
is supplied. This port removes the separate-repository import dependency.
"""
from dataclasses import dataclass
from hashlib import sha256

@dataclass(frozen=True)
class PhraseRule:
 entry:str
 exit:str
 text:str
 role:str
 bindings:tuple
 source:str

@dataclass(frozen=True)
class Chunk:
 id:str
 text:str
 entry:str
 exit:str
 role:str
 source:str
 bindings:tuple=()

def compile_phrase_rules(plan_id,rules,licensed_interfaces):
 out={}
 for r in rules:
  if (r.entry,r.exit) not in licensed_interfaces:raise ValueError('unlicensed syntactic interface')
  binding=dict(r.bindings)
  if len(binding)!=len(r.bindings):raise ValueError('duplicate feature key')
  key=(r.entry,r.exit,r.text,tuple(sorted(r.bindings)))
  cid='rule-'+sha256(repr((plan_id,key)).encode()).hexdigest()[:16]
  entry=r.entry if r.entry=='START' else plan_id+':'+r.entry
  exit=r.exit if r.exit=='END' else plan_id+':'+r.exit
  out[key]=Chunk(cid,r.text,entry,exit,r.role,r.source,r.bindings)
 return list(out.values())
