from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: esperado 1 ocorrência, encontrei {n}')
    s=s.replace(old,new,1)

# Backup: versão correta e inclui outbox ainda não sincronizado.
once("  const chaves=['fdo_lotes','fdo_laminacoes','fdo_lote_seq','fdo_operadores','fdo_farinha_lotes_atuais','fdo_sess','fdo_bat_run'];\n  const dados={app:'Folhados d\\'Ouro — Produção',versao:'25.0',exportadoEm:new Date().toISOString(),origem:'localStorage',dados:{}};",
     "  const chaves=['fdo_lotes','fdo_laminacoes','fdo_lote_seq','fdo_operadores','fdo_farinha_lotes_atuais','fdo_sess','fdo_bat_run','fdo_sync_outbox_v25'];\n  const dados={app:'Folhados d\\'Ouro — Produção',versao:'25.1',exportadoEm:new Date().toISOString(),origem:'localStorage',dados:{}};",
     'backup v25.1')

# Outbox: só confirma a remoção se ninguém tiver gravado uma versão mais nova enquanto a transação estava em voo.
once("  drop(k,id){const o=this.out();if(o[k])delete o[k][id];this.saveOut(o)},",
     "  ack(k,id,sent){const o=this.out(),cur=o[k]&&o[k][id];if(cur&&JSON.stringify(cur)===JSON.stringify(sent))delete o[k][id];this.saveOut(o)},",
     'ack outbox')

old_flush="""  async flush(){
    if(this.flushing||!FB.db||!navigator.onLine)return;const o=this.out(),jobs=[];this.COL.forEach(k=>Object.entries(o[k]||{}).forEach(([id,x])=>jobs.push([k,id,x])));if(!jobs.length){FB.status('ok','✓ Sincronizado');return}
    this.flushing=true;FB.status('pending','Salvo aqui · sincronizando…');let ok=true;
    for(const [k,id,x] of jobs){try{const r=await FB.db.ref(this.path(k)+'/'+id).transaction(cur=>this.merge(k,cur,x),undefined,false);this.itemJson[k][id]=JSON.stringify(r.snapshot.val());this.drop(k,id)}catch(e){ok=false;console.warn('[FB25] item',k,id,e)}}
    this.flushing=false;FB.status(ok&&!this.pending()?'ok':'err',ok&&!this.pending()?'✓ Sincronizado':'⚠ Salvo aqui · nuvem pendente');
  },"""
new_flush="""  async flush(){
    if(this.flushing||!FB.db||!navigator.onLine)return;const o=this.out(),jobs=[];this.COL.forEach(k=>Object.entries(o[k]||{}).forEach(([id,x])=>jobs.push([k,id,x])));if(!jobs.length){FB.status('ok','✓ Sincronizado');return}
    this.flushing=true;FB.status('pending','Salvo aqui · sincronizando…');let ok=true;
    for(const [k,id,x] of jobs){try{const r=await FB.db.ref(this.path(k)+'/'+id).transaction(cur=>this.merge(k,cur,x),undefined,false);this.itemJson[k][id]=JSON.stringify(r.snapshot.val());this.ack(k,id,x)}catch(e){ok=false;console.warn('[FB25] item',k,id,e)}}
    this.flushing=false;
    if(this.pending()&&navigator.onLine){FB.status('pending','Salvo aqui · sincronizando…');setTimeout(()=>this.flush(),0);return}
    FB.status(ok?'ok':'err',ok?'✓ Sincronizado':'⚠ Salvo aqui · nuvem pendente');
  },"""
once(old_flush,new_flush,'flush sem perda')

old_legacy="""  legacy(k,v){if(!Array.isArray(v))return;const json=JSON.stringify(v);if(this.mirrorJson[k]===json)return;v.forEach(x=>{if(!x||!x.id)return;const id=this.key(x.id),r=this.raw[k]&&this.raw[k][id];if(r&&r._deleted)return;this.queue(k,this.merge(k,r,x))});if(this.ready[k])FB.status('pending','Aparelho antigo detectado · conciliando…');this.flush()},"""
new_legacy="""  legacy(k,v){if(!Array.isArray(v))return;const json=JSON.stringify(v);if(this.mirrorJson[k]===json)return;let reassert=false;v.forEach(x=>{if(!x||!x.id)return;const id=this.key(x.id),r=this.raw[k]&&this.raw[k][id];if(r&&r._deleted){reassert=true;return}this.queue(k,this.merge(k,r,x))});if(this.ready[k])FB.status('pending','Aparelho antigo detectado · conciliando…');if(reassert)this.mirror(k);this.flush()},"""
once(old_legacy,new_legacy,'legacy tombstone')

old_mirror="""  mirror(k){if(!FB.db||!navigator.onLine)return;clearTimeout(this.mirrorTimer[k]);this.mirrorTimer[k]=setTimeout(async()=>{const canon=this.map(LS.g(k,[])),raw=this.raw[k]||{};try{const r=await FB.db.ref(k).transaction(cur=>{const atual=this.map(Array.isArray(cur)?cur:[]),u={...canon};Object.entries(atual).forEach(([id,x])=>{if(raw[id]&&raw[id]._deleted)return;u[id]=this.merge(k,u[id],x)});return this.arr(k,u)},undefined,false);this.mirrorJson[k]=JSON.stringify(r.snapshot.val()||[])}catch(e){console.warn('[FB25] bridge',k,e)}},450)},"""
new_mirror="""  mirror(k){if(!FB.db||!navigator.onLine)return;clearTimeout(this.mirrorTimer[k]);this.mirrorTimer[k]=setTimeout(async()=>{const canon=this.map(LS.g(k,[])),raw=this.raw[k]||{};try{const r=await FB.db.ref(k).transaction(cur=>{const atual=this.map(Array.isArray(cur)?cur:[]),u={...canon};Object.entries(atual).forEach(([id,x])=>{if(raw[id]&&raw[id]._deleted)return;u[id]=this.merge(k,u[id],x)});let arr=this.arr(k,u);if(k==='fdo_lotes'&&typeof loteAtivo==='function')arr=arr.filter(l=>loteAtivo(l));return arr},undefined,false);this.mirrorJson[k]=JSON.stringify(r.snapshot.val()||[])}catch(e){console.warn('[FB25] bridge',k,e)}},450)},"""
once(old_mirror,new_mirror,'legacy sem cancelados')

# Criação atômica de laminação online: confere as partes no próprio nó de laminações antes de inserir.
needle="""  async proxLamSeq(ts){const d=new Date(ts),key=d.getFullYear()+String(d.getMonth()+1).padStart(2,'0')+String(d.getDate()).padStart(2,'0'),local=LS.g('fdo_laminacoes',[]).filter(x=>dataCurta(x.dataTs)===dataCurta(ts)).length;if(!FB.db||!navigator.onLine)return local+1;try{const r=await FB.db.ref('fdo_v25/meta/lam_seq/'+key).transaction(cur=>Math.max(Number(cur)||0,local)+1,undefined,false);return Number(r.snapshot.val())||local+1}catch(e){return local+1}},
"""
insert=needle+"""  async criarLaminacaoAtomica(lam,capacidades){
    if(!FB.db||!navigator.onLine)return {ok:true,offline:true};
    const id=this.key(lam.id);let conflito='';
    try{
      const r=await FB.db.ref(this.path('fdo_laminacoes')).transaction(cur=>{
        conflito='';const m=(cur&&typeof cur==='object')?this.clone(cur):{},usados={};
        Object.values(m).forEach(x=>{if(!x||x._deleted||!Array.isArray(x.composicao))return;x.composicao.forEach(c=>{if(!c||!c.loteId)return;usados[c.loteId]=(usados[c.loteId]||0)+(Number(c.partes)||0)})});
        for(const c of (lam.composicao||[])){const cap=Number(capacidades[c.loteId])||0,ja=Number(usados[c.loteId])||0,q=Number(c.partes)||0;if(q<=0||ja+q>cap){conflito='Balde #'+(c.loteNum||'')+' já teve partes usadas em outro aparelho.';return}}
        m[id]=this.merge('fdo_laminacoes',m[id],lam);return m;
      },undefined,false);
      if(!r.committed)return {ok:false,motivo:conflito||'As partes selecionadas mudaram em outro aparelho.'};
      const salvo=r.snapshot.child(id).val();if(salvo)this.itemJson.fdo_laminacoes[id]=JSON.stringify(salvo);return {ok:true,offline:false};
    }catch(e){console.warn('[FB25] lam atomic',e);return {ok:false,motivo:'Não foi possível confirmar as partes na nuvem.'}}
  },
"""
once(needle,insert,'laminação atômica')

# Reset global com evento explícito para os outros aparelhos baixarem o contador local.
old_reset="""  async resetSeq(){if(!FB.db||!navigator.onLine){alert('Conecte à internet para reiniciar a numeração com segurança em todos os aparelhos.');return false}try{await FB.db.ref('fdo_v25/meta/lote_seq').transaction(()=>0,undefined,false);await FB.db.ref('fdo_lote_seq').set(0);this.local('fdo_lote_seq',0);return true}catch(e){alert('Não foi possível reiniciar a numeração na nuvem.');return false}},"""
new_reset="""  async resetSeq(){if(!FB.db||!navigator.onLine){alert('Conecte à internet para reiniciar a numeração com segurança em todos os aparelhos.');return false}try{const token=Date.now();await FB.db.ref('fdo_v25/meta/lote_seq').transaction(()=>0,undefined,false);await FB.db.ref('fdo_v25/meta/lote_seq_reset').set(token);await FB.db.ref('fdo_lote_seq').set(0);this.local('fdo_seq_reset_ts_v25',token);this.local('fdo_lote_seq',0);return true}catch(e){alert('Não foi possível reiniciar a numeração na nuvem.');return false}},"""
once(old_reset,new_reset,'reset global')

old_init="""      FB.db.ref('fdo_lote_seq').on('value',snap=>this.absorverSeq(snap.val()));FB.db.ref('fdo_v25/meta/lote_seq').on('value',snap=>{const n=Number(snap.val())||0;if(n>(Number(LS.g('fdo_lote_seq',0))||0))this.local('fdo_lote_seq',n)});FB.db.ref('fdo_v25/meta/schema').transaction(cur=>Math.max(Number(cur)||0,1),undefined,false).catch(()=>{});this.flush();"""
new_init="""      FB.db.ref('fdo_lote_seq').on('value',snap=>this.absorverSeq(snap.val()));FB.db.ref('fdo_v25/meta/lote_seq').on('value',snap=>{const n=Number(snap.val())||0;if(n>(Number(LS.g('fdo_lote_seq',0))||0))this.local('fdo_lote_seq',n)});FB.db.ref('fdo_v25/meta/lote_seq_reset').on('value',snap=>{const t=Number(snap.val())||0,seen=Number(LS.g('fdo_seq_reset_ts_v25',0))||0;if(t>seen){this.local('fdo_seq_reset_ts_v25',t);this.local('fdo_lote_seq',0)}});FB.db.ref('fdo_v25/meta/schema').transaction(cur=>Math.max(Number(cur)||0,1),undefined,false).catch(()=>{});this.flush();"""
once(old_init,new_init,'listener reset')

once("FB.proxLamSeqDia=ts=>SYNC25.proxLamSeq(ts);\nFB.reiniciarSeq=()=>SYNC25.resetSeq();",
     "FB.proxLamSeqDia=ts=>SYNC25.proxLamSeq(ts);\nFB.criarLaminacaoAtomica=(lam,capacidades)=>SYNC25.criarLaminacaoAtomica(lam,capacidades);\nFB.reiniciarSeq=()=>SYNC25.resetSeq();",
     'expor lam atomica')

# Antes de gravar a laminação, reserva atomicamente as partes quando online.
old_lam="""  const lam={
    id:FB.novoId('lam'), nome, seqDia, data:agora.toLocaleString('pt-BR'), dataTs:agora.getTime(),
    receita, receitaNome, composicao, totalPartes:total, temMassaAnterior:temAnterior, op:getOp(),
    etapas:{laminacao:{feito:true, em:agora.toLocaleString('pt-BR'), emTs:agora.getTime(), op:getOp()}}
  };
  const lams=LS.g('fdo_laminacoes',[]); lams.unshift(lam); LS.s('fdo_laminacoes',lams);
  LS.s('fdo_lotes',todos);"""
new_lam="""  const lam={
    id:FB.novoId('lam'), nome, seqDia, data:agora.toLocaleString('pt-BR'), dataTs:agora.getTime(),
    receita, receitaNome, composicao, totalPartes:total, temMassaAnterior:temAnterior, op:getOp(),
    etapas:{laminacao:{feito:true, em:agora.toLocaleString('pt-BR'), emTs:agora.getTime(), op:getOp()}}
  };
  const capacidades={};composicao.forEach(c=>{const l=todos.find(x=>x.id===c.loteId),b=l&&l.etapas&&l.etapas.batimento;capacidades[c.loteId]=Number(b&&b.partes)||0});
  const reserva=await FB.criarLaminacaoAtomica(lam,capacidades);
  if(!reserva.ok){st.lamSel={};renderLaminacao();alert(reserva.motivo||'As partes mudaram em outro aparelho. Revise a seleção.');falar('As partes mudaram em outro aparelho. Revise a seleção.');return;}
  const lams=LS.g('fdo_laminacoes',[]).filter(x=>x.id!==lam.id); lams.unshift(lam); LS.s('fdo_laminacoes',lams);
  LS.s('fdo_lotes',todos);"""
once(old_lam,new_lam,'reserva de partes')

p.write_text(s,encoding='utf-8')

# Corrige o validador: fail deve existir antes de ser usado e adiciona invariantes da revisão final.
vp=Path('tools/validate_fdo.py')
v=vp.read_text(encoding='utf-8')
old="""errors=[]

# v25.1 — sincronização granular/transacional
for marker in (\"fdo_v25/lotes\",\"fdo_v25/laminacoes\",\"fdo_sync_outbox_v25\",\"async function proxLoteNum()\",\"await proxLoteNum()\",\"async function proxLamSeqDia(ts)\",\"function lotePartesUsadas(l)\",\"Aparelho antigo detectado · conciliando\"):
    if marker not in html: fail('v25.1 sem marcador: '+marker)
if \"function proxLoteNum(){ const n=LS.g('fdo_lote_seq',0)+1\" in html: fail('Numeração antiga ainda presente')

def fail(msg): errors.append(msg)
"""
new="""errors=[]

def fail(msg): errors.append(msg)

# v25.1 — sincronização granular/transacional
for marker in (\"fdo_v25/lotes\",\"fdo_v25/laminacoes\",\"fdo_sync_outbox_v25\",\"async function proxLoteNum()\",\"await proxLoteNum()\",\"async function proxLamSeqDia(ts)\",\"function lotePartesUsadas(l)\",\"Aparelho antigo detectado · conciliando\",\"criarLaminacaoAtomica\",\"fdo_v25/meta/lote_seq_reset\",\"ack(k,id,sent)\"):
    if marker not in html: fail('v25.1 sem marcador: '+marker)
if \"function proxLoteNum(){ const n=LS.g('fdo_lote_seq',0)+1\" in html: fail('Numeração antiga ainda presente')
if \"versao:'25.0'\" in html: fail('Backup ainda declara versão 25.0')
"""
if old not in v:
    raise SystemExit('validator: bloco esperado não encontrado')
vp.write_text(v.replace(old,new,1),encoding='utf-8')

# Service Worker: não esconder falha do precache. Se o cache essencial falhar, a instalação falha e o SW anterior continua ativo.
sw=Path('sw.js')
w=sw.read_text(encoding='utf-8')
old_sw="caches.open(CACHE).then(c=>c.addAll(ASSETS)).catch(()=>{})"
if old_sw not in w:
    raise SystemExit('sw: precache esperado não encontrado')
w=w.replace(old_sw,"caches.open(CACHE).then(c=>c.addAll(ASSETS))",1)
sw.write_text(w,encoding='utf-8')

print('Revisão final v25.1 aplicada')
