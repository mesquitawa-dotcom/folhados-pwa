from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'index.html'
s=p.read_text(encoding='utf-8')

def between(start,end,new,label):
    global s
    a=s.find(start)
    if a<0: raise SystemExit(label+': início não encontrado')
    b=s.find(end,a+len(start))
    if b<0: raise SystemExit(label+': fim não encontrado')
    s=s[:a]+new+s[b:]

old='<!-- Firebase Realtime Database (compat, namespaced) — CDN, sem build -->'
new='<!-- Firebase Realtime Database (compat, namespaced) — SDK local, sem build -->'
if s.count(old)!=1: raise SystemExit('comentário Firebase inesperado')
s=s.replace(old,new,1)

# Cancelamento/restauro: preserva exatamente as quebras de linha e garante
# que uma restauração após estorno sempre reconstrua estorno + reaplicação.
block=r'''function apagarLote(id){
  if(!OP.pode('apagar')){alert('Você não tem permissão para cancelar baldes.\nPeça ao administrador.');return;}
  const todos=LS.g('fdo_lotes',[]),lote=todos.find(l=>l.id===id);if(!lote||!loteAtivo(lote))return;
  if(!confirm(`Cancelar o Balde #${lote.num}?\n\nEle sai das etapas de produção, mas permanece no histórico e pode ser restaurado.`))return;
  let estoqueAcao='manter';
  if(estoqueTemMovimento('saida_receita_'+lote.id)){
    const usados=confirm(`ESTOQUE DO BALDE #${lote.num}\n\nOs ingredientes deste balde chegaram a ser utilizados?\n\nOK = SIM · manter a baixa no estoque\nCancelar = NÃO · foi lançamento por engano e a baixa será estornada`);
    if(!usados){if(!confirm('Confirmar que os ingredientes NÃO foram utilizados e que a baixa deve ser estornada?'))return;estoqueAcao='estornar';}
  }
  lote.cancelado={em:new Date().toLocaleString('pt-BR'),emTs:Date.now(),op:getOp(),estoqueAcao};LS.s('fdo_lotes',todos);if(estoqueAcao==='estornar')registrarEstornoEstoqueLote(lote);renderHist();
}
function restaurarLote(id){
  if(!OP.pode('apagar'))return;const todos=LS.g('fdo_lotes',[]),lote=todos.find(l=>l.id===id);if(!lote||loteAtivo(lote))return;
  if(!confirm(`Restaurar o Balde #${lote.num} para a produção?`))return;
  const reaplicar=!!(lote.cancelado&&lote.cancelado.estoqueAcao==='estornar');lote.restaurado={em:new Date().toLocaleString('pt-BR'),emTs:Date.now(),op:getOp(),estoqueReaplicar:reaplicar};LS.s('fdo_lotes',todos);if(reaplicar){registrarEstornoEstoqueLote(lote);registrarReaplicacaoEstoqueLote(lote);}renderHist();
}

'''
between('function apagarLote(id){','// Migra sessões antigas concluídas',block+'// Migra sessões antigas concluídas','cancelamento/restauro')

# Reconciliador: se houver restauro, garante primeiro o estorno e só então reaplica.
old="function estoqueReconciliarAjustesCancelamento(){\n  let n=0;LS.g('fdo_lotes',[]).forEach(l=>{if(!l||!l.cancelado||l.cancelado.estoqueAcao!=='estornar')return;const c=Number(l.cancelado.emTs)||0,r=Number(l.restaurado&&l.restaurado.emTs)||0;if(r>c){if(registrarReaplicacaoEstoqueLote(l))n++;}else if(registrarEstornoEstoqueLote(l))n++;});return n;\n}"
new="function estoqueReconciliarAjustesCancelamento(){\n  let n=0;LS.g('fdo_lotes',[]).forEach(l=>{if(!l||!l.cancelado||l.cancelado.estoqueAcao!=='estornar')return;const c=Number(l.cancelado.emTs)||0,r=Number(l.restaurado&&l.restaurado.emTs)||0;if(r>c){if(registrarEstornoEstoqueLote(l))n++;if(registrarReaplicacaoEstoqueLote(l))n++;}else if(registrarEstornoEstoqueLote(l))n++;});return n;\n}"
if s.count(old)!=1: raise SystemExit('reconciliador de cancelamento inesperado')
s=s.replace(old,new,1)

# Gemini: mantém GenerateContent REST compatível, mas API key vai em header,
# conforme documentação atual; preserva quebra de linha do contexto.
ai=r'''const GEMINI_MODEL='gemini-3.6-flash';
async function perguntarGemini(pergunta){
  const key=getKey();if(!key)return;
  const p=RECEITA[st.step];
  const ctx=`Passo atual ${p.id}, ${p.grupo}, ${p.nome} ${p.qty}.\nPergunta: "${pergunta}"`;
  try{
    setDot('off','Consultando...');
    const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`,{method:'POST',headers:{'Content-Type':'application/json','x-goog-api-key':key},body:JSON.stringify({system_instruction:{parts:[{text:montarSystem()}]},contents:[{role:'user',parts:[{text:ctx}]}],generationConfig:{maxOutputTokens:150}})});
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
    const r=await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`,{method:'POST',headers:{'Content-Type':'application/json','x-goog-api-key':key},body:JSON.stringify({contents:[{role:'user',parts:[{text:'Responda somente OK'}]}],generationConfig:{maxOutputTokens:10}})});
    const data=await r.json().catch(()=>({}));if(!r.ok)throw new Error((data&&data.error&&data.error.message)||('HTTP '+r.status));
    out.style.color='var(--grn)';out.textContent='✓ Assistente conectado · '+GEMINI_MODEL;
  }catch(e){out.style.color='var(--red)';out.textContent='⚠ Não foi possível acessar o Assistente. Confira internet e chave API.';}
  finally{btn.disabled=false;}
}

'''
between("const GEMINI_MODEL='gemini-3.6-flash';",'function falar(texto){',ai,'Gemini final')

p.write_text(s,encoding='utf-8')
print('Acabamento v26.3 aplicado')
