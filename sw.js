// Folhados d'Ouro — Service Worker
// OBS 27/05/2026: cache fdo-v7 —
//   • Divisão por voz ("dividir X por 8", "X dividido por 8" etc.).
//   • Wake Lock: tela não apaga durante o porcionamento.
//   • Auto-retomada do mic ao voltar de outro app (limitação do navegador:
//     em segundo plano o reconhecimento de voz fica pausado).
//   • Pós-secos: pergunta "continua receita ou outro balde de secos?"
//     ao terminar o balde 1, preservando a temperatura/fermento.
//   Gemini e Open-Meteo nunca são cacheados.
// IMPORTANTE: a cada publicação, troque a versão (fdo-vN) para o celular atualizar.
const CACHE = 'fdo-v7';

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll([
        './',
        './index.html',
        './manifest.json',
        './icon-192.png',
        './icon-512.png'
      ]))
      .then(() => self.skipWaiting())
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
  // APIs externas (Gemini e previsão do tempo) — nunca cachear
  if (e.request.url.includes('generativelanguage.googleapis.com')) return;
  if (e.request.url.includes('api.open-meteo.com')) return;
  if (e.request.method !== 'GET') return;

  e.respondWith(
    caches.match(e.request)
      .then(r => r || fetch(e.request).then(res => {
        if (res.ok) {
          const clone = res.clone();
          caches.open(CACHE).then(c => c.put(e.request, clone));
        }
        return res;
      }))
      .catch(() => caches.match('./index.html'))
  );
});
