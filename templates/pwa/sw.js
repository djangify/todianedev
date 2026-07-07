{% load static %}// ToDiane — The Coach Who Codes — service worker (installable PWA + offline blog reading)
// Bump CACHE_VERSION whenever you want every installed app to refresh its caches.
const CACHE_VERSION = 'todiane-pwa-v1';
const BLOG_CACHE = 'todiane-blog-v1';
const OFFLINE_URL = '/offline/';

// How many blog pages to keep on the device before evicting the oldest.
const BLOG_LIMIT = 120;

// Core files cached on install so the app shell + offline page always work.
const CORE_URLS = [
  OFFLINE_URL,
  '{% static "css/output.css" %}',
  '{% static "images/android-chrome-192x192.png" %}',
  '{% static "images/android-chrome-512x512.png" %}'
];

// Latest posts injected by the server so they're readable offline even if
// the visitor never opened them. Best-effort (a failure never blocks install).
const PRECACHE_PAGES = {{ precache_pages|safe }};

self.addEventListener('install', (event) => {
  event.waitUntil(
    (async () => {
      const cache = await caches.open(CACHE_VERSION);
      // Core shell must succeed.
      await cache.addAll(CORE_URLS);
      // Latest blog posts are best-effort — cache each on its own.
      const blogCache = await caches.open(BLOG_CACHE);
      await Promise.all(
        PRECACHE_PAGES.map((url) =>
          fetch(url, { credentials: 'omit' })
            .then((res) => (res && res.ok ? blogCache.put(url, res) : null))
            .catch(() => null)
        )
      );
      await self.skipWaiting();
    })()
  );
});

self.addEventListener('activate', (event) => {
  const keep = [CACHE_VERSION, BLOG_CACHE];
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((key) => !keep.includes(key)).map((key) => caches.delete(key))
      ))
      .then(() => self.clients.claim())
  );
});

// Let the page tell a waiting worker to activate immediately (update prompt).
self.addEventListener('message', (event) => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});

// Keep the blog cache from growing without bound (oldest entries evicted first).
function trimCache(cacheName, maxEntries) {
  caches.open(cacheName).then((cache) => {
    cache.keys().then((keys) => {
      if (keys.length > maxEntries) {
        cache.delete(keys[0]).then(() => trimCache(cacheName, maxEntries));
      }
    });
  });
}

self.addEventListener('fetch', (event) => {
  const req = event.request;

  // Only handle GET requests.
  if (req.method !== 'GET') return;

  const url = new URL(req.url);

  // Ignore anything off-site (htmx CDN, analytics, external images) — let it hit the network.
  if (url.origin !== self.location.origin) return;

  // Never cache dynamic / logged-in / admin areas. Always go to the network.
  const BYPASS = ['/accounts', '/admin', '/sw.js'];
  if (BYPASS.some((path) => url.pathname.startsWith(path))) return;

  // Uploaded blog images: cache-first so cached posts show their pictures offline.
  if (url.pathname.startsWith('/media/blog/')) {
    event.respondWith(
      caches.match(req).then((cached) => {
        const fetched = fetch(req).then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(BLOG_CACHE).then((cache) => cache.put(req, copy));
          }
          return res;
        }).catch(() => cached);
        return cached || fetched;
      })
    );
    return;
  }

  // Static assets: cache-first for speed, refresh in the background.
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(req).then((cached) => {
        const fetched = fetch(req).then((res) => {
          if (res && res.ok) {
            const copy = res.clone();
            caches.open(CACHE_VERSION).then((cache) => cache.put(req, copy));
          }
          return res;
        }).catch(() => cached);
        return cached || fetched;
      })
    );
    return;
  }

  // Page navigations: network-first (always fresh when online).
  // Pages that opt in with the X-PWA-Cacheable header (blog posts) are stored
  // for offline reading. Pages without that header are never cached.
  if (req.mode === 'navigate') {
    event.respondWith(
      fetch(req)
        .then((res) => {
          const cacheable =
            res &&
            res.ok &&
            res.type === 'basic' &&
            res.headers.get('X-PWA-Cacheable') === '1';
          if (cacheable) {
            const copy = res.clone();
            caches.open(BLOG_CACHE).then((cache) => {
              cache.put(req, copy).then(() => trimCache(BLOG_CACHE, BLOG_LIMIT));
            });
          }
          return res;
        })
        .catch(() =>
          // Offline: serve the cached page if we have it, otherwise the offline page.
          caches.match(req).then((cached) => cached || caches.match(OFFLINE_URL))
        )
    );
    return;
  }
});
