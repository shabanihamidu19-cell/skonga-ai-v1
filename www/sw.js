/* ══════════════════════════════════════════════════════════════
   SKONGA AI — App Shell Service Worker
   ------------------------------------------------------------
   What this does and doesn't do:
   - Caches the app SHELL only (index.html + pay.html + the two pinned CDN
     scripts it loads: jszip, plotly). This is what lets the app
     actually OPEN when the device is offline or the connection is
     too flaky to even load the page — right now the offline banner
     inside the app implies this works, but without a service worker
     it didn't: a genuinely offline first-load / reload would just
     fail to load anything.
   - Does NOT cache /api/* calls. Chat replies, image generation,
     search, and notifications must always hit the network — caching
     those would mean showing stale or wrong AI answers, which is
     worse than showing the "you're offline" state the app already
     has.
   - Cache-first for the shell: instant load, and correctness is
     fine because CACHE_VERSION below is bumped by hand whenever
     index.html changes (see "Updating" below), which forces a
     fresh fetch + swap on next visit.
   - NOTE on the packaged Android APK (Capacitor): index.html is
     already bundled inside the app itself, so it loads from local
     storage even without this service worker — this file mainly
     matters if SKONGA is ever also served as a regular website/PWA
     in a browser. It's harmless either way, just lower-impact
     inside the APK build specifically.
══════════════════════════════════════════════════════════════ */

const CACHE_VERSION = 'skonga-shell-v2'; // bump this string whenever index.html or pay.html changes
const SHELL_URLS = [
  './index.html',
  './pay.html',
  'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js',
  'https://cdn.plot.ly/plotly-basic-2.27.0.min.js'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => cache.addAll(SHELL_URLS))
  );
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Never intercept API calls — always go to the network.
  if (url.pathname.startsWith('/api/') || url.hostname.includes('skonga-backend')) {
    return;
  }
  // Only handle GET requests for the shell / pinned CDN scripts.
  if (event.request.method !== 'GET') return;

  const isShellRequest =
    SHELL_URLS.some((shellUrl) => event.request.url.endsWith(shellUrl.replace('./', ''))) ||
    url.pathname === '/' || url.pathname.endsWith('/index.html') || url.pathname.endsWith('/pay.html');

  if (!isShellRequest) return;

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((response) => {
        const clone = response.clone();
        caches.open(CACHE_VERSION).then((cache) => cache.put(event.request, clone));
        return response;
      }).catch(() => cached); // if genuinely offline and nothing cached, this fails naturally
    })
  );
});
