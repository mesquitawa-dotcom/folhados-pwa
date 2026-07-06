// Folhados d'Ouro — Service Worker
// Versão do cache: incrementada a TODA entrega.
const CACHE='fdo-v24-9';
const ASSETS=[
  './',
  './index.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
];

self.addEventListener('install',e=>{
  e.waitUntil(
    caches.open(CACHE).then(c=>c.addAll(ASSETS)).catch(()=>{})
  );
  self.skipWaiting();
});

self.addEventListener('activate',e=>{
  e.waitUntil(
    caches.keys().then(keys=>Promise.all(
      keys.filter(k=>k!==CACHE).map(k=>caches.delete(k))
    )).then(()=>self.clients.claim())
  );
});

self.addEventListener('fetch',e=>{
  const req=e.request;
  if(req.method!=='GET') return;
  const isHtml=req.mode==='navigate' || (req.headers.get('accept')||'').includes('text/html');
  if(isHtml){
    e.respondWith(
      fetch(req).then(r=>{
        const copy=r.clone();
        caches.open(CACHE).then(c=>c.put(req,copy)).catch(()=>{});
        return r;
      }).catch(()=>caches.match(req).then(r=>r||caches.match('./index.html')))
    );
    return;
  }
  e.respondWith(
    caches.match(req).then(r=>r || fetch(req).then(resp=>{
      const copy=resp.clone();
      caches.open(CACHE).then(c=>c.put(req,copy)).catch(()=>{});
      return resp;
    }).catch(()=>r))
  );
});
