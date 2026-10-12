# Experimental real search, 028

This additive package mounts `/api/dev/v3/health` and `/api/dev/v3/composition`. The old `/api/v3` composer, bank, model, proxy and production frontend remain in place. No model inference is used by the new route.

Each request runs bounded outside-in search over a typed lexical question grammar with five action verbs. Fixed grammatical actor/location spans may surround an editable internal gap when `seed_text` is supplied. Directional letter debt can cross words; the final normalized text is checked independently. Words and argument slots are inputs; completed answers are not cached or sampled. Grammar bindings establish only limited role consistency, not a readability certificate.

Defaults: 22 requested letters, 150 ms search timeout, 3,000 visited states, 24 steps, 32 output tapes, eight letters of debt. `seed` orders actual returned candidates. Literal `centre` and editable `seed_text` are distinct and cannot be combined. Unlicensed seeds and unsupported lengths return HTTP 409 with the real search receipt. `fallback=true` explicitly requests the unchanged legacy composer after failure; its response says `explicit-legacy-corpus-fallback` and `newly_searched:false`. The frontend never requests that fallback.

The finite question fixture has eight exact texts with maximum length 29. This is a narrow experimental English grammar. The supplied geese seed reconstructs its existing 31-letter control with a shifted center; it is labeled as a supplied-example reconstruction. Question-seed recomposition can change the predicate and object, so it preserves roles and outer spans rather than every original word. These behaviors do not establish a general long coherent paragraph generator or worldwide novelty.

Mount only after backing up the inspected old app:

```python
from server.dev_real_search import create_router
from server.v3 import composition as legacy_composition
app.include_router(create_router(legacy_composition))
```

Copy this directory's `dev_real_search.py` and `experimental_search/` into the existing `server/` package; never overwrite `server/v3.py`, the bank or the original grammar modules. Source hashes and a backup of `server/app.py` identify deployment independently of the old checkout revision. Controlled reload uses the existing LaunchAgent. Rollback restores that exact app backup and reloads the same LaunchAgent; additive files may remain inert. The dedicated deployment script refuses a changed baseline.

Tests: `PYTHONPATH=palindrome-v3 python3 -m unittest backend.test_real_search`. Build development UI with `npm run build:search --prefix palindrome-v3/canonical`; normal and production builds retain the existing production endpoints and defaults. Do not deploy a search build to the production Pages branch.
