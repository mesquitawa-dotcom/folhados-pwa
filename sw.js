// Folhados d'Ouro — Service Worker
// OBS 15/06/2026: cache fdo-v8 —
//   • Controle de LOTES (numerados, apagáveis com cascata) no menu "Lotes".
//   • Senha de acesso por PIN (padrão 123789) ao entrar nos módulos.
//   • Botão liga/desliga do autofalante (TTS) + comando de voz.
//   • Módulo Bater a Massa (início): seleção de lote porcionado + confirmação
//     da temperatura ambiente puxada de outro batimento do dia.
//   • Receita 2 → "Receita 2 - MASSA 3 KG"; Receita 3 → "Receita 3 - PADRÃO".
//   --- mantido da v7 ---
//   • Divisão por voz, Wake Lock, pós-secos com contador de baldes.
//   • Gemini e Open-Meteo nunca são cacheados.
// IMPORTANTE: a cada publicação, troque a versão (fdo-vN) para o celular atualizar.
const CACHE = 'fdo-v8';

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
