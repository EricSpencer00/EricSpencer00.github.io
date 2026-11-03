import unittest,random,re
from .experimental_search.bilateral_seams import Chunk
from .experimental_search.composition_029 import GlobalSearch,grammar,graph,features,memo_grammar
from .experimental_search.validator import normalize

def forward(cs):
 out={};paths=[]
 for c in cs:out.setdefault(c.entry,[]).append(c)
 stack=[('START','',{})]
 while stack:
  state,text,b=stack.pop()
  if state=='END':paths.append(text);continue
  for c in out.get(state,[]):
   if any(k in b and b[k]!=v for k,v in c.bindings):continue
   n={**b,**dict(c.bindings)};topics=[v for k,v in n.items()if k.startswith('outer_topic')]
   if len(topics)!=len(set(topics)):continue
   stack.append((c.exit,text+c.text,n))
 return paths

def exact(s):
 t=''.join(c.lower()for c in s if 'a'<=c.lower()<='z');return bool(t)and all(t[i]==t[-1-i]for i in range(len(t)//2))
class CompositionTests(unittest.TestCase):
 def test_heldout_global_oracle(self):
  for depth in [1,2,3]:
   for verb in ['strap','spot','redraw']:
    cs=grammar(depth,('Aziza','Anina'),(verb,),('draw','snip'))
    expected={normalize(t)for t in forward(cs)if exact(t)}
    run=GlobalSearch(cs).search(seed=29000,seconds=.15,audit=True)
    self.assertEqual(run['receipt']['status'],'complete');self.assertEqual({normalize(x['text'])for x in run['outputs']},expected)
 def test_100_independent_synthetic_dags(self):
  rng=random.Random(29019)
  for i in range(100):
   cs=[]
   for state in range(4):
    for j in range(rng.randint(1,3)):
     word=''.join(rng.choice('abc')for _ in range(rng.randint(1,3)));cs.append(Chunk(str(len(cs)),word,'START'if state==0 else str(state),'END'if state==3 else str(state+1),'synthetic role','independent synthetic test'))
   want={normalize(s)for s in forward(cs)if exact(s)};run=GlobalSearch(cs).search(seed=i)
   self.assertEqual(run['receipt']['status'],'complete');self.assertEqual({normalize(x['text'])for x in run['outputs']},want)
 def test_target_eligibility_before_output_cap(self):
  cs=(Chunk('a','a','START','END','word','test'),Chunk('b','racecar','START','END','word','test'))
  for seed in range(8):
   r=GlobalSearch(cs).search(seed=seed,low=6,high=8,max_outputs=1);self.assertEqual([x['text']for x in r['outputs']],['racecar'])
 def test_indexed_vs_unindexed_complete_sets(self):
  g=GlobalSearch(grammar(2,('Anna','Bob'),('draw',),('snip',)))
  a=g.search(seed=29,indexed=False);b=g.search(seed=29,indexed=True)
  self.assertEqual({normalize(x['text'])for x in a['outputs']},{normalize(x['text'])for x in b['outputs']})
 def test_seed_reproduction_varied_traversal_and_longer_tapes(self):
  g=graph(2);a=g.search(seed=29004,low=40,high=60);b=g.search(seed=29004,low=40,high=60)
  self.assertEqual([x['text']for x in a['outputs']],[x['text']for x in b['outputs']]);self.assertTrue(all(40<=x['letters']<=60 and exact(x['text'])for x in a['outputs']))
  c=g.search(seed=29005,low=40,high=60);self.assertNotEqual([x['text']for x in a['outputs']],[x['text']for x in c['outputs']])
 def test_full_string_append_and_nonaba_seam(self):
  a='Did Anna snip pins? Anna did.';b='Did Bob draw a ward? Bob did.'
  self.assertTrue(exact(a));self.assertTrue(exact(b));self.assertFalse(exact(a+b));self.assertTrue(exact(a+b+a))
  merged='Did Anna snip? '+b+' Pins? Anna did.';self.assertTrue(exact(merged));self.assertGreater(len(normalize(merged)),40);self.assertNotIn(a,merged);self.assertNotEqual(normalize(merged),normalize(a+b+a))
 def test_argument_constraints_and_fragment_disclosure(self):
  r=graph(3).search(seed=29002,low=65,high=83)
  self.assertTrue(r['outputs'])
  for x in r['outputs']:
   b=x['bindings'];self.assertNotEqual(b['outer_topic0'],b['outer_topic1']);f=features(x['text'],b);self.assertTrue(f['contains_clarification_fragments']);self.assertTrue(exact(x['text']))
 def test_nonpalindromic_actor_control_does_not_change_person(self):
  g=GlobalSearch(grammar(1,('Nora','Aron'),('snip',),('snip',)));r=g.search();self.assertEqual(r['outputs'],[]);self.assertEqual(r['receipt']['status'],'complete')
 def test_independent_memo_family(self):
  paths=forward(memo_grammar());want={normalize(t)for t in paths if exact(t)};r=graph(0).search()
  self.assertEqual({normalize(x['text'])for x in r['outputs']},want);self.assertEqual(len(want),1)
if __name__=='__main__':unittest.main()
