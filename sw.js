// Folhados d'Ouro — Service Worker
// OBS 18/06/2026: cache fdo-v12 —
//   • Porcionamento dividido em DOIS: Secos (gera o lote + etiqueta) e
//     Líquidos (continua um lote já com os secos prontos; sem etiqueta).
//   • Bater a Massa só libera lotes com Secos E Líquidos prontos.
//   • Receita 3 PADRÃO: Bagatelle 3600 g + Italiana 4400 g (sem Feuilletage).
//   • Senha própria das Configurações (padrão 456), pedida toda vez.
//   • Bater a Massa: microfone JÁ LIGADO no campo de peso (fala ou digita).
//   • Cronômetro do batimento resiste a sair do app (retoma ao voltar);
//     só sai por comando claro (confirmação). Wake Lock durante a batida.
//   • Impressão MDK-022: seletor de linguagem (ESC/POS · TSPL · CPCL),
//     teste rápido e diagnóstico de serviços/características Bluetooth.
//   --- mantido das versões anteriores ---
//   • Lotes numerados/apagáveis, PIN do Porcionamento, autofalante, calculadora,
//     previsão de madrugada (Open-Meteo), Gemini no contexto da receita.
// IMPORTANTE: a cada publicação, troque a versão (fdo-vN) para o celular atualizar.
const CACHE = 'fdo-v12';

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
