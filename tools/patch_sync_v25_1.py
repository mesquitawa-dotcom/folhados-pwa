from pathlib import Path
p=Path('index.html'); s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: esperado 1, achei {n}')
    s=s.replace(old,new,1)

def between(a,b,new,label):
    global s
    i=s.find(a); j=s.find(b,i+1)
    if i<0 or j<0: raise SystemExit(f'{label}: marcador ausente')
    s=s[:i]+new+s[j:]

once("FOLHADOS D'OURO — atualização v25.0","FOLHADOS D'OURO — atualização v25.1",'versao')
once("       NOVIDADES v25.0:\n","       NOVIDADES v25.1:\n       • Sincronização granular: baldes e laminações passam a registros independentes no Firebase.\n       • Ponte temporária concilia aparelhos antigos sem apagar dados da estrutura nova.\n       • Numeração de baldes e sequência diária da laminação usam transações quando online.\n       • Alterações offline entram numa fila local e são reenviadas ao reconectar.\n       NOVIDADES v25.0:\n",'cabecalho')
once("  loginOpId:null,loginFiltro:''};","  loginOpId:null,loginFiltro:'',criandoLote:false,criandoLam:false};",'st')

sync_block=r'''
// ════════════════════════════════════════════════════════════
// SINCRONIZAÇÃO GRANULAR v25.1
// Mantém arrays no localStorage/UI, mas usa um nó por registro na nuvem.
// Chaves antigas continuam como ponte temporária para aparelhos v24/v25.0.
// ════════════════════════════════════════════════════════════
const SYNC25={
  COL:['fdo_lotes','fdo_laminacoes'], SCALAR:['fdo_operadores','fdo_farinha_lotes_atuais'],
  OUT:'fdo_sync_outbox_v25', itemJson:{fdo_lotes:{},fdo_laminacoes:{}}, raw:{fdo_lotes:{},fdo_laminacoes:{}}, ready:{fdo_lotes:false,fdo_laminacoes:false},
  flushing:false, mirrorTimer:{}, mirrorJson:{},
  path(k){return k==='fdo_lotes'?'fdo_v25/lotes':'fdo_v25/laminacoes'},
  key(id){return String(id||'sem_id').replace(/[.#$\[\]\/]/g,'_')},
  clone(v){return v==null?v:JSON.parse(JSON.stringify(v))},
  local(k,v){try{localStorage.setItem(k,JSON.stringify(v))}catch(e){}},
  novoId(prefix){let u='';try{if(crypto&&crypto.randomUUID)u=crypto.randomUUID()}catch(e){}if(!u)u=Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,10);return prefix+'_'+u},
  map(arr){const o={};(Array.isArray(arr)?arr:[]).forEach(x=>{if(x&&x.id)o[this.key(x.id)]=this.clone(x)});return o},
  arr(k,m){return Object.values(m||{}).filter(x=>x&&x.id&&!x._deleted).map(x=>this.clone(x)).sort((a,b)=>{const ta=Number(k==='fdo_lotes'?a.criadoTs:a.dataTs)||0,tb=Number(k==='fdo_lotes'?b.criadoTs:b.dataTs)||0;return tb-ta})},
  ts(x){if(!x)return 0;let m=Math.max(Number(x.criadoTs)||0,Number(x.dataTs)||0,Number(x.deletedTs)||0,Number(x.cancelado&&x.cancelado.emTs)||0,Number(x.restaurado&&x.restaurado.emTs)||0);Object.values(x.etapas||{}).forEach(v=>m=Math.max(m,Number(v&&v.emTs)||0));return m},
  etapa(a,b){if(!a)return this.clone(b);if(!b)return this.clone(a);return (Number(b.emTs)||0)>=(Number(a.emTs)||0)?{...this.clone(a),...this.clone(b)}:{...this.clone(b),...this.clone(a)}},
  merge(k,a,b){
    if(!a)return this.clone(b); if(!b)return this.clone(a);
    if(k==='fdo_laminacoes'){
      if(a._deleted||b._deleted){const da=Number(a.deletedTs)||0,db=Number(b.deletedTs)||0;if(a._deleted&&da>=this.ts(b))return this.clone(a);if(b._deleted&&db>=this.ts(a))return this.clone(b)}
      return this.ts(b)>=this.ts(a)?{...this.clone(a),...this.clone(b)}:{...this.clone(b),...this.clone(a)};
    }
    const base=this.ts(b)>=this.ts(a)?{...this.clone(a),...this.clone(b)}:{...this.clone(b),...this.clone(a)};
    const ea=a.etapas||{}, eb=b.etapas||{}, e={};new Set([...Object.keys(ea),...Object.keys(eb)]).forEach(x=>e[x]=this.etapa(ea[x],eb[x]));if(Object.keys(e).length)base.etapas=e;
    const ca=a.cancelado,cb=b.cancelado;if(ca||cb)base.cancelado=(Number(cb&&cb.emTs)||0)>=(Number(ca&&ca.emTs)||0)?this.clone(cb||ca):this.clone(ca);
    const ra=a.restaurado,rb=b.restaurado;if(ra||rb)base.restaurado=(Number(rb&&rb.emTs)||0)>=(Number(ra&&ra.emTs)||0)?this.clone(rb||ra):this.clone(ra);
    return base;
  },
  out(){return LS.g(this.OUT,{fdo_lotes:{},fdo_laminacoes:{}})||{fdo_lotes:{},fdo_laminacoes:{}}},
  saveOut(o){this.local(this.OUT,o)},
  queue(k,item){if(!item||!item.id)return;const o=this.out();o[k]=o[k]||{};const id=this.key(item.id);o[k][id]=this.merge(k,o[k][id],item);this.saveOut(o)},
  drop(k,id){const o=this.out();if(o[k])delete o[k][id];this.saveOut(o)},
  pending(){const o=this.out();return this.COL.some(k=>Object.keys(o[k]||{}).length)},
  push(k,v){
    if(FB.applying)return;
    if(this.COL.includes(k)){const m=this.map(v);Object.entries(m).forEach(([id,x])=>{if(this.itemJson[k][id]!==JSON.stringify(x))this.queue(k,x)});if(this.pending())FB.status(navigator.onLine?'pending':'local',navigator.onLine?'Salvo aqui · sincronizando…':'Salvo neste aparelho · sem internet');this.flush();return}
    if(k==='fdo_lote_seq')return this.absorverSeq(v);
    if(!this.SCALAR.includes(k)||!FB.db)return;
    FB.db.ref(k).set(v).catch(e=>{console.warn('[FB25] scalar',k,e);FB.status('err','⚠ Salvo aqui · nuvem pendente')});
  },
  async flush(){
    if(this.flushing||!FB.db||!navigator.onLine)return;const o=this.out(),jobs=[];this.COL.forEach(k=>Object.entries(o[k]||{}).forEach(([id,x])=>jobs.push([k,id,x])));if(!jobs.length){FB.status('ok','✓ Sincronizado');return}
    this.flushing=true;FB.status('pending','Salvo aqui · sincronizando…');let ok=true;
    for(const [k,id,x] of jobs){try{const r=await FB.db.ref(this.path(k)+'/'+id).transaction(cur=>this.merge(k,cur,x),undefined,false);this.itemJson[k][id]=JSON.stringify(r.snapshot.val());this.drop(k,id)}catch(e){ok=false;console.warn('[FB25] item',k,id,e)}}
    this.flushing=false;FB.status(ok&&!this.pending()?'ok':'err',ok&&!this.pending()?'✓ Sincronizado':'⚠ Salvo aqui · nuvem pendente');
  },
  apply(k,v){
    const m=(v&&typeof v==='object')?this.clone(v):{};this.raw[k]=this.clone(m);const local=this.map(LS.g(k,[]));if(!this.ready[k])Object.entries(local).forEach(([id,x])=>{m[id]=this.merge(k,m[id],x);if(!v||!v[id])this.queue(k,x)});const o=this.out();Object.entries(o[k]||{}).forEach(([id,x])=>m[id]=this.merge(k,m[id],x));
    FB.applying=true;this.local(k,this.arr(k,m));FB.applying=false;this.itemJson[k]={};Object.entries(m).forEach(([id,x])=>this.itemJson[k][id]=JSON.stringify(x));this.ready[k]=true;FB.repaint();this.mirror(k);this.flush();
  },
  legacy(k,v){if(!Array.isArray(v))return;const json=JSON.stringify(v);if(this.mirrorJson[k]===json)return;v.forEach(x=>{if(!x||!x.id)return;const id=this.key(x.id),r=this.raw[k]&&this.raw[k][id];if(r&&r._deleted)return;this.queue(k,this.merge(k,r,x))});if(this.ready[k])FB.status('pending','Aparelho antigo detectado · conciliando…');this.flush()},
  mirror(k){if(!FB.db||!navigator.onLine)return;clearTimeout(this.mirrorTimer[k]);this.mirrorTimer[k]=setTimeout(async()=>{const canon=this.map(LS.g(k,[])),raw=this.raw[k]||{};try{const r=await FB.db.ref(k).transaction(cur=>{const atual=this.map(Array.isArray(cur)?cur:[]),u={...canon};Object.entries(atual).forEach(([id,x])=>{if(raw[id]&&raw[id]._deleted)return;u[id]=this.merge(k,u[id],x)});return this.arr(k,u)},undefined,false);this.mirrorJson[k]=JSON.stringify(r.snapshot.val()||[])}catch(e){console.warn('[FB25] bridge',k,e)}},450)},
  async remove(k,id0){const id=this.key(id0),t={id:id0,_deleted:true,deletedTs:Date.now(),op:typeof getOp==='function'?getOp():''};this.queue(k,t);this.raw[k][id]=t;await this.flush()},
  async proxLoteNum(){const local=Number(LS.g('fdo_lote_seq',0))||0;if(!FB.db||!navigator.onLine){const n=local+1;this.local('fdo_lote_seq',n);FB.status('err','⚠ Número criado offline · sincronizar depois');return {num:n,origem:'offline'}}try{const r=await FB.db.ref('fdo_v25/meta/lote_seq').transaction(cur=>Math.max(Number(cur)||0,local)+1,undefined,false),n=Number(r.snapshot.val())||local+1;this.local('fdo_lote_seq',n);FB.db.ref('fdo_lote_seq').transaction(cur=>Math.max(Number(cur)||0,n),undefined,false).catch(()=>{});return {num:n,origem:'transacao'}}catch(e){const n=local+1;this.local('fdo_lote_seq',n);FB.status('err','⚠ Numeração local · nuvem pendente');return {num:n,origem:'offline'}}},
  async proxLamSeq(ts){const d=new Date(ts),key=d.getFullYear()+String(d.getMonth()+1).padStart(2,'0')+String(d.getDate()).padStart(2,'0'),local=LS.g('fdo_laminacoes',[]).filter(x=>dataCurta(x.dataTs)===dataCurta(ts)).length;if(!FB.db||!navigator.onLine)return local+1;try{const r=await FB.db.ref('fdo_v25/meta/lam_seq/'+key).transaction(cur=>Math.max(Number(cur)||0,local)+1,undefined,false);return Number(r.snapshot.val())||local+1}catch(e){return local+1}},
  async resetSeq(){if(!FB.db||!navigator.onLine){alert('Conecte à internet para reiniciar a numeração com segurança em todos os aparelhos.');return false}try{await FB.db.ref('fdo_v25/meta/lote_seq').transaction(()=>0,undefined,false);await FB.db.ref('fdo_lote_seq').set(0);this.local('fdo_lote_seq',0);return true}catch(e){alert('Não foi possível reiniciar a numeração na nuvem.');return false}},
  absorverSeq(v){const n=Number(v)||0,local=Number(LS.g('fdo_lote_seq',0))||0;if(n>local)this.local('fdo_lote_seq',n);if(FB.db&&n>0)FB.db.ref('fdo_v25/meta/lote_seq').transaction(cur=>Math.max(Number(cur)||0,n),undefined,false).catch(()=>{})},
  init(){
    if(typeof firebase==='undefined'||!firebase.initializeApp){FB.status('local','Salvo neste aparelho · sem nuvem');return}try{if(!firebase.apps.length)firebase.initializeApp(FB_CFG);FB.db=firebase.database();FB.status(navigator.onLine?'pending':'local',navigator.onLine?'Sincronizando…':'Salvo neste aparelho · sem internet');
      this.COL.forEach(k=>{FB.db.ref(this.path(k)).on('value',snap=>this.apply(k,snap.val()),e=>{console.warn('[FB25] granular',k,e);FB.status('err','⚠ Nuvem v25 indisponível')});FB.db.ref(k).on('value',snap=>this.legacy(k,snap.val()),e=>console.warn('[FB25] legacy',k,e))});
      this.SCALAR.forEach(k=>FB.db.ref(k).on('value',snap=>{const v=snap.val();if(v==null){const l=localStorage.getItem(k);if(l!==null)try{FB.db.ref(k).set(JSON.parse(l))}catch(e){};return}FB.applying=true;this.local(k,v);FB.applying=false;FB.repaint()},e=>console.warn('[FB25] scalar listen',k,e)));
      FB.db.ref('fdo_lote_seq').on('value',snap=>this.absorverSeq(snap.val()));FB.db.ref('fdo_v25/meta/lote_seq').on('value',snap=>{const n=Number(snap.val())||0;if(n>(Number(LS.g('fdo_lote_seq',0))||0))this.local('fdo_lote_seq',n)});FB.db.ref('fdo_v25/meta/schema').transaction(cur=>Math.max(Number(cur)||0,1),undefined,false).catch(()=>{});this.flush();
    }catch(e){console.warn('[FB25] init',e);FB.status('err','⚠ Firebase indisponível')}
  },
  online(){if(!FB.db)return;FB.status('pending','Internet voltou · sincronizando…');this.flush();this.COL.forEach(k=>this.mirror(k))}
};
FB.init=()=>SYNC25.init();
FB.push=(k,v)=>SYNC25.push(k,v);
FB.novoId=p=>SYNC25.novoId(p);
FB.proxLoteNum=()=>SYNC25.proxLoteNum();
FB.proxLamSeqDia=ts=>SYNC25.proxLamSeq(ts);
FB.reiniciarSeq=()=>SYNC25.resetSeq();
FB.removerRegistro=(k,id)=>SYNC25.remove(k,id);
FB.aoVoltarOnline=()=>SYNC25.online();

'''
marker="// Decide e navega para a tela inicial correta respeitando operadores/login."
if marker not in s: raise SystemExit('insert sync: marcador ausente')
s=s.replace(marker,sync_block+marker,1)

once("function proxLoteNum(){ const n=LS.g('fdo_lote_seq',0)+1; LS.s('fdo_lote_seq',n); return n; }","async function proxLoteNum(){ return FB.proxLoteNum(); }",'prox lote')
new_criar=r'''async function criarLoteSecos(){
  const r=RECEITAS[st.receita]||RECEITAS.r1;
  const agora=new Date();
  const seq=await proxLoteNum();
  const lote={
    num:seq.num, numOrigem:seq.origem, id:FB.novoId('lote'),
    receita:st.receita, receitaNome:r.nome, rotulo:r.rotulo,
    criado:agora.toLocaleString('pt-BR'), criadoTs:agora.getTime(),
    etapas:{ porcionamento_secos:{
      feito:true, em:agora.toLocaleString('pt-BR'), emTs:agora.getTime(),
      op:getOp(), temp:st.temp, fermento_g:st.fermento, fermento_horas:st.fermentoHoras, baldes_secos:st.baldeSecos||1,
      farinhas_lotes:st.farinhasLotes?JSON.parse(JSON.stringify(st.farinhasLotes)):null,
      total_g:totalReceitaFull(st.receita), peso_secos_g:pesoBaldeSecosAtual(), concluidos:st.done.size, total:RECEITA.length,
      dur:Math.round((Date.now()-st.sessionStart)/60000)
    }}
  };
  const todos=LS.g('fdo_lotes',[]);todos.unshift(lote);LS.s('fdo_lotes',todos);return lote;
}

'''
between("function criarLoteSecos(){","function loteAtivo",new_criar,'criar lote')
new_cancel=r'''function loteAtivo(l){if(!l)return false;const c=Number(l.cancelado&&l.cancelado.emTs)||0,r=Number(l.restaurado&&l.restaurado.emTs)||0;return !c||r>c;}
function apagarLote(id){
  if(!OP.pode('apagar')){alert('Você não tem permissão para cancelar baldes.\nPeça ao administrador.');return;}
  const todos=LS.g('fdo_lotes',[]),lote=todos.find(l=>l.id===id);if(!lote||!loteAtivo(lote))return;
  if(!confirm(`Cancelar o Balde #${lote.num}?\n\nEle sai das etapas de produção, mas permanece no histórico e pode ser restaurado.`))return;
  lote.cancelado={em:new Date().toLocaleString('pt-BR'),emTs:Date.now(),op:getOp()};LS.s('fdo_lotes',todos);renderHist();
}
function restaurarLote(id){
  if(!OP.pode('apagar'))return;const todos=LS.g('fdo_lotes',[]),lote=todos.find(l=>l.id===id);if(!lote||loteAtivo(lote))return;
  if(!confirm(`Restaurar o Balde #${lote.num} para a produção?`))return;
  lote.restaurado={em:new Date().toLocaleString('pt-BR'),emTs:Date.now(),op:getOp()};LS.s('fdo_lotes',todos);renderHist();
}

'''
between("function loteAtivo(l){","// Migra sessões antigas",new_cancel,'cancelamento')
new_reset=r'''async function reiniciarNumeracaoLotes(){
  if(!confirm('Reiniciar a numeração dos baldes?\n\nO próximo balde criado será o #1.\nOs baldes que já estão na lista continuam guardados (com os números atuais).'))return;
  if(await FB.reiniciarSeq())alert('Numeração reiniciada. O próximo balde será o #1 em todos os aparelhos atualizados.');
}

'''
between("function reiniciarNumeracaoLotes(){","// Escolhe qual receita rodar",new_reset,'reset')
new_final=r'''async function finalizarSecos(){
  if(st.criandoLote)return;st.criandoLote=true;
  try{
    salvarSessao(true);const lote=await criarLoteSecos();st.ultimoLoteId=lote.id;
    pararVoz();liberarWakeLock();st.sessionStart=0;st.modo='normal';mostrarPerguntaSecos(false);
    const tot=formatPeso(totalReceitaFull(st.receita));document.getElementById('done-emoji').textContent='✅';document.getElementById('done-title').textContent='Secos Concluídos!';document.getElementById('done-lote').textContent='BALDE #'+lote.num;document.getElementById('done-mark').style.display='';document.getElementById('done-mark').textContent='✍️ Marque este número na massa';document.getElementById('done-etq-btn').style.display='';document.getElementById('done-etq-massas-btn').style.display='';document.getElementById('done-voltar-porc-btn').style.display='';document.getElementById('done-tot').innerHTML=`<div class="done-conf">Total da massa (secos + líquidos)</div><div class="done-val">${tot}</div>`;falar(`Porcionamento de secos concluído. Balde número ${lote.num}.`);setTimeout(()=>ir('done'),1500);
  }finally{st.criandoLote=false;}
}

'''
between("function finalizarSecos(){","// PORCIONAMENTO DE LÍQUIDOS concluído",new_final,'final secos')
old="""function lotePartesDisp(l){\n  const b=(l&&l.etapas&&l.etapas.batimento)||null;\n  if(!b||!b.feito) return 0;\n  return Math.max(0,(Number(b.partes)||0)-(Number(b.partesUsadas)||0));\n}\nfunction lotesComPartes(){ return LS.g('fdo_lotes',[]).filter(l=>loteAtivo(l)&&lotePartesDisp(l)>0); }"""
new="""function lotePartesUsadas(l){if(!l||!l.id)return 0;return LS.g('fdo_laminacoes',[]).reduce((s,x)=>s+(x&&Array.isArray(x.composicao)?x.composicao.reduce((a,c)=>a+(c.loteId===l.id?(Number(c.partes)||0):0),0):0),0);}\nfunction lotePartesDisp(l){const b=(l&&l.etapas&&l.etapas.batimento)||null;if(!b||!b.feito)return 0;return Math.max(0,(Number(b.partes)||0)-lotePartesUsadas(l));}\nfunction lotesComPartes(){ return LS.g('fdo_lotes',[]).filter(l=>loteAtivo(l)&&lotePartesDisp(l)>0); }"""
once(old,new,'partes')
once("function proxLamSeqDia(ts){\n  const dia=dataCurta(ts);\n  return LS.g('fdo_laminacoes',[]).filter(x=>dataCurta(x.dataTs)===dia).length + 1;\n}","async function proxLamSeqDia(ts){return FB.proxLamSeqDia(ts);}",'seq lam')
once("function criarLaminacao(){","async function criarLaminacao(){\n  if(st.criandoLam)return;st.criandoLam=true;\n  try{",'lam async')
once("    l.etapas=l.etapas||{}; l.etapas.batimento=l.etapas.batimento||{};\n    l.etapas.batimento.partesUsadas=(Number(l.etapas.batimento.partesUsadas)||0)+q;\n    if(!l.etapas.laminacao || !l.etapas.laminacao.feito){ l.etapas.laminacao={feito:true, em:new Date().toLocaleString('pt-BR'), emTs:Date.now()}; }","    l.etapas=l.etapas||{};if(!l.etapas.laminacao || !l.etapas.laminacao.feito){l.etapas.laminacao={feito:true,em:new Date().toLocaleString('pt-BR'),emTs:Date.now(),op:getOp()};}",'lam contador')
once("  const seqDia=proxLamSeqDia(agora.getTime());","  const seqDia=await proxLamSeqDia(agora.getTime());",'lam await')
once("    id:'lam_'+agora.getTime(), nome, seqDia, data:agora.toLocaleString('pt-BR'), dataTs:agora.getTime(),","    id:FB.novoId('lam'), nome, seqDia, data:agora.toLocaleString('pt-BR'), dataTs:agora.getTime(),",'lam id')
once("  falar(`Lote ${nome} criado. ${total} ${total===1?'parte':'partes'}. ${compFala}.`+(temAnterior?' Atenção: inclui massa de dia anterior.':''));\n}\nfunction apagarLaminacao(id){","  falar(`Lote ${nome} criado. ${total} ${total===1?'parte':'partes'}. ${compFala}.`+(temAnterior?' Atenção: inclui massa de dia anterior.':''));\n  }finally{st.criandoLam=false;}\n}\nfunction apagarLaminacao(id){",'lam finally')
once("  const todos=LS.g('fdo_lotes',[]);\n  (lam.composicao||[]).forEach(c=>{\n    const l=todos.find(x=>x.id===c.loteId); if(!l||!l.etapas||!l.etapas.batimento) return;\n    l.etapas.batimento.partesUsadas=Math.max(0,(Number(l.etapas.batimento.partesUsadas)||0)-(Number(c.partes)||0));\n  });\n  LS.s('fdo_lotes',todos);\n  LS.s('fdo_laminacoes',lams.filter(x=>x.id!==id));","  FB.removerRegistro('fdo_laminacoes',id);\n  LS.s('fdo_laminacoes',lams.filter(x=>x.id!==id));",'lam delete')
once("window.addEventListener('online',()=>{ if(FB.db)FB.status('pending','Internet voltou · sincronizando…'); });","window.addEventListener('online',()=>FB.aoVoltarOnline());",'online')
p.write_text(s,encoding='utf-8')

sw=Path('sw.js');w=sw.read_text(encoding='utf-8');
if "const CACHE='fdo-v25-0';" not in w:raise SystemExit('cache base não encontrado')
sw.write_text(w.replace("const CACHE='fdo-v25-0';","const CACHE='fdo-v25-1';",1),encoding='utf-8')

vp=Path('tools/validate_fdo.py');v=vp.read_text(encoding='utf-8');needle="errors=[]\n"
extra="""errors=[]\n\n# v25.1 — sincronização granular/transacional\nfor marker in (\"fdo_v25/lotes\",\"fdo_v25/laminacoes\",\"fdo_sync_outbox_v25\",\"async function proxLoteNum()\",\"await proxLoteNum()\",\"async function proxLamSeqDia(ts)\",\"function lotePartesUsadas(l)\",\"Aparelho antigo detectado · conciliando\"):\n    if marker not in html: fail('v25.1 sem marcador: '+marker)\nif \"function proxLoteNum(){ const n=LS.g('fdo_lote_seq',0)+1\" in html: fail('Numeração antiga ainda presente')\n"""
if needle not in v:raise SystemExit('validator sem ponto')
vp.write_text(v.replace(needle,extra,1),encoding='utf-8')
print('Patch v25.1 aplicado')
