// Xfinder service worker: پوسته‌ی برنامه کش می‌شود؛ داده‌ها (configs/output) همیشه از شبکه، با fallback به کش.
const V = "xfinder-v25";
const SHELL = ["./", "index.html", "assets/css/style.css", "assets/js/app.js", "assets/img/icon-192.png", "assets/img/logo.png", "favicon.ico"];
self.addEventListener("install", e => { e.waitUntil(caches.open(V).then(c => c.addAll(SHELL).catch(() => {})).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => { e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== V).map(x => caches.delete(x)))).then(() => self.clients.claim())); });
self.addEventListener("fetch", e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== "GET" || u.origin !== location.origin) return;
  const live = /\/(data|output)\//.test(u.pathname);
  e.respondWith(fetch(r).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(V).then(c => c.put(r, copy)); }
    return res;
  }).catch(() => caches.match(r).then(m => m || (live ? new Response("[]", {status: 503}) : caches.match("index.html")))));
});
