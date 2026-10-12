import unittest,hashlib
from fastapi import FastAPI
from fastapi.testclient import TestClient
from .dev_real_search import create_router,generate
from .experimental_search.validator import normalize,is_palindrome
class SearchEndpointTests(unittest.TestCase):
 def setUp(self):
  self.calls=[]
  def legacy(**kw):self.calls.append(kw);return {'text':'Never odd or even','letters':14}
  a=FastAPI();a.include_router(create_router(legacy));self.c=TestClient(a)
 def test_real_search_provenance_and_longer_than40(self):
  r=self.c.get('/api/dev/v3/composition?letters=51&seed=29').json();self.assertTrue(is_palindrome(r['text']));self.assertGreater(r['letters'],40);self.assertTrue(r['newly_searched']);self.assertFalse(r['search']['answer_cache']);self.assertTrue(r['derivation']['trace']);self.assertFalse(self.calls)
  self.assertTrue(r['composition']['whole_output_exact']);self.assertFalse(r['composition']['plain_append_exact']);self.assertTrue(all(x['exact']for x in r['composition']['components']))
 def test_window_clamps_and_applies_before_output_cap(self):
  for request in [-500,16,29,51,10000]:
   r=self.c.get('/api/dev/v3/composition',params={'letters':request,'seed':29011}).json();self.assertEqual(r['target_letters'],max(16,min(57,request)));self.assertLessEqual(abs(r['letters']-r['target_letters']),10)
 def test_repeated_requests_varied_tapes_not_punctuation(self):
  rows=[self.c.get('/api/dev/v3/composition',params={'letters':29,'seed':s}).json()for s in range(29010,29018)];self.assertGreater(len({normalize(r['text'])for r in rows}),3);self.assertGreater(len({r['letters']for r in rows}),2)
  a=self.c.get('/api/dev/v3/composition?letters=29&seed=29010').json();b=self.c.get('/api/dev/v3/composition?letters=29&seed=29010').json();self.assertEqual(a['text'],b['text']);self.assertEqual(a['derivation'],b['derivation'])
 def test_seedless_interactive_and_previous_exclusion(self):
  a=self.c.get('/api/dev/v3/composition?letters=29').json();b=self.c.get('/api/dev/v3/composition',params={'letters':29,'seed':a['search']['seed'],'exclude_id':a['result_id']}).json();self.assertNotEqual(normalize(a['text']),normalize(b['text']))
 def test_no_result_and_no_silent_fallback(self):
  r=self.c.get('/api/dev/v3/composition?letters=51&centre=zzzz');self.assertEqual(r.status_code,409);self.assertFalse(self.calls);self.assertEqual(r.json()['detail']['search']['eligible_outputs'],0)
 def test_explicit_fallback_parameters(self):
  r=self.c.get('/api/dev/v3/composition?letters=1200&seed=7&seed_text=hello&fallback=true').json();self.assertFalse(r['newly_searched']);self.assertEqual(r['generation_method'],'explicit-legacy-corpus-fallback');self.assertEqual(self.calls,[{'seed':7,'letters':1200,'chops':None,'longest_first':False,'centre':'hello','novel':True}])
 def test_budget_and_health(self):
  self.assertEqual(self.c.get('/api/dev/v3/composition?budget_ms=151').status_code,422);h=self.c.get('/api/dev/v3/health').json();self.assertEqual(h['revision'],'global-composition-029');self.assertEqual(h['length_window'],10);self.assertEqual(h['capacity']['novel']['max_letters'],57);self.assertFalse(h['bank_sampling'])
 def test_punctuation_case_and_true_letter_center(self):
  r=self.c.get('/api/dev/v3/composition?letters=51&seed=29').json();s=r['shape'];tokens=s['left']+([s['centerDisplay']]if s['centerDisplay']else[])+s['right'];self.assertEqual(' '.join(tokens),r['text']);self.assertIn('?',r['text']);self.assertIn('.',r['text']);self.assertTrue(r['text'].startswith('Did '));self.assertTrue(s['punctuated'])
  before=len(normalize(' '.join(s['left'])));raw=s['centerDisplay'];offset=len(normalize(raw[:s['pivot']]));self.assertEqual(before+offset,r['letters']//2)
 def test_geese_control_shift_and_unavailable_long_window(self):
  r=self.c.get('/api/dev/v3/composition',params={'letters':29,'seed_text':'Do geese see god'}).json();self.assertEqual(r['text'],'Do geese on a cedar trade canoe see God?');self.assertEqual(r['shape']['centerDisplay'],'trade');self.assertEqual(r['shape']['pivot'],0);self.assertFalse(r['centre_is_yours']);self.assertTrue(r['reconstructs_supplied_example']);self.assertEqual(self.c.get('/api/dev/v3/composition',params={'letters':51,'seed_text':'Do geese see god'}).status_code,409)
 def test_complete_result_seed_retained_with_new_seam(self):
  text='Did Anna snip pins? Anna did.';r=self.c.get('/api/dev/v3/composition',params={'letters':51,'seed_text':text,'seed':29}).json();self.assertTrue(r['composition']['complete_seed_tape_preserved']);self.assertEqual(normalize(r['composition']['components'][0]['text']),normalize(text));self.assertGreater(r['letters'],40);self.assertFalse(r['centre_is_yours'])
 def test_legacy_fragment_recomposition_disclosed(self):
  r=self.c.get('/api/dev/v3/composition',params={'letters':51,'seed_text':'Eva, can I strap level parts in a cave?','seed':29}).json();self.assertGreater(r['letters'],40);self.assertFalse(r['composition']['complete_seed_tape_preserved']);self.assertIn('fragments',r['seed_semantics']);self.assertEqual(r['removed_seed_modifiers'],['level'])
 def test_invalid_inputs_and_no_false_search_claim(self):
  self.assertEqual(self.c.get('/api/dev/v3/composition?seed_text=é').status_code,422);r=self.c.get('/api/dev/v3/composition?seed_text=hello');self.assertEqual(r.status_code,409);self.assertFalse(r.json()['detail']['newly_searched'])
if __name__=='__main__':unittest.main()
