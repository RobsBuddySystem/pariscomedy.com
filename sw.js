// Paris Comedy — Service Worker
// Caches core assets for offline browsing & faster repeat visits

const CACHE = 'pariscomedy-v2';
const CORE = [
  '/',
  '/shows.html',
  '/calendar.html',
  '/venues.html',
  '/book.html',
  '/history.html',
  '/about.html',
  '/css/style.css',
  '/js/app.js',
  '/js/data.js',
  '/img/og-image.png',
  '/img/icon-192.png',
  '/manifest.webmanifest'
];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  // Only handle GET requests for same-origin or cached assets
  if (e.request.method !== 'GET') return;
  const url = new URL(e.request.url);
  // Network-first for HTML pages (fresh content), cache-first for assets
  const isPage = url.pathname.endsWith('.html') || url.pathname === '/';
  if (isPage) {
    e.respondWith(
      fetch(e.request)
        .then(res => {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
          return res;
        })
        .catch(() => caches.match(e.request).then(r => r || caches.match('/')))
    );
  } else {
    e.respondWith(
      caches.match(e.request).then(r => r || fetch(e.request).then(res => {
        if (res.ok) {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return res;
      }))
    );
  }
});
