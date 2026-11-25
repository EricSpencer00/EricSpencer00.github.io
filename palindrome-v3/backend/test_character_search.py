import unittest,random
from fastapi import FastAPI
from fastapi.testclient import TestClient
from .experimental_search.bilateral_seams import Chunk
from .experimental_search.composition_030 import CharacterSearch,grammar030,verified_insertion
from .experimental_search.validator import normalize,is_palindrome
from .dev_real_search import generate_characters,create_router,compiled_characters
from .test_global_search import forward,exact
class CharacterTests(unittest.TestCase):
 def test_character_bounds_against_100_independent_forward_oracles(self):
  rng=random.Random(30)
  for i in range(100):
   cs=[]
   for state in range(3):
    for _ in range(rng.randint(1,3)):
     text=''.join(rng.choice('abc')for _ in range(rng.randint(1,3)))+rng.choice(['','? ','!'])
     cs.append(Chunk(str(len(cs)),text,'START'if state==0 else str(state),'END'if state==2 else str(state+1),'independent fixture','test'))
   lo,hi=sorted([rng.randint(1,12),rng.randint(1,12)])
   want={normalize(t)for t in forward(cs)if exact(t)and lo<=len(t)<=hi}
   r=CharacterSearch(cs).search(seed=i,low_chars=lo,high_chars=hi)
   self.assertEqual(r['receipt']['status'],'complete');self.assertEqual({normalize(x['text'])for x in r['outputs']},want)
 def test_shared_input_graph_is_safe_for_concurrent_requests(self):
  from concurrent.futures import ThreadPoolExecutor
  g=CharacterSearch(grammar030(2,names=('Anna','Bob'),verbs=('snip',),outer=('strap',)))
  with ThreadPoolExecutor(max_workers=2)as pool:runs=list(pool.map(lambda seed:g.search(seed=seed,max_outputs=100),[1,2]))
  self.assertEqual({normalize(x['text'])for x in runs[0]['outputs']},{normalize(x['text'])for x in runs[1]['outputs']})
 def test_actual_word_search_reaches_100_letters(self):
  r=CharacterSearch(grammar030(4)).search(seed=1,low=100,high=130,max_steps=40,max_outputs=3)
  self.assertTrue(r['outputs'])
  for x in r['outputs']:
   self.assertGreaterEqual(len(normalize(x['text'])),100);self.assertTrue(is_palindrome(x['text']));self.assertTrue(x['trace'])
 def test_100_displayed_characters_with_canonical_paragraph_break(self):
  actors=(('Anna',),('Hannah',),('Bob',));r=CharacterSearch(grammar030(3,actors=actors,paragraph_break=True)).search(seed=30,low_chars=100,high_chars=100,max_steps=40)
  self.assertTrue(r['outputs']);self.assertTrue(all(len(x['text'])==100 and is_palindrome(x['text'])for x in r['outputs']))
 def test_unreachable_char_length_never_returns_short_fallback(self):
  r=CharacterSearch(grammar030(1)).search(low_chars=1000,high_chars=1200);self.assertEqual(r['outputs'],[]);self.assertEqual(r['receipt']['status'],'complete')
 def test_mirrored_insertion_and_partial_offsets(self):
  r=verified_insertion('abba','xy','yx',1,3);self.assertEqual(r['text'],'axybbyxa');self.assertTrue(is_palindrome(r['text']));self.assertFalse(r['grammar_verified'])
  r=verified_insertion('abba','eve','eve',1,3);self.assertEqual(r['kind'],'symmetric-end-to-end-blocks')
  r=verified_insertion('abba','eve','eve',2,2);self.assertTrue(is_palindrome(r['text']))
  for args in [('abba','xy','xy',1,3),('abba','xy','yx',1,2),('hello','xy','yx',1,4)]:
   with self.assertRaises(ValueError):verified_insertion(*args)
 def test_actor_identity_not_reversed_into_a_different_person(self):
  r=CharacterSearch(grammar030(1,names=('Nora','Aron'),verbs=('snip',))).search();self.assertEqual(r['outputs'],[])
 def test_character_route_units_count_and_validation(self):
  app=FastAPI();app.include_router(create_router(lambda **kw:None));c=TestClient(app)
  r=c.get('/api/dev/v3/composition?characters=140&seed=30').json();self.assertEqual(r['length_unit'],'displayed_characters');self.assertEqual(r['characters'],len(r['text']));self.assertEqual(r['letters'],len(normalize(r['text'])));self.assertLessEqual(abs(r['characters']-140),10)
  self.assertEqual(c.get('/api/dev/v3/composition?characters=1201').status_code,422)
  self.assertEqual(c.get('/api/dev/v3/composition?characters=100&seed_text=hello').status_code,409)
  self.assertEqual(c.get('/api/dev/v3/health').json()['capacity']['novel']['max_characters'],1200)
 def test_licensed_seed_whole_normalized_core_is_preserved(self):
  seed='Did Anna snip pins? Anna did.';r,s=generate_characters(characters=100,seed=30,seed_text=seed)
  self.assertIsNotNone(r);self.assertIn(normalize(seed),normalize(r['text']));self.assertTrue(is_palindrome(r['text']))
 def test_geese_and_eva_end_to_end_seeds_are_retained(self):
  for seed in ['Do geese see God?','Eva, can I snip pins in a cave?']:
   r,s=generate_characters(characters=100,seed=30,seed_text=seed)
   self.assertIsNotNone(r);self.assertIn(normalize(seed),normalize(r['text']));self.assertTrue(is_palindrome(r['text']))
 def test_1200_has_actual_exact_result_and_honest_quality_metadata(self):
  compiled_characters(34).remaining_chars('START','END')
  r,s=generate_characters(characters=1200,seed=1)
  self.assertIsNotNone(r);self.assertTrue(1190<=len(r['text'])<=1200);self.assertTrue(is_palindrome(r['text']));self.assertTrue(r['quality_unrated']);self.assertIn('not evidence',r['quality_limit'])
if __name__=='__main__':unittest.main()
