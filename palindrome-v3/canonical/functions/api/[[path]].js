// The "worker" half of the site: Pages serves the static page, and every /api
// call is proxied to the Mac Mini through its cloudflared tunnel. Same-origin
// for the browser, so no CORS, and the backend hostname stays an implementation
// detail. The upstream response is returned as-is so the SSE body keeps
// streaming rather than being buffered.
const ORIGIN = "https://palindrome-api.ericspencer.us"

export async function onRequest(context) {
  const url = new URL(context.request.url)
  const upstream = new URL(url.pathname + url.search, ORIGIN)

  const res = await fetch(upstream, {
    method: context.request.method,
    headers: context.request.headers,
    body: ["GET", "HEAD"].includes(context.request.method) ? undefined : context.request.body,
  })

  const headers = new Headers(res.headers)
  headers.set("Cache-Control", "no-cache")
  headers.delete("content-encoding")   // never re-encode a stream we pass through
  headers.delete("content-length")
  return new Response(res.body, { status: res.status, headers })
}
