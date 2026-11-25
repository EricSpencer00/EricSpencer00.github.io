import unittest,re
from .dev_real_search import generate_characters
from .experimental_search.continuations_033 import compiled,assess,LEXICON
from .experimental_search.validator import normalize,is_palindrome
class LinkedTests(unittest.TestCase):
 def forward_accepts(self,cs,text):
  tokens=re.findall('[A-Za-z]+|[.!?]',text);stack=[('START',0,{})]
  while stack:
   state,at,b=stack.pop()
   if state=='END'and at==len(tokens):return True
   for c in cs.out[state]:
    words=re.findall('[A-Za-z]+|[.!?]',c.text)
    if [w.lower()for w in tokens[at:at+len(words)]]!=[w.lower()for w in words]:continue
    if any(k in b and b[k]!=v for k,v in c.bindings):continue
    stack.append((c.exit,at+len(words),{**b,**dict(c.bindings)}))
  return False
 def test_fresh_seed_length_distribution_and_independent_forward_parse(self):
  ids=set();linked=0
  for target in [100,140,180]:
   for seed in range(3301,3309):
    row,receipt=generate_characters(characters=target,seed=seed)
    self.assertIsNotNone(row);self.assertTrue(is_palindrome(row['text']));self.assertLessEqual(abs(len(row['text'])-target),10);ids.add(normalize(row['text']))
    if row['generation_method']=='linked-clause-word-search033':
     linked+=1;self.assertFalse(row['features']['unlicensed_self_reference']);self.assertEqual(row['features']['duplicate_sentences'],0);self.assertTrue(self.forward_accepts(compiled(row['construction_depth']),row['text']))
  self.assertGreaterEqual(linked,20);self.assertGreater(len(ids),18)
 def test_no_complete_answer_inventory_and_reproducible_lexical_input(self):
  self.assertFalse(LEXICON['contains_completed_sentences']);self.assertNotIn('sentences',LEXICON)
  a,_=generate_characters(characters=140,seed=3305);b,_=generate_characters(characters=140,seed=3305)
  self.assertEqual(a['text'],b['text']);self.assertEqual(a['derivation'],b['derivation'])
 def test_identity_failure_is_rejected_and_prior_result_excluded(self):
  row={'text':'Stressed Hannah reviled Hannah.','bindings':{'frame0':'affected_reaction'}};self.assertTrue(assess(row)['unlicensed_self_reference'])
  a,_=generate_characters(characters=140,seed=3305);b,_=generate_characters(characters=140,seed=3305,exclude_id=a['result_id']);self.assertIsNotNone(b);self.assertNotEqual(a['result_id'],b['result_id'])
 def test_030_seed_and_long_cap_are_preserved_and_labelled(self):
  a,_=generate_characters(characters=100,seed=30,seed_text='Do geese see God?');self.assertIsNotNone(a);self.assertIn(normalize('Do geese see God?'),normalize(a['text']))
  b,_=generate_characters(characters=1200,seed=1);self.assertIsNotNone(b);self.assertTrue(1190<=b['characters']<=1200);self.assertTrue(b['search']['retained_030_route']);self.assertEqual(b['quality_caption'],'experimental nested dialogue')
 def test_shape_preserves_every_punctuation_mark(self):
  r,_=generate_characters(characters=140,seed=3305);s=r['shape'];words=s['left']+([s['centerDisplay']]if s['centerDisplay']else[])+s['right'];self.assertEqual(' '.join(words),r['text']);self.assertIn(',',r['text']);self.assertTrue(s['punctuated'])
if __name__=='__main__':unittest.main()
