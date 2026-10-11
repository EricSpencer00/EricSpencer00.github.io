# Palindrome v3 phrase expansion

This is the v3 product route on the existing static dev site. It replaces
offline bank selection with bounded request-time phrase search in a browser
Worker. No new backend, credentials, inference models or paid API are needed.
It does not unretire the legacy server's output routes or alter the paper.

The v1 service used single-word center-out search, a 14-second default budget,
SSE status/partial/result messages, and optional GPT-2 ranking. The new route
retains asynchronous progress, cancellation and inspectable center-out
construction while using grammatical phrase units and argument bindings.
`SearchClient.request(options)` implements the browser request boundary;
`worker.mjs` emits status/progress/result/error/cancelled messages by request
ID. This static deployment is not a new HTTP API endpoint. Legacy v3 remains
an independent service and was HTTP 403 during baseline inspection.

## Method and limitations

The engine ports the proven `bilateral_seams.py` whole-chunk center algorithm
and experiment 027's residual debt/payoff method. Phrase rules form finite
typed graphs. Closure requires both complete grammatical endpoints and
empty letter debt; the full rendered sentence then receives an independent
two-pointer exactness check. The client repeats exactness before display.

The active search compiles 21 source spans from 11 explicitly human-liked
examples using the existing research typed phrase compiler. Four per-seed
editable windows preserve the selected seed's actual prefix and suffix.
The suss window carries one retained left-context letter, `s`, in its grammar;
the editable window itself need not be a palindrome. No finished sentence is
injected into search. Corpus membership is used only to label/filter controls.
Tap permits only an insertion before its retained Pat; mock changes only its
subject. These do not borrow the suss or ward search graphs.

The split grammar at debt four returns four exact suss closures (two imported
controls and two corpus-unseen, human-ungraded recombinations), and one
imported control each for tap, ward and mock. At debt eight ward also returns
the known longer drawing control. There are two new texts overall, no new
paragraph. Institution ownership of roti is a declared semantic adapter and
needs human judgment. The conditional link to memos remains weak.

Regrouping the suss VP recovers the same outputs at debt one that split
chunks recover at debt four. Operational cap exhaustion is not a proof of
linguistic impossibility. Ordering is user-adjustable shorter/longer/soft
repetition; no lexical preference or invented human quality score is used.
Imported controls are hidden by default and available explicitly.

Every request searches again; no completed-output bank is sampled. A set of
already shown normalized IDs makes repeated requests advance, then report
exhaustion. Changing seed clears that history. Filters can genuinely produce
no result; no catalogue or seed fallback is silently displayed as generation.
Local reader feedback stays in browser storage and does not modify global
human labels or train a model.

Bounds are 32 lexical phrase arcs per graph, 3,000 visited states, 12 phrase
steps, 32 unique closures, and 150 ms search time. The search yields every
24 states so cancellation can run; cancelling also terminates the Worker.
Latest request IDs reject delayed stale callbacks and settings changes
cancel in-flight work. Module load and browser scheduling occur outside the
search time budget, so response latency is measured separately in the UI.

## Verification

Run `node --test tests/palindrome-v3*.test.mjs` and
`python3 scripts/compile_palindrome_windows.py --check` or the existing Python unittest
suite. Dedicated GitHub checks target the dev branch; the existing deployment
workflow remains unchanged. All product files are tracked before deployment,
so the existing generated dev mirror includes the new route.

Desktop 1440px and mobile 390px headless browser checks cover keyboard start,
exact results, partial-word completion, repeated generation, exhaustion,
reset, cancellation, settings invalidation, impossible constraints, delayed
stale real-worker callbacks, copy, local feedback and horizontal overflow.
Timing receipts distinguish engine search time, client response time and
automation wall time. Viewport tests on one host are not device benchmarks;
no broad speedup is claimed against a blocked legacy service.

Only dev is targeted. Existing unrelated routes and the portfolio main branch
are preserved. The route carries noindex and retains that exclusion.
