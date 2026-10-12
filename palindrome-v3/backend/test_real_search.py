import unittest,time
from fastapi import FastAPI
from fastapi.testclient import TestClient
from .dev_real_search import create_router,generate
class SearchEndpointTests(unittest.TestCase):
 def setUp(self):
  self.calls=[]
  def legacy(**kwargs):self.calls.append(kwargs);return {'text':'Never odd or even','letters':14}
  app=FastAPI();app.include_router(create_router(legacy));self.client=TestClient(app)
 def test_real_search_and_provenance(self):
  response=self.client.get('/api/dev/v3/composition?letters=22&seed=28');self.assertEqual(response.status_code,200)
  r=response.json();t=''.join(c.lower()for c in r['text']if c.isalpha());self.assertEqual(t,t[::-1]);self.assertTrue(r['newly_searched']);self.assertFalse(r['search']['answer_cache']);self.assertTrue(r['derivation']['trace']);self.assertFalse(self.calls)
 def test_no_silent_bank_fallback(self):
  r=self.client.get('/api/dev/v3/composition?letters=1200');self.assertEqual(r.status_code,409);self.assertFalse(self.calls);self.assertEqual(r.json()['detail']['search']['eligible_outputs'],0)
 def test_explicit_fallback_provenance_and_parameters(self):
  r=self.client.get('/api/dev/v3/composition?letters=1200&seed=7&fallback=true').json();self.assertFalse(r['newly_searched']);self.assertEqual(r['generation_method'],'explicit-legacy-corpus-fallback');self.assertEqual(self.calls,[{'seed':7,'letters':1200,'chops':None,'longest_first':False,'centre':None,'novel':True}])
 def test_budget_limits_and_health(self):
  self.assertEqual(self.client.get('/api/dev/v3/composition?budget_ms=151').status_code,422)
  h=self.client.get('/api/dev/v3/health').json();self.assertTrue(h['search']);self.assertFalse(h['bank_sampling']);self.assertEqual(h['revision'],'late-center-lexical-028')
 def test_shifted_seed_and_no_complete_answer_inputs(self):
  r=self.client.get('/api/dev/v3/composition',params={'seed_text':'Do geese see god'}).json()
  self.assertEqual(r['text'],'Do geese on a cedar trade canoe see God?');self.assertEqual(r['generation_method'],'typed-internal-gap-search');self.assertFalse(r['centre_is_yours']);self.assertTrue(r['seed_is_yours']);self.assertTrue(r['reconstructs_supplied_example'])
  self.assertEqual(r['search']['arcs'],17)
  self.assertEqual(self.client.get('/api/dev/v3/composition',params={'seed_text':'No rider sees Leon'}).status_code,409)
 def test_typed_seed_recomposition_grows_and_keeps_outer_roles(self):
  result,receipt=generate(seed_text='Eva, can I snip pins in a cave?',seed=28)
  self.assertGreater(result['letters'],22);self.assertTrue(result['text'].startswith('Eva, can I '));self.assertTrue(result['text'].endswith(' in a cave?'));self.assertTrue(result['seed_is_yours']);self.assertFalse(result['reconstructs_supplied_example'])
 def test_center_alignment_and_ascii(self):
  r=self.client.get('/api/dev/v3/composition?centre=é').status_code;self.assertEqual(r,422)
  result,receipt=generate(letters=1,centre='pins',seed=7)
  if result:
   t=''.join(c.lower()for c in result['text']if c.isalpha());at=(len(t)-4)//2;self.assertEqual((len(t)-4)%2,0);self.assertEqual(t[at:at+4],'pins')
if __name__=='__main__':unittest.main()
