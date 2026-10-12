# Jitter-only canonical frontend preview

Source is the inspected canonical frontend (mini revision6231fc3), with the writing-transform transition fix and independent response exactness check. Input, Generate, length, output, Read/Poster and Copy stay unchanged. No typed expansion or backend integration is active.

The existing Cloudflare Pages palindrome project hosts only a preview branch named palindrome-webkit-fix. Its unchanged same-origin API function proxies the existing service. Canonical production deployment and backend stay untouched. The GitHub dev preview embeds this patched preview to preserve API access without CORS changes.

Build: npm ci && npm run build. Deploy only a preview branch, never main: wrangler pages deploy dist --project-name palindrome --branch palindrome-webkit-fix --commit-hash EXACT_SOURCE_SHA.

Desktop WebKit with iPhone emulation reproduced camera tracking lag at1200 letters. Original140ms transitions are retargeted every writing tick; writing transforms now apply directly, retaining the final900ms eased fit. Same live E2E fails before and passes after. This is not physical-iPhone or genuine-pinch verification.

## Frontend-only production promotion

`npm run build:production` temporarily uses the original production HTML and footer credit, preserves all three existing public files (favicon, icon sprite, Panama), writes production-dist, then restores preview source. Deploy that artifact to the existing palindrome Pages main branch only after approval/CI. The API proxy remains the original unchanged implementation. No backend model/corpus files are packaged or deployed.
