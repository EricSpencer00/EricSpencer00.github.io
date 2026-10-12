# Canonical and experimental search frontend

The accepted WebKit writing-transform fix remains: writing updates apply directly, while the final 900 ms fit is eased. Physical-iPhone and genuine-pinch coverage is limited to the user's reported jitter acceptance; desktop WebKit emulation is recorded separately.

`npm run build` and `npm run build:production` use the existing `/api/v3` composer, 40-letter minimum and 1,200-letter default. Production HTML, credit and public files retain their existing build path. This task does not redeploy that artifact.

`npm run build:search` selects the additive `/api/dev/v3` search route, a 16-letter slider minimum and 22-letter default. Optional input is a grammatical palindrome seed; supported seed spans can be recomposed internally while the literal center moves. Empty and unsupported requests display the API's honest error. The minimal controls, exactness validation, Read, Poster and Copy remain.

Deploy the search build only to the existing Cloudflare project `palindrome` preview branch `palindrome-webkit-fix`, using the exact source commit. The unchanged same-origin proxy reaches the new API route. Never send a search build to the production `main` branch.
