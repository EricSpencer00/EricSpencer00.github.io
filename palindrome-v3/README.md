# Palindrome preview

The primary route embeds the existing `https://palindrome.ericspencer.us/` interface full screen. Its live prompt, Generate, length slider, output, read/copy interactions and API run unchanged. Direct calls from the static dev origin are blocked by CORS; embedding preserves the canonical same-origin service path. No proxy, backend change, paid inference or credential change.

The live site still runs the older generator despite current research source retiring output. This correction uses the user-requested existing deployed service; it does not change retirement source or redeploy the backend. Long output is not certified as readable prose.

Previous finite search sources/tests remain as evidence but are not loaded by the page. Canonical exactness validation remains; desktop/mobile browser checks independently validate returned text and real API behavior. The wrapper has loading and timeout/error fallback. Cross-origin HTTP errors inside the frame are handled by the canonical page, whose DOM the wrapper cannot inspect.

Run `node --test tests/palindrome-v3*.test.mjs` and existing Python suite.
