from pathlib import Path
import re
import urllib.request

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'

text=INDEX.read_text(encoding='utf-8')


def one(old,new,label):
    global text
    n=text.count(old)
    if n!=1:
        raise SystemExit(f'{label}: esperado 1 ocorrência, encontrado {n}')
    text=text.replace(old,new,1)


def between(start,end,new,label):
    global text
    a=text.find(start)
    if a<0: raise SystemExit(f'{label}: início não encontrado')
    b=text.find(end,a+len(start))
    if b<0: raise SystemExit(f'{label}: fim não encontrado')
    text=text[:a]+new+text[b:]

# Cabeçalho/versionamento
one(
"       FOLHADOS D'OURO — atualização v26.2\n       NOVIDADES v26.2:",
"""       FOLHADOS D'OURO — atualização v26.3
       NOVIDADES v26.3:
       • Confiabilidade: falha de armazenamento local passa a bloquear a operação e avisar claramente.
       • Firebase SDK passa a ser servido localmente e pré-cacheado para boot offline previsível.
       • Assistente migra do Gemini 2.0 Flash desativado para Gemini 3.6 Flash estável, com erro visível e teste em Config.
       • Após operadores já terem sido implantados, lista vazia não libera mais o app sem login (fail-closed).
       • PIN recebe limitação temporária após tentativas repetidas; relógio do aparelho é conferido contra o servidor.
       • Cancelamento de balde distingue insumo realmente usado de lançamento por engano, com estorno/reaplicação auditáveis.
       • Nenhum peso, total, fermento, tempo de receita ou snapshot histórico foi alterado.
       NOVIDADES v26.2:""",
'cabeçalho v26.3')

one("versao:'26.2'","versao:'26.3'",'versão do backup')

# Firebase SDK local — mesma versão 10.13.2, sem mudar a API compat
for remote,local in [
('https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js','vendor/firebase-app-compat.js'),
('https://www.gstatic.com/firebasejs/10.13.2/firebase-auth-compat.js','vendor/firebase-auth-compat.js'),
('https://www.gstatic.com/firebasejs/10.13.2/firebase-database-compat.js','vendor/firebase-database-compat.js')]:
    one(f'<script src=\"{remote}\"></script>',f'<script src=\"{local}\"></script>','Firebase local '+local)

# Botão de diagnóstico do Assistente
one(
'  <input id="inp-key" class="inp" type="password" placeholder="AIza..." autocomplete="off">',
'''  <input id="inp-key" class="inp" type="password" placeholder="AIza..." autocomplete="off">
  <button class="link-btn" id="btn-testar-ia" style="width:100%;text-align:center;margin-top:-.2rem;margin-bottom:.4rem" onclick="testarAssistenteConfig()">Testar Assistente</button>
  <div class="cfg-s" id="ai-test-status" style="font-size:.68rem;line-height:1.4;margin-top:-.15rem"></div>''',
'botão testar Assistente')

# Diagnóstico de versão/armazenamento em Config
pat=r'(<div class="cfg-s" id="device-info"[^>]*>Identificação Firebase: —</div>)'
m=re.search(pat,text)
if not m: raise SystemExit('device-info não encontrado')
insert=m.group(1)+'''\n  <div class="cfg-s" style="font-size:.68rem;line-height:1.45">Versão 26.3 · cache fdo-v26-3 · Firebase SDK local</div>
  <div class="cfg-s" id="storage-info" style="font-size:.68rem;line-height:1.45">Armazenamento local: verificando…</div>'''
text=text[:m.start()]+insert+text[m.end():]

# Escrita local segura + diagnóstico. O wrapper também sinaliza falhas em setItem diretos antigos.
old="const LS={g:(k,d)=>{try{const v=localStorage.getItem(k);return v===null?d:JSON.parse(v)}catch{return d}},s:(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch{} FB.push(k,v);}};"
new=r'''let _storageFalhaMostrada=false;
function storageFalhou(err,chave){
  console.error('[STORAGE] falha ao gravar',chave,err);
  if(_storageFalhaMostrada)return;_storageFalhaMostrada=true;
  setTimeout(()=>{
    if(document.getElementById('storage-fatal-v263'))return;
    const bg=document.createElement('div');bg.id='storage-fatal-v263';
    bg.style.cssText='position:fixed;inset:0;z-index:20000;background:rgba(0,0,0,.94);display:flex;align-items:center;justify-content:center;padding:1rem';
    const card=document.createElement('div');card.style.cssText='width:min(100%,22rem);background:#1a1305;border:2px solid #f87171;border-radius:.7rem;padding:1.1rem;color:#f0e6c8;font-family:Georgia,serif;text-align:center;line-height:1.45';
    card.innerHTML='<div style="font-size:2rem">⚠️</div><div style="font-size:1.05rem;color:#f87171;font-weight:bold;margin:.35rem 0">Falha ao salvar neste aparelho</div><div style="font-size:.78rem">A operação foi interrompida para evitar perda silenciosa de dados. Não continue a produção neste aparelho. Feche e abra o PWA novamente; se o aviso voltar, use outro aparelho e avise a gerência.</div><button style="margin-top:.8rem;width:100%;min-height:2.6rem;background:#c9973a;border:0;border-radius:.4rem;font-family:Georgia,serif;font-weight:bold;font-size:.8rem" onclick="location.reload()">Recarregar aplicativo</button>';
    bg.appendChild(card);document.body.appendChild(bg);
  },0);
}
try{
  const _storageSetItemNativo=Storage.prototype.setItem;
  Storage.prototype.setItem=function(k,v){try{return _storageSetItemNativo.call(this,k,v)}catch(e){storageFalhou(e,k);throw e}};
}catch(e){console.warn('[STORAGE] proteção global indisponível',e)}
async function atualizarStorageInfo(){
  const el=document.getElementById('storage-info');if(!el)return;
  try{
    const est=navigator.storage&&navigator.storage.estimate?await navigator.storage.estimate():null;
    if(!est||!Number(est.quota)){el.textContent='Armazenamento local: disponível · medição não suportada';return;}
    const used=Number(est.usage)||0,quota=Number(est.quota)||0,pct=quota?(used/quota*100):0;
    el.textContent='Armazenamento local: '+(used/1048576).toFixed(1)+' MB de '+(quota/1048576).toFixed(0)+' MB · '+pct.toFixed(1)+'%'+(pct>=80?' · ATENÇÃO':' · OK');
    el.style.color=pct>=80?'var(--red)':'var(--mut)';
  }catch(e){el.textContent='Armazenamento local: diagnóstico indisponível';}
}
const LS={g:(k,d)=>{try{const v=localStorage.getItem(k);return v===null?d:JSON.parse(v)}catch{return d}},s:(k,v)=>{try{localStorage.setItem(k,JSON.stringify(v))}catch(e){storageFalhou(e,k);throw e}FB.push(k,v);return true;}};'''
one(old,new,'LS seguro')

one('function carregarConfig(){\n','function carregarConfig(){\n  atualizarStorageInfo();\n','diagnóstico ao abrir Config')

# Operadores: depois que o sistema foi implantado uma vez, lista vazia não pode reabrir modo legado.
one(
"  lista(){ return LS.g('fdo_operadores',[]); },",
"""  lista(){ const arr=LS.g('fdo_operadores',[]);if(Array.isArray(arr)&&arr.length){try{localStorage.setItem('fdo_operadores_inicializados',JSON.stringify(true))}catch(e){storageFalhou(e,'fdo_operadores_inicializados')}}return arr; },""",
'marca implantação de operadores')

old_block="""  if(!OP.lista().length){
    _bootPendenteOperadores=true;
    setTimeout(()=>{ _bootPendenteOperadores=false; }, 10000);
    ir('start');
    return;
  }"""
new_block="""  if(!OP.lista().length){
    if(LS.g('fdo_operadores_inicializados',false)===true){
      const msg='O cadastro de operadores já existia neste aparelho, mas está indisponível. Conecte à internet e toque em “Verificar autorização”. A produção foi bloqueada para evitar acesso sem login.';
      if(typeof DEVICE!=='undefined'&&DEVICE.mostrar)DEVICE.mostrar(msg,'Cadastro de operadores indisponível');else alert(msg);
      return;
    }
    _bootPendenteOperadores=true;
    setTimeout(()=>{ _bootPendenteOperadores=false; }, 10000);
    ir('start');
    return;
  }"""
one(old_block,new_block,'fail-closed de operadores')

# Limite simples de tentativas de PIN, sem tornar o uso normal mais lento.
new_pin=r'''let pinFalhasV263=0,pinBloqAteV263=0;
function verificarPin(){
  const agora=Date.now();
  if(agora<pinBloqAteV263){
    st.pinBuf='';atualizarPinDots();
    document.getElementById('pin-err').textContent='Muitas tentativas. Aguarde '+Math.ceil((pinBloqAteV263-agora)/1000)+' s.';
    return;
  }
  if(st.pinBuf===pinEsperado()){
    pinFalhasV263=0;pinBloqAteV263=0;
    // Só o acesso à produção fica desbloqueado pela sessão; o Config e o
    // login de operador pedem senha sempre.
    if(st.pinTipo==='producao') sessaoDesbloqueada=true;
    const fn=st.pinAlvo; st.pinAlvo=null; st.pinBuf='';
    if(typeof fn==='function') fn(); else ir('start');
  }else{
    pinFalhasV263++;st.pinBuf=''; atualizarPinDots();
    if(pinFalhasV263>=5){pinFalhasV263=0;pinBloqAteV263=Date.now()+30000;document.getElementById('pin-err').textContent='Muitas tentativas. Aguarde 30 s.';}
    else document.getElementById('pin-err').textContent='Senha incorreta. Tente de novo.';
    const w=document.getElementById('pin-wrap');
    w.classList.remove('err'); void w.offsetWidth; w.classList.add('err');
  }
}
'''
between('function verificarPin(){','function cancelarPin(){',new_pin,'limite de PIN')

# Relógio: compara com o offset de servidor do Realtime Database.
clock=r'''let _relogioAvisadoV263=false;
function verificarRelogioServidor(){
  if(!FB.db)return;
  try{
    FB.db.ref('.info/serverTimeOffset').once('value').then(snap=>{
      const off=Number(snap.val())||0;
      if(Math.abs(off)>5*60*1000&&!_relogioAvisadoV263){
        _relogioAvisadoV263=true;
        const min=Math.round(Math.abs(off)/60000);
        alert('⚠️ Relógio do aparelho parece incorreto ('+min+' min de diferença). Ative Data e hora automáticas no Android antes de registrar novas produções.');
      }
    }).catch(()=>{});
  }catch(e){}
}

'''
one('const DEVICE={',clock+'const DEVICE={','checagem de relógio')
one("if(!firebase.apps.length)firebase.initializeApp(FB_CFG);FB.db=firebase.database();this.auth=firebase.auth();","if(!firebase.apps.length)firebase.initializeApp(FB_CFG);FB.db=firebase.database();this.auth=firebase.auth();verificarRelogioServidor();",'aciona relógio no Firebase')

# Gemini: modelo estável recomendado pelo Google para substituir 2.0 Flash + falha explícita.
new_ai=r'''const GEMINI_MODEL='gemini-3.6-flash';
async function perguntarGemini(pergunta){
  const key=getKey();if(!key)return;
  const p=RECEITA[st.step];
  const ctx=`Passo atual ${p.id}, ${p.grupo}, ${p.nome} ${p.qty}.\
Pergunta: "${pergunta}"`;
  try{
    setDot('off','Consultando...');
    const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${key}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({system_instruction:{parts:[{text:montarSystem()}]},contents:[{role:'user',parts:[{text:ctx}]}],generationConfig:{maxOutputTokens:150}})});
    const data=await r.json().catch(()=>({}));
    if(!r.ok)throw new Error((data&&data.error&&data.error.message)||('HTTP '+r.status));
    const resp=data?.candidates?.[0]?.content?.parts?.[0]?.text||'';
    setDot('on','Ouvindo');
    if(resp){mostrarAI(resp);falar(resp);}else mostrarAI('Assistente não retornou uma resposta. A produção continua normalmente.');
  }catch(err){console.warn('[IA] indisponível',err);setDot('on','Ouvindo · IA indisponível');mostrarAI('Assistente indisponível agora. A produção continua normalmente.');}
}
async function testarAssistenteConfig(){
  const out=document.getElementById('ai-test-status'),btn=document.getElementById('btn-testar-ia'),key=String(document.getElementById('inp-key').value||'').trim();
  if(!out||!btn)return;if(!key){out.style.color='var(--red)';out.textContent='Informe a chave Gemini para testar.';return;}
  btn.disabled=true;out.style.color='var(--mut)';out.textContent='Testando '+GEMINI_MODEL+'…';
  try{
    const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent?key=${key}`,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({contents:[{role:'user',parts:[{text:'Responda somente OK'}]}],generationConfig:{maxOutputTokens:10}})});
    const data=await r.json().catch(()=>({}));if(!r.ok)throw new Error((data&&data.error&&data.error.message)||('HTTP '+r.status));
    out.style.color='var(--grn)';out.textContent='✓ Assistente conectado · '+GEMINI_MODEL;
  }catch(e){out.style.color='var(--red)';out.textContent='⚠ Não foi possível acessar o Assistente. Confira internet e chave API.';}
  finally{btn.disabled=false;}
}

'''
between('async function perguntarGemini(pergunta){','function falar(texto){',new_ai,'Gemini v26.3')

# Estoque: estorno é novo movimento, nunca apaga a baixa original.
adjust=r'''function estoqueMovimentoPorId(id){return estoqueMovimentos().find(m=>m&&m.id===id)||null;}
function registrarEstornoEstoqueLote(lote){
  if(!lote||!lote.id||!lote.cancelado)return false;const cts=Number(lote.cancelado.emTs)||0;if(!cts)return false;
  const id='estorno_saida_'+lote.id+'_'+cts;if(estoqueTemMovimento(id))return false;
  const saida=estoqueMovimentoPorId('saida_receita_'+lote.id);if(!saida)return false;const itens={};
  Object.entries(saida.itens||{}).forEach(([k,v])=>{const n=Number(v)||0;if(n)itens[k]=-n;});if(!Object.keys(itens).length)return false;
  const reg={id,tipo:'estorno_cancelamento',em:new Date(cts).toLocaleString('pt-BR'),emTs:cts+1,atualizadoTs:cts+1,op:(lote.cancelado.op||getOp()),loteId:lote.id,loteNum:lote.num,receita:lote.receita,receitaNome:lote.receitaNome||lote.rotulo||'',itens,observacao:'Balde cancelado como lançamento por engano; insumos não utilizados.',dispositivo:(typeof DEVICE!=='undefined'?DEVICE.audit():null)};
  ESTOQUE_SYNC.localPush('movimentos',reg);return true;
}
function registrarReaplicacaoEstoqueLote(lote){
  if(!lote||!lote.id||!lote.restaurado)return false;const rts=Number(lote.restaurado.emTs)||0;if(!rts)return false;
  const id='reaplica_saida_'+lote.id+'_'+rts;if(estoqueTemMovimento(id))return false;
  const saida=estoqueMovimentoPorId('saida_receita_'+lote.id);if(!saida)return false;const itens={};
  Object.entries(saida.itens||{}).forEach(([k,v])=>{const n=Number(v)||0;if(n)itens[k]=n;});if(!Object.keys(itens).length)return false;
  const reg={id,tipo:'reaplicacao_restauro',em:new Date(rts).toLocaleString('pt-BR'),emTs:rts+1,atualizadoTs:rts+1,op:(lote.restaurado.op||getOp()),loteId:lote.id,loteNum:lote.num,receita:lote.receita,receitaNome:lote.receitaNome||lote.rotulo||'',itens,observacao:'Balde restaurado; baixa de insumos reaplicada.',dispositivo:(typeof DEVICE!=='undefined'?DEVICE.audit():null)};
  ESTOQUE_SYNC.localPush('movimentos',reg);return true;
}
function estoqueReconciliarAjustesCancelamento(){
  let n=0;LS.g('fdo_lotes',[]).forEach(l=>{if(!l||!l.cancelado||l.cancelado.estoqueAcao!=='estornar')return;const c=Number(l.cancelado.emTs)||0,r=Number(l.restaurado&&l.restaurado.emTs)||0;if(r>c){if(registrarReaplicacaoEstoqueLote(l))n++;}else if(registrarEstornoEstoqueLote(l))n++;});return n;
}
'''
one('let estoqueReconciliando=false;',adjust+'let estoqueReconciliando=false;','funções de estorno')
one("let n=0;LS.g('fdo_lotes',[]).forEach(l=>{if(l&&Number(l.criadoTs)>=inicio&&registrarSaidaEstoqueLote(l))n++;});return n;","let n=0;LS.g('fdo_lotes',[]).forEach(l=>{if(l&&Number(l.criadoTs)>=inicio&&registrarSaidaEstoqueLote(l))n++;});n+=estoqueReconciliarAjustesCancelamento();return n;",'reconcilia cancelamentos')

old_del=r'''function apagarLote(id){
  if(!OP.pode('apagar')){alert('Você não tem permissão para cancelar baldes.\
Peça ao administrador.');return;}
  const todos=LS.g('fdo_lotes',[]),lote=todos.find(l=>l.id===id);if(!lote||!loteAtivo(lote))return;
  if(!confirm(`Cancelar o Balde #${lote.num}?\
\
Ele sai das etapas de produção, mas permanece no histórico e pode ser restaurado.`))return;
  lote.cancelado={em:new Date().toLocaleString('pt-BR'),emTs:Date.now(),op:getOp()};LS.s('fdo_lotes',todos);renderHist();
}'''
new_del=r'''function apagarLote(id){
  if(!OP.pode('apagar')){alert('Você não tem permissão para cancelar baldes.\
Peça ao administrador.');return;}
  const todos=LS.g('fdo_lotes',[]),lote=todos.find(l=>l.id===id);if(!lote||!loteAtivo(lote))return;
  if(!confirm(`Cancelar o Balde #${lote.num}?\
\
Ele sai das etapas de produção, mas permanece no histórico e pode ser restaurado.`))return;
  let estoqueAcao='manter';
  if(estoqueTemMovimento('saida_receita_'+lote.id)){
    const usados=confirm(`ESTOQUE DO BALDE #${lote.num}\
\
Os ingredientes deste balde chegaram a ser utilizados?\
\
OK = SIM · manter a baixa no estoque\
Cancelar = NÃO · foi lançamento por engano e a baixa será estornada`);
    if(!usados){if(!confirm('Confirmar que os ingredientes NÃO foram utilizados e que a baixa deve ser estornada?'))return;estoqueAcao='estornar';}
  }
  lote.cancelado={em:new Date().toLocaleString('pt-BR'),emTs:Date.now(),op:getOp(),estoqueAcao};LS.s('fdo_lotes',todos);if(estoqueAcao==='estornar')registrarEstornoEstoqueLote(lote);renderHist();
}'''
one(old_del,new_del,'cancelamento com estoque')

old_restore="""function restaurarLote(id){
  if(!OP.pode('apagar'))return;const todos=LS.g('fdo_lotes',[]),lote=todos.find(l=>l.id===id);if(!lote||loteAtivo(lote))return;
  if(!confirm(`Restaurar o Balde #${lote.num} para a produção?`))return;
  lote.restaurado={em:new Date().toLocaleString('pt-BR'),emTs:Date.now(),op:getOp()};LS.s('fdo_lotes',todos);renderHist();
}"""
new_restore="""function restaurarLote(id){
  if(!OP.pode('apagar'))return;const todos=LS.g('fdo_lotes',[]),lote=todos.find(l=>l.id===id);if(!lote||loteAtivo(lote))return;
  if(!confirm(`Restaurar o Balde #${lote.num} para a produção?`))return;
  const reaplicar=!!(lote.cancelado&&lote.cancelado.estoqueAcao==='estornar');lote.restaurado={em:new Date().toLocaleString('pt-BR'),emTs:Date.now(),op:getOp(),estoqueReaplicar:reaplicar};LS.s('fdo_lotes',todos);if(reaplicar)registrarReaplicacaoEstoqueLote(lote);renderHist();
}"""
one(old_restore,new_restore,'restauro com estoque')

one("const tit=m.tipo==='entrada'?'Entrada recebida':('Saída automática · Balde #'+(m.loteNum||'—'));","const tit=m.tipo==='entrada'?'Entrada recebida':m.tipo==='estorno_cancelamento'?('Estorno · Balde #'+(m.loteNum||'—')):m.tipo==='reaplicacao_restauro'?('Saída reaplicada · Balde #'+(m.loteNum||'—')):('Saída automática · Balde #'+(m.loteNum||'—'));",'título movimentos de estoque')

INDEX.write_text(text,encoding='utf-8')

# Vendoriza exatamente a versão já usada pelo app. Só muda a dependência de rede no boot.
VENDOR=ROOT/'vendor';VENDOR.mkdir(exist_ok=True)
urls={
'firebase-app-compat.js':'https://www.gstatic.com/firebasejs/10.13.2/firebase-app-compat.js',
'firebase-auth-compat.js':'https://www.gstatic.com/firebasejs/10.13.2/firebase-auth-compat.js',
'firebase-database-compat.js':'https://www.gstatic.com/firebasejs/10.13.2/firebase-database-compat.js',
}
for name,url in urls.items():
    data=urllib.request.urlopen(url,timeout=30).read()
    if len(data)<1000 or b'firebase' not in data.lower():raise SystemExit('download Firebase inválido: '+name)
    (VENDOR/name).write_bytes(data)

(VENDOR/'README.md').write_text('Firebase JavaScript SDK compat 10.13.2, copiado do CDN oficial gstatic para permitir boot offline previsível. Fontes: https://www.gstatic.com/firebasejs/10.13.2/ . O código do aplicativo continua usando a API compat existente.\n',encoding='utf-8')
print('PATCH v26.3 aplicado em index.html + vendor Firebase')
