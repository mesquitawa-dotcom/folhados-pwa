// ════════════════════════════════════════════════════════════════════
// Folhados d'Ouro — Service Worker (fdo-v23)
// • Cache-first dos assets essenciais (HTML + manifest + ícones).
// • Bumpe o nome do cache (fdo-vN) a cada deploy para forçar update.
// • Em fetch, tenta o cache primeiro; se faltar, busca da rede e cacheia.
// • No activate, limpa caches antigos (qualquer fdo-v* que não seja o atual).
// ════════════════════════════════════════════════════════════════════
const CACHE = 'fdo-v23';
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png'
];

self.addEventListener('install', (event) => {
  // Pula a espera: a nova versão entra em ação no primeiro reload.
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE).then((cache) => cache.addAll(ASSETS).catch(() => {}))
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((nomes) =>
      Promise.all(
        nomes
          .filter((n) => n.startsWith('fdo-v') && n !== CACHE)
          .map((n) => caches.delete(n))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  // Não cacheia métodos não-GET nem requisições para o Firebase / Gemini /
  // Open-Meteo (esses precisam ir sempre para a rede)
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (
    url.hostname.endsWith('firebaseio.com') ||
    url.hostname.endsWith('googleapis.com') ||
    url.hostname.endsWith('gstatic.com') ||
    url.hostname.endsWith('open-meteo.com')
  ) {
    return; // deixa o fetch nativo cuidar
  }
  event.respondWith(
    caches.match(req).then((hit) => {
      if (hit) return hit;
      return fetch(req).then((res) => {
        // Cacheia respostas OK do mesmo domínio (para offline futuro)
        if (res && res.status === 200 && url.origin === self.location.origin) {
          const clone = res.clone();
          caches.open(CACHE).then((c) => c.put(req, clone).catch(() => {}));
        }
        return res;
      }).catch(() => hit); // sem rede, devolve o que tiver
    })
  );
});
