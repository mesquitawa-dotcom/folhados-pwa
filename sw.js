// Folhados d'Ouro — Service Worker
// OBS 18/06/2026: cache fdo-v13 —
//   • Temperatura da Noite: só DUAS opções (ambas 17°C), por tempo de
//     fermentação — fermento 70 g (14 h) ou 64 g (17 h).
//   • Secos: "Voltar" no 1º passo sai para o menu inicial.
//   • Entre farinhas, a voz fala só o nome e o total (sem "Concluído").
//   • Finalização dos secos sem "+ Outro balde de secos".
//   • Voz ao finalizar só diz "concluído + número do lote".
//   • Bater a Massa: balde 1 mostra fermento, sal e manteiga.
//   --- base v12 ---
//   • Porcionamento dividido em Secos (gera lote + etiqueta) e Líquidos.
//   • Bater a Massa só libera lotes com Secos E Líquidos prontos.
//   • Receita 3 PADRÃO; senha própria das Configurações; microfone já
//     ligado no peso do batimento; cronômetro resiste ao segundo plano;
//     impressão MDK-022 (ESC/POS · TSPL · CPCL) com teste e diagnóstico.
//   --- mantido das versões anteriores ---
//   • Lotes numerados/apagáveis, PIN do Porcionamento, autofalante, calculadora,
//     previsão de madrugada (Open-Meteo), Gemini no contexto da receita.
// IMPORTANTE: a cada publicação, troque a versão (fdo-vN) para o celular atualizar.
const CACHE = 'fdo-v13';

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
