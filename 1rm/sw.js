// Offline shell for /1rm/. Bump CACHE to ship a new version: the old cache is
// dropped on activate, so a stale page can never outlive its own assets.
var CACHE = "1rm-v3";
var CORE = [
  "/1rm/",
  "/1rm/index.html",
  "/1rm/manifest.webmanifest",
  "/1rm/icon-192.png",
  "/1rm/icon-512.png",
  "/1rm/icon-maskable-512.png",
  "/1rm/icon-180.png"
];

self.addEventListener("install", function (e) {
  e.waitUntil(
    caches.open(CACHE)
      .then(function (c) { return c.addAll(CORE); })
      .then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (e) {
  e.waitUntil(
    caches.keys()
      .then(function (keys) {
        return Promise.all(keys.map(function (k) {
          return k === CACHE ? null : caches.delete(k);
        }));
      })
      .then(function () { return self.clients.claim(); })
  );
});

// Stale-while-revalidate: the gym has no signal, so the cached copy always
// answers first; the network copy lands in the cache for the next launch.
self.addEventListener("fetch", function (e) {
  var req = e.request;
  if (req.method !== "GET") return;

  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (!url.pathname.startsWith("/1rm/")) return;

  e.respondWith(
    caches.open(CACHE).then(function (cache) {
      return cache.match(req, { ignoreSearch: true }).then(function (hit) {
        var net = fetch(req).then(function (res) {
          if (res && res.ok && res.type === "basic") cache.put(req, res.clone());
          return res;
        }).catch(function () {
          // Offline and uncached: a navigation still has the shell to fall back on.
          return hit || cache.match("/1rm/index.html");
        });
        return hit || net;
      });
    })
  );
});
