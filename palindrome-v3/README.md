# Palindrome development preview

The minimal interface keeps the prompt, Generate, length slider, output, Read, Poster and Copy. Its experimental build calls `/api/dev/v3` through the existing same-origin proxy. It runs a finite typed lexical search on every request; errors do not silently display corpus output. The default target is a short sentence. Longer cohesive paragraphs remain a research objective, not an achieved capability.

Canonical production continues to use `/api/v3`, with its existing length controls and composer. `build:production` retains that behavior; `build:search` selects the development route. The accepted WebKit jitter fix remains in both builds. No paid model, new tunnel or changed credentials are required.

See [backend/README.md](backend/README.md) for bounds, provenance, seed semantics, installation and rollback. Previous finite phrase-search sources and tests remain as evidence; they are not the primary page's generator.
