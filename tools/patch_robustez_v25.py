from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: esperado 1 ocorrência, encontrei {n}')
    s=s.replace(old,new,1)

# Versão e histórico
once("FOLHADOS D'OURO — atualização v24.10\n       NOVIDADES v24.10:","FOLHADOS D'OURO — atualização v25.0\n       NOVIDADES v25.0:\n       • Robustez de dados: histórico não é mais descartado após 200 registros.\n       • Exclusão de balde virou cancelamento reversível, preservando rastreabilidade.\n       • Backup administrativo em JSON e indicador simples de sincronização.\n       • Correção do tempo do porcionamento de líquidos e proteção contra\n         comandos de voz negativos como 'não está pronto'.\n       NOVIDADES v24.10:", 'cabecalho versão')

# CSS do status de sync/cancelamento
once("    @keyframes geo-spin{to{transform:rotate(360deg)}}\n  </style>","    @keyframes geo-spin{to{transform:rotate(360deg)}}\n    .sync-pill{margin:.35rem 1rem 0;padding:.3rem .65rem;border:1px solid var(--brd);border-radius:.35rem;\n      font-size:.58rem;color:var(--mut);text-align:center;letter-spacing:.05rem;flex-shrink:0}\n    .sync-pill.ok{color:var(--grn);border-color:rgba(74,222,128,.3)}\n    .sync-pill.pending{color:var(--gold);border-color:rgba(201,151,58,.35)}\n    .sync-pill.err{color:var(--red);border-color:rgba(248,113,113,.35)}\n    .lote-card.cancelado{opacity:.62;border-color:#5a1a0e}\n    .lote-cancelado{font-size:.68rem;color:var(--red);font-weight:bold;margin-top:.35rem}\n  </style>", 'css robustez')

# Backup na Config
once("  <label class=\"cfg-mini\" style=\"margin-top:.1rem\">Raio permitido (metros)<input id=\"inp-geo-raio\" class=\"inp\" type=\"number\" min=\"10\" placeholder=\"150\"></label>\n  <button class=\"btn-main\" onclick=\"salvarConfig()\">Salvar e Continuar</button>","  <label class=\"cfg-mini\" style=\"margin-top:.1rem\">Raio permitido (metros)<input id=\"inp-geo-raio\" class=\"inp\" type=\"number\" min=\"10\" placeholder=\"150\"></label>\n  <div class=\"cfg-sep\"></div>\n  <div class=\"cfg-t\" style=\"font-size:1rem\">💾 Backup</div>\n  <div class=\"cfg-s\" style=\"font-size:.72rem;line-height:1.45\">Exporta uma cópia dos dados de produção deste aparelho para recuperação e auditoria.</div>\n  <button class=\"link-btn\" style=\"width:100%;text-align:center;margin-bottom:.4rem\" onclick=\"exportarBackup()\">Exportar backup dos dados</button>\n  <button class=\"btn-main\" onclick=\"salvarConfig()\">Salvar e Continuar</button>", 'botao backup')

# Indicador na tela inicial
once("  <div class=\"op-bar\" id=\"op-bar\" style=\"display:none\">\n    <div class=\"op-bar-av\" id=\"op-bar-av\">?</div>\n    <div class=\"op-bar-nome\" id=\"op-bar-nome\">—</div>\n    <button class=\"op-bar-trocar\" onclick=\"trocarOperador()\">Trocar</button>\n  </div>","  <div class=\"op-bar\" id=\"op-bar\" style=\"display:none\">\n    <div class=\"op-bar-av\" id=\"op-bar-av\">?</div>\n    <div class=\"op-bar-nome\" id=\"op-bar-nome\">—</div>\n    <button class=\"op-bar-trocar\" onclick=\"trocarOperador()\">Trocar</button>\n  </div>\n  <div class=\"sync-pill\" id=\"sync-pill\">Salvo neste aparelho</div>", 'indicador sync')

# Estado de sync no Firebase
once("const FB={\n  db:null, applying:false, lastJson:{},","const FB={\n  db:null, applying:false, lastJson:{}, syncEstado:'local',\n  status(estado,txt){\n    this.syncEstado=estado;\n    const el=document.getElementById('sync-pill'); if(!el)return;\n    el.className='sync-pill'+(estado==='ok'?' ok':estado==='pending'?' pending':estado==='err'?' err':'');\n    el.textContent=txt||(estado==='ok'?'✓ Sincronizado':estado==='pending'?'Sincronizando…':estado==='err'?'⚠ Sincronização pendente':'Salvo neste aparelho');\n  },", 'FB status')

once("    if(typeof firebase==='undefined'||!firebase.initializeApp) return;","    if(typeof firebase==='undefined'||!firebase.initializeApp){ this.status('local','Salvo neste aparelho · sem nuvem'); return; }", 'FB sem SDK')
once("      this.db=firebase.database();","      this.db=firebase.database();\n      this.status(navigator.onLine?'pending':'local',navigator.onLine?'Sincronizando…':'Salvo neste aparelho · sem internet');", 'FB conectado')
once("        },err=>{ console.warn('[FB] listen',k,err); });","          this.status('ok','✓ Sincronizado');\n        },err=>{ console.warn('[FB] listen',k,err); this.status('err','⚠ Salvo aqui · nuvem pendente'); });", 'listener status')
once("    if(!this.db) return; // offline ou SDK não carregou: fica só local\n    try{\n      const json=JSON.stringify(v);\n      this.lastJson[k]=json;\n      this.db.ref(k).set(v).catch(e=>console.warn('[FB] set',k,e));","    if(!this.db){ this.status('local','Salvo neste aparelho'); return; } // offline ou SDK não carregou: fica só local\n    try{\n      const json=JSON.stringify(v);\n      this.lastJson[k]=json;\n      this.status('pending','Salvo aqui · sincronizando…');\n      this.db.ref(k).set(v).then(()=>this.status('ok','✓ Sincronizado')).catch(e=>{console.warn('[FB] set',k,e);this.status('err','⚠ Salvo aqui · nuvem pendente');});", 'push status')

# Backup: inserir antes de salvarConfig
once("function salvarConfig(){","function exportarBackup(){\n  const chaves=['fdo_lotes','fdo_laminacoes','fdo_lote_seq','fdo_operadores','fdo_farinha_lotes_atuais','fdo_sess','fdo_bat_run'];\n  const dados={app:'Folhados d\\'Ouro — Produção',versao:'25.0',exportadoEm:new Date().toISOString(),origem:'localStorage',dados:{}};\n  chaves.forEach(k=>{ const raw=localStorage.getItem(k); if(raw!==null){ try{dados.dados[k]=JSON.parse(raw);}catch{dados.dados[k]=raw;} } });\n  const blob=new Blob([JSON.stringify(dados,null,2)],{type:'application/json'});\n  const a=document.createElement('a'); a.href=URL.createObjectURL(blob);\n  a.download='fdo-backup-'+new Date().toISOString().slice(0,10)+'.json';\n  document.body.appendChild(a); a.click(); a.remove(); setTimeout(()=>URL.revokeObjectURL(a.href),1000);\n}\nfunction salvarConfig(){", 'func backup')

# Cancelamento reversível
once("function apagarLote(id){\n  if(!OP.pode('apagar')){\n    alert('Você não tem permissão para apagar baldes.\\nPeça ao administrador.');\n    return;\n  }\n  const todos=LS.g('fdo_lotes',[]);\n  const lote=todos.find(l=>l.id===id);\n  if(!lote) return;\n  const ok=confirm(`Apagar o Balde #${lote.num} e TODOS os seus processos (porcionamento, batimento e demais etapas)?\\n\\nEsta ação não pode ser desfeita.`);\n  if(!ok) return;\n  LS.s('fdo_lotes',todos.filter(l=>l.id!==id));\n  renderHist();\n}","function loteAtivo(l){ return !(l&&l.cancelado&&l.cancelado.emTs); }\nfunction apagarLote(id){\n  if(!OP.pode('apagar')){\n    alert('Você não tem permissão para cancelar baldes.\\nPeça ao administrador.');\n    return;\n  }\n  const todos=LS.g('fdo_lotes',[]);\n  const lote=todos.find(l=>l.id===id);\n  if(!lote||!loteAtivo(lote)) return;\n  const ok=confirm(`Cancelar o Balde #${lote.num}?\\n\\nEle sai das etapas de produção, mas permanece no histórico e pode ser restaurado.`);\n  if(!ok) return;\n  lote.cancelado={em:new Date().toLocaleString('pt-BR'),emTs:Date.now(),op:getOp()};\n  LS.s('fdo_lotes',todos);\n  renderHist();\n}\nfunction restaurarLote(id){\n  if(!OP.pode('apagar')) return;\n  const todos=LS.g('fdo_lotes',[]); const lote=todos.find(l=>l.id===id); if(!lote||loteAtivo(lote))return;\n  if(!confirm(`Restaurar o Balde #${lote.num} para a produção?`))return;\n  delete lote.cancelado; LS.s('fdo_lotes',todos); renderHist();\n}", 'cancelamento balde')

# Não descartar histórico após 200
s=s.replace("LS.s('fdo_lotes',todos.slice(0,200));","LS.s('fdo_lotes',todos);")
s=s.replace("LS.s('fdo_laminacoes',lams.slice(0,200));","LS.s('fdo_laminacoes',lams);")

# Excluir cancelados das filas operacionais
s=s.replace("return LS.g('fdo_lotes',[]).filter(l=>{\n    const e=l.etapas||{};\n    // Bater a Massa:","return LS.g('fdo_lotes',[]).filter(l=>{\n    if(!loteAtivo(l)) return false;\n    const e=l.etapas||{};\n    // Bater a Massa:")
s=s.replace("return LS.g('fdo_lotes',[]).filter(l=> secosFeito(l) && !liquidosFeito(l));","return LS.g('fdo_lotes',[]).filter(l=> loteAtivo(l) && secosFeito(l) && !liquidosFeito(l));")
s=s.replace("return LS.g('fdo_lotes',[]).filter(l=>{\n    const e=l.etapas||{};\n    return e.batimento && e.batimento.feito", "return LS.g('fdo_lotes',[]).filter(l=>{\n    if(!loteAtivo(l)) return false;\n    const e=l.etapas||{};\n    return e.batimento && e.batimento.feito")
s=s.replace("function lotesComPartes(){ return LS.g('fdo_lotes',[]).filter(l=>lotePartesDisp(l)>0); }","function lotesComPartes(){ return LS.g('fdo_lotes',[]).filter(l=>loteAtivo(l)&&lotePartesDisp(l)>0); }")
s=s.replace("  for(const l of LS.g('fdo_lotes',[])){\n    const b=l.etapas&&l.etapas.batimento;","  for(const l of LS.g('fdo_lotes',[])){\n    if(!loteAtivo(l)) continue;\n    const b=l.etapas&&l.etapas.batimento;")
s=s.replace("  for(const l of LS.g('fdo_lotes',[])){\n    const f=l.etapas&&l.etapas.fermentacao;","  for(const l of LS.g('fdo_lotes',[])){\n    if(!loteAtivo(l)) continue;\n    const f=l.etapas&&l.etapas.fermentacao;")
s=s.replace("    .filter(l=>l&&l.etapas&&l.etapas.batimento&&l.etapas.batimento.feito)","    .filter(l=>loteAtivo(l)&&l&&l.etapas&&l.etapas.batimento&&l.etapas.batimento.feito)")

# Histórico: card cancelado e restaurar
once("    const btnDel = podeApagar ? `<button class=\"lote-del\" onclick=\"apagarLote('${l.id}')\" title=\"Apagar balde\">🗑</button>` : '';\n    return `<div class=\"lote-card\">","    const cancelado=!loteAtivo(l);\n    const btnDel = podeApagar ? (cancelado\n      ? `<button class=\"lote-del\" onclick=\"restaurarLote('${l.id}')\" title=\"Restaurar balde\">↩</button>`\n      : `<button class=\"lote-del\" onclick=\"apagarLote('${l.id}')\" title=\"Cancelar balde\">🗑</button>`) : '';\n    return `<div class=\"lote-card ${cancelado?'cancelado':''}\">", 'hist cancelado classe')
once("      <div class=\"lote-meta\">${meta}</div>\n      <div class=\"lote-etapas\">${chips}</div>","      <div class=\"lote-meta\">${meta}</div>\n      ${cancelado?`<div class=\"lote-cancelado\">CANCELADO · ${l.cancelado.em||''} · ${_escHtml(l.cancelado.op||'')}</div>`:''}\n      <div class=\"lote-etapas\">${chips}</div>", 'hist cancelado detalhe')

# Corrige duração dos líquidos
once("function concluirLiquidos(){\n  const todos=LS.g('fdo_lotes',[]);\n  const lote=todos.find(l=>l.id===st.liqLote);\n  pararVoz();liberarWakeLock();st.sessionStart=0;st.modo='normal';","function concluirLiquidos(){\n  const todos=LS.g('fdo_lotes',[]);\n  const lote=todos.find(l=>l.id===st.liqLote);\n  const inicioSessao=st.sessionStart||Date.now();\n  pararVoz();liberarWakeLock();st.sessionStart=0;st.modo='normal';", 'inicio líquidos')
once("    dur:Math.round((Date.now()-(st.sessionStart||Date.now()))/60000)","    dur:Math.round((Date.now()-inicioSessao)/60000)", 'duração líquidos')

# Voz: negações não podem avançar
once("function processarComando(txt,alt){\n  const todas=[txt];","function comandoNegativo(t){\n  const x=(t||'').toLowerCase();\n  return ['não está pronto','nao esta pronto','ainda não','ainda nao','não terminei','nao terminei','não fiz','nao fiz','não coloquei','nao coloquei','não pesei','nao pesei','não acabou','nao acabou'].some(p=>x.includes(p));\n}\nfunction processarComando(txt,alt){\n  const todas=[txt];", 'função negação')
once("  // 3) Comandos normais\n  for(const t of todas){\n    const som=ehComandoSom(t);", "  // 3) Comandos normais\n  for(const t of todas){\n    if(comandoNegativo(t) && matchCmd(t,'avancar')){ mostrarAI('Entendi: ainda não concluído.'); falar('Certo. Aguardo você concluir.'); return; }\n    const som=ehComandoSom(t);", 'bloqueio negação')

# Eventos de conectividade e versão da tela
once("(function(){\n  // Sincronia multi-aparelho via Firebase Realtime Database","window.addEventListener('online',()=>{ if(FB.db)FB.status('pending','Internet voltou · sincronizando…'); });\nwindow.addEventListener('offline',()=>FB.status('local','Salvo neste aparelho · sem internet'));\n\n(function(){\n  // Sincronia multi-aparelho via Firebase Realtime Database", 'eventos rede')

p.write_text(s,encoding='utf-8')

sw=Path('sw.js')
w=sw.read_text(encoding='utf-8')
old="const CACHE='fdo-v24-10';"
if w.count(old)!=1: raise SystemExit('cache anterior não encontrado exatamente uma vez')
w=w.replace(old,"const CACHE='fdo-v25-0';",1)
sw.write_text(w,encoding='utf-8')

print('Patch v25 aplicado')
