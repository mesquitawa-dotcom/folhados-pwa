from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'index.html'
html=P.read_text(encoding='utf-8')

def rep(old,new,label,count=1):
    global html
    n=html.count(old)
    if n!=count:
        raise SystemExit(f'{label}: esperado {count}, encontrado {n}')
    html=html.replace(old,new,count)

def sub(pattern,repl,label,count=1,flags=0):
    global html
    html2,n=re.subn(pattern,repl,html,count=count,flags=flags)
    if n!=count:
        raise SystemExit(f'{label}: esperado {count}, encontrado {n}')
    html=html2

# ── cabeçalho / versão ───────────────────────────────────────────────
rep("       FOLHADOS D'OURO — atualização v26.1\n       NOVIDADES v26.1:","""       FOLHADOS D'OURO — atualização v26.2
       NOVIDADES v26.2:
       • Lembrete de conferência de estoque por operador e dia da semana configuráveis.
       • O responsável recebe pop-up no dia programado; conferência já registrada no dia não volta a ser cobrada.
       • Tempos do batimento passam a pertencer à receita e deixam de ser configuração global de rotina.
       • Os tempos anteriores (4 fases em sequência) viram base de migração para todas as receitas já existentes.
       • Receita completa e Receita Teste permitem alterar os tempos de batimento; mudanças definitivas entram na auditoria.
       • Balde e batimento guardam a configuração usada, preservando históricos e retomada do cronômetro.
       NOVIDADES v26.1:""","cabeçalho v26.2")

# ── CSS do pop-up ────────────────────────────────────────────────────
css_anchor="    /* ════ GESTÃO DE RECEITAS DEFINITIVAS (v26.1) ════ */"
css_new="""    /* ════ LEMBRETE DE ESTOQUE (v26.2) ════ */
    .est-rem-bg{position:fixed;inset:0;z-index:9999;background:rgba(0,0,0,.78);display:none;align-items:center;justify-content:center;padding:1rem}
    .est-rem-bg.on{display:flex}.est-rem-card{width:min(100%,20rem);background:var(--bg3);border:1px solid var(--gold);border-radius:.7rem;padding:1.15rem;box-shadow:0 .5rem 2rem rgba(0,0,0,.55)}
    .est-rem-icon{font-size:2.5rem;text-align:center}.est-rem-title{font-size:1.15rem;color:var(--gl);font-weight:bold;text-align:center;margin:.45rem 0}
    .est-rem-txt{font-size:.82rem;color:var(--text);line-height:1.5;text-align:center;margin-bottom:.9rem}.est-rem-actions{display:flex;flex-direction:column;gap:.5rem}

"""+css_anchor
rep(css_anchor,css_new,'css lembrete')

# ── configurações: sai batimento global; entra responsável/dia ───────
pat=r'''  <div class="cfg-sep"></div>\n  <div class="cfg-s" style="font-size:\.75rem">⏱ Tempos do batimento \(minutos, somados em sequência\):</div>\n  <div class="cfg-grid">\n    <label class="cfg-mini">Batimento inicial lento<input id="inp-bt1".*?</div>\n  <label class="cfg-mini" style="margin-top:\.1rem">Dividir massa em \(partes p/ gelar\)<input id="inp-bdiv"'''
repl='''  <div class="cfg-sep"></div>
  <div class="cfg-s" style="font-size:.75rem">📦 Lembrete da conferência de estoque:</div>
  <div class="cfg-grid">
    <label class="cfg-mini">Responsável<select id="inp-est-cont-op" class="inp"><option value="">Sem lembrete</option></select></label>
    <label class="cfg-mini">Dia da semana<select id="inp-est-cont-dia" class="inp">
      <option value="1">Segunda-feira</option><option value="2">Terça-feira</option><option value="3">Quarta-feira</option><option value="4">Quinta-feira</option><option value="5">Sexta-feira</option><option value="6">Sábado</option><option value="0">Domingo</option>
    </select></label>
  </div>
  <div class="cfg-s" style="font-size:.68rem;line-height:1.45">O operador escolhido recebe um aviso ao entrar no aplicativo no dia programado. Só aparecem aqui operadores ativos com permissão para conferência de estoque.</div>
  <div class="cfg-sep"></div>
  <div class="cfg-s" style="font-size:.72rem;line-height:1.45;color:var(--gold)">⏱ Os tempos do batimento agora são configurados dentro de cada receita, em <b>Receita completa → Editar receita</b>.</div>
  <label class="cfg-mini" style="margin-top:.1rem">Dividir massa em (partes p/ gelar)<input id="inp-bdiv"'''
sub(pat,repl,'configuração estoque/batimento',flags=re.S)

# ── editor de receita: bloco batimento ───────────────────────────────
rep('    <div id="receita-edit-fermentacao"></div>\n    <div class="rec-edit-card">','    <div id="receita-edit-fermentacao"></div>\n    <div id="receita-edit-batimento"></div>\n    <div class="rec-edit-card">','container batimento receita')

# ── Receita Teste: tempos por lote experimental ──────────────────────
anchor='''    <div class="teste-card">
      <div class="teste-card-title">Observações do teste</div>'''
teste_bat='''    <div class="teste-card">
      <div class="teste-card-title">Batimento · minutos em sequência</div>
      <div class="teste-grid">
        <label class="teste-field"><span class="teste-label">Inicial lento</span><input id="teste-bt1" class="teste-inp" type="number" inputmode="decimal" min="0" step="0.5" oninput="atualizarResumoTeste()"></label>
        <label class="teste-field"><span class="teste-label">Até colocar fermento</span><input id="teste-bt2" class="teste-inp" type="number" inputmode="decimal" min="0" step="0.5" oninput="atualizarResumoTeste()"></label>
        <label class="teste-field"><span class="teste-label">Até colocar a massa</span><input id="teste-bt3" class="teste-inp" type="number" inputmode="decimal" min="0" step="0.5" oninput="atualizarResumoTeste()"></label>
        <label class="teste-field"><span class="teste-label">Até ver ponto de véu</span><input id="teste-bt4" class="teste-inp" type="number" inputmode="decimal" min="0" step="0.5" oninput="atualizarResumoTeste()"></label>
      </div>
      <div class="teste-note" style="margin-top:.45rem">Começa com os tempos da receita base. Altere somente se este teste também exigir outro batimento.</div>
    </div>
'''+anchor
rep(anchor,teste_bat,'batimento Receita Teste')

# ── pop-up de estoque ────────────────────────────────────────────────
pop_anchor='<!-- ═══ CONTROLE DE ESTOQUE (v26.0) ═══ -->'
popup='''<div id="estoque-lembrete-bg" class="est-rem-bg" role="dialog" aria-modal="true" aria-labelledby="estoque-lembrete-title">
  <div class="est-rem-card">
    <div class="est-rem-icon">📦</div>
    <div class="est-rem-title" id="estoque-lembrete-title">Hoje é dia da contagem</div>
    <div class="est-rem-txt" id="estoque-lembrete-txt">Hoje é dia de fazer a contagem do estoque.</div>
    <div class="est-rem-actions">
      <button class="btn-main" onclick="estoqueLembreteAgora()">✓ Fazer contagem agora</button>
      <button class="link-btn" style="width:100%;text-align:center" onclick="estoqueLembreteDepois()">Mais tarde</button>
    </div>
  </div>
</div>

'''+pop_anchor
rep(pop_anchor,popup,'popup estoque')

# ── helpers dos tempos ───────────────────────────────────────────────
anchor="function getTara(){ return Number(LS.g('fdo_tara_balde',474))||474; } // tara (g) do balde vazio, para conferência"
helpers=anchor+'''\n\n// v26.2 — tempos do batimento pertencem à receita. As chaves antigas ficam somente como base/fallback de migração.
const BATIMENTO_CAMPOS=[
  {k:'t1',nome:'Batimento inicial lento'},
  {k:'t2',nome:'Colocar fermento'},
  {k:'t3',nome:'Colocar a massa'},
  {k:'t4',nome:'Ver ponto de véu'}
];
function batTemposNormalizar(v,base){
  const b=base||{t1:getBatT1(),t2:getBatT2(),t3:getBatT3(),t4:getBatT4()},o={};
  BATIMENTO_CAMPOS.forEach(c=>{const n=Number(v&&v[c.k]);o[c.k]=(isFinite(n)&&n>=0)?n:Number(b[c.k]);});return o;
}
function batTemposBaseLegado(){return batTemposNormalizar({t1:getBatT1(),t2:getBatT2(),t3:getBatT3(),t4:getBatT4()},{t1:4,t2:6,t3:3,t4:2});}
function batTemposReceita(r){return batTemposNormalizar(r&&r.batimento,batTemposBaseLegado());}
function batTemposDoLote(l){
  const b=l&&l.etapas&&l.etapas.batimento;if(b&&b.temposProgramados)return batTemposNormalizar(b.temposProgramados,batTemposBaseLegado());
  if(l&&l.receitaSnapshot&&l.receitaSnapshot.batimento)return batTemposNormalizar(l.receitaSnapshot.batimento,batTemposBaseLegado());
  if(l&&l.batimentoConfig)return batTemposNormalizar(l.batimentoConfig,batTemposBaseLegado());
  return batTemposBaseLegado();
}
function batFmtMin(n){n=Number(n)||0;return Number.isInteger(n)?String(n):String(Math.round(n*10)/10).replace('.',',');}
function batTemposTexto(v){const b=batTemposNormalizar(v,batTemposBaseLegado());return batFmtMin(b.t1)+' + '+batFmtMin(b.t2)+' + '+batFmtMin(b.t3)+' + '+batFmtMin(b.t4)+' min';}
'''
rep(anchor,helpers,'helpers batimento')

# ── catálogo em memória sempre ganha tempos efetivos ─────────────────
old='''function aplicarReceitasDefinitivas(){
  Object.keys(RECEITAS).forEach(k=>{if(!RECEITAS_PADRAO_IDS.includes(k))delete RECEITAS[k];});
  RECEITAS_PADRAO_IDS.forEach(k=>{RECEITAS[k]=clonarReceita(RECEITAS_ORIGINAIS[k]);});
  receitasDefinitivas().forEach(reg=>{if(reg&&reg.id&&reg.receita&&Array.isArray(reg.receita.passos))RECEITAS[reg.id]=clonarReceita(reg.receita);});
}'''
new='''function aplicarReceitasDefinitivas(){
  Object.keys(RECEITAS).forEach(k=>{if(!RECEITAS_PADRAO_IDS.includes(k))delete RECEITAS[k];});
  RECEITAS_PADRAO_IDS.forEach(k=>{RECEITAS[k]=clonarReceita(RECEITAS_ORIGINAIS[k]);});
  receitasDefinitivas().forEach(reg=>{if(reg&&reg.id&&reg.receita&&Array.isArray(reg.receita.passos))RECEITAS[reg.id]=clonarReceita(reg.receita);});
  Object.values(RECEITAS).forEach(r=>{if(r&&!r.batimento)r.batimento=batTemposBaseLegado();});
}'''
rep(old,new,'aplicar receitas')

# ── migração segura: receitas existentes + baldes pendentes ──────────
anchor='''function congelarSnapshotsReceitasLegadas(){
  const todos=LS.g('fdo_lotes',[]);let mudou=false;const agora=Date.now();
  todos.forEach(l=>{if(!l||l.receitaSnapshot||!RECEITAS_PADRAO_IDS.includes(l.receita)||!RECEITAS_ORIGINAIS[l.receita])return;l.receitaSnapshot=clonarReceita(RECEITAS_ORIGINAIS[l.receita]);l.snapshotMigrado={emTs:agora,origem:'base v26.0 para preservação futura'};mudou=true;});
  if(mudou)LS.s('fdo_lotes',todos);return mudou;
}'''
mig=anchor+'''\nfunction congelarBatimentoBaldesPendentesV262(){
  if(LS.g('fdo_migr_bat_baldes_v262',false))return false;const todos=LS.g('fdo_lotes',[]),base=batTemposBaseLegado();let mudou=false;
  todos.forEach(l=>{const feito=l&&l.etapas&&l.etapas.batimento&&l.etapas.batimento.feito;if(!l||feito||!loteAtivo(l)||l.batimentoConfig||(l.receitaSnapshot&&l.receitaSnapshot.batimento))return;l.batimentoConfig=clonarReceita(base);l.batimentoConfigMigradoV262={emTs:Date.now(),origem:'tempos globais vigentes antes da v26.2'};mudou=true;});
  if(mudou)LS.s('fdo_lotes',todos);LS.s('fdo_migr_bat_baldes_v262',true);return mudou;
}
function migrarBatimentoReceitasV262(){
  if(LS.g('fdo_migr_bat_receitas_v262',false))return;aplicarReceitasDefinitivas();const base=batTemposBaseLegado(),agora=new Date(),lista=receitasOrdenadas();
  lista.forEach(x=>{const ant=receitaDefRegistro(x.id);if(ant&&ant.receita&&ant.receita.batimento)return;const rec=clonarReceita(x.r);rec.batimento=clonarReceita(base);const reg={id:x.id,numero:x.numero,ativo:x.ativo!==false,origem:(ant&&ant.origem)||(RECEITAS_PADRAO_IDS.includes(x.id)?'receita_padrao':'receita_definitiva'),origemBaldeId:(ant&&ant.origemBaldeId)||null,origemTesteId:(ant&&ant.origemTesteId)||null,receita:rec,criadoEm:(ant&&ant.criadoEm)||agora.toLocaleString('pt-BR'),criadoTs:(ant&&ant.criadoTs)||agora.getTime(),criadoPor:(ant&&ant.criadoPor)||getOp(),atualizadoEm:agora.toLocaleString('pt-BR'),atualizadoTs:agora.getTime(),atualizadoPor:getOp(),migracaoBatimentoV262:{emTs:agora.getTime(),base:clonarReceita(base)}};ESTOQUE_SYNC.localPush('receitas',reg);});
  LS.s('fdo_migr_bat_receitas_v262',true);aplicarReceitasDefinitivas();
}'''
rep(anchor,mig,'migração batimento')

# ── diferença/auditoria inclui os quatro tempos ──────────────────────
old="  const ha=a.fermentoHoras!=null?Number(a.fermentoHoras):null,hb=b.fermentoHoras!=null?Number(b.fermentoHoras):null;if(ha!==hb)out.push('Fermentação: '+(ha==null?'—':ha+' h')+' → '+(hb==null?'—':hb+' h'));\n  return out;"
new="""  const ha=a.fermentoHoras!=null?Number(a.fermentoHoras):null,hb=b.fermentoHoras!=null?Number(b.fermentoHoras):null;if(ha!==hb)out.push('Fermentação: '+(ha==null?'—':ha+' h')+' → '+(hb==null?'—':hb+' h'));
  const ba=batTemposReceita(a),bb=batTemposReceita(b);BATIMENTO_CAMPOS.forEach(c=>{if(Number(ba[c.k])!==Number(bb[c.k]))out.push(c.nome+': '+batFmtMin(ba[c.k])+' min → '+batFmtMin(bb[c.k])+' min');});
  return out;"""
rep(old,new,'auditoria batimento')

# ── receita completa mostra os tempos ────────────────────────────────
old="""  else if(r.fermentoTemp!=null&&r.fermentoHoras!=null)html+='<div class=\"rec-full-fer\"><b>Fermentação fixa</b><span>'+r.fermentoTemp+'°C · '+r.fermentoHoras+' h = '+r.fermentoFixo+' g</span></div>';
  document.getElementById('receita-full-lista').innerHTML=html;"""
new="""  else if(r.fermentoTemp!=null&&r.fermentoHoras!=null)html+='<div class=\"rec-full-fer\"><b>Fermentação fixa</b><span>'+r.fermentoTemp+'°C · '+r.fermentoHoras+' h = '+r.fermentoFixo+' g</span></div>';
  const bt=batTemposReceita(r);html+='<div class=\"rec-full-fer\"><b>Batimento · minutos em sequência</b><span>Inicial lento: '+batFmtMin(bt.t1)+' min</span><span>Depois, até colocar fermento: +'+batFmtMin(bt.t2)+' min</span><span>Depois, até colocar a massa: +'+batFmtMin(bt.t3)+' min</span><span>Depois, até conferir véu: +'+batFmtMin(bt.t4)+' min</span><span><b>Total programado: '+batFmtMin(bt.t1+bt.t2+bt.t3+bt.t4)+' min</b></span></div>';
  document.getElementById('receita-full-lista').innerHTML=html;"""
rep(old,new,'receita completa batimento')

# ── editor da receita: render e leitura ──────────────────────────────
needle="}\nfunction voltarEditorReceita(){const rid=st.receitaEditId||st.receitaVisual;"
insert="""  const bt=batTemposReceita(r);document.getElementById('receita-edit-batimento').innerHTML=`<div class=\"rec-edit-card\"><div class=\"rec-edit-title\">Batimento · minutos em sequência</div><div class=\"rec-edit-grid\"><label class=\"rec-edit-field\"><span>Batimento inicial lento</span><input class=\"inp\" id=\"receita-edit-bt1\" type=\"number\" inputmode=\"decimal\" min=\"0\" step=\"0.5\" value=\"${bt.t1}\"></label><label class=\"rec-edit-field\"><span>Depois, até colocar fermento</span><input class=\"inp\" id=\"receita-edit-bt2\" type=\"number\" inputmode=\"decimal\" min=\"0\" step=\"0.5\" value=\"${bt.t2}\"></label><label class=\"rec-edit-field\"><span>Depois, até colocar a massa</span><input class=\"inp\" id=\"receita-edit-bt3\" type=\"number\" inputmode=\"decimal\" min=\"0\" step=\"0.5\" value=\"${bt.t3}\"></label><label class=\"rec-edit-field\"><span>Depois, até ver ponto de véu</span><input class=\"inp\" id=\"receita-edit-bt4\" type=\"number\" inputmode=\"decimal\" min=\"0\" step=\"0.5\" value=\"${bt.t4}\"></label></div><div class=\"rec-edit-note\" style=\"margin-top:.45rem\">Os minutos são intervalos somados em sequência. Esta configuração será congelada em cada novo balde.</div></div>`;
}
function voltarEditorReceita(){const rid=st.receitaEditId||st.receitaVisual;"""
rep(needle,insert,'render batimento editor')

sub(r'''function receitaLerEditor\(\)\{.*?\n\}\nfunction salvarEdicaoReceita\(\)\{''','''function receitaLerEditor(){
  const r=st.receitaEditOriginal,v=receitaValores(r);for(const inp of document.querySelectorAll('#receita-edit-campos [data-rec-k]')){const n=Number(inp.value);if(!Number.isInteger(n)||n<0){alert('Confira '+(inp.previousElementSibling?inp.previousElementSibling.textContent:'o peso')+'. Use gramas inteiras e valor não negativo.');inp.focus();return null;}v[inp.dataset.recK]=n;}
  if(r&&r.fermentoFixo!=null){const f=Number(document.getElementById('receita-edit-fermento').value),t=Number(document.getElementById('receita-edit-temp').value),h=Number(document.getElementById('receita-edit-horas').value);if(!Number.isInteger(f)||f<0||!isFinite(t)||t<=0||!isFinite(h)||h<=0){alert('Confira fermento, temperatura e horas.');return null;}v.fermento=f;v.temp=t;v.horas=h;}
  const bt={};for(const c of BATIMENTO_CAMPOS){const el=document.getElementById('receita-edit-b'+c.k.slice(1)),n=Number(el&&el.value);if(!isFinite(n)||n<0||n>120){alert('Confira '+c.nome+'. Informe minutos entre 0 e 120.');if(el)el.focus();return null;}bt[c.k]=Math.round(n*10)/10;}v.batimento=bt;return v;
}
function salvarEdicaoReceita(){''','ler editor',flags=re.S)

sub(r'''function salvarEdicaoReceita\(\)\{.*?\n\}\nasync function aprovarTesteComoReceita''','''function salvarEdicaoReceita(){
  if(!OP.pode('receita_editar')||!receitaNuvemObrigatoria())return;const rid=st.receitaEditId,antes=st.receitaEditOriginal;if(!rid||!antes)return;const nome=String(document.getElementById('receita-edit-nome').value||'').trim();if(nome.length<2){alert('Informe o nome da receita.');return;}const motivo=String(document.getElementById('receita-edit-motivo').value||'').trim();if(motivo.length<8){alert('Escreva o motivo da alteração (mínimo de 8 caracteres).');document.getElementById('receita-edit-motivo').focus();return;}const v=receitaLerEditor();if(!v)return;const fixa=antes.fermentoFixo!=null,temp=fixa?v.temp:null,horas=fixa?v.horas:null,depois=receitaMontarEditada(antes,v,nome,temp,horas);depois.batimento=clonarReceita(v.batimento);const mudancas=receitaDiferencas(antes,depois);if(!mudancas.length){alert('Nenhuma alteração foi feita na receita.');return;}const resumo=mudancas.slice(0,16).join('\\n')+(mudancas.length>16?'\\n+'+(mudancas.length-16)+' alterações':'');if(!confirm('CONFIRMAR ALTERAÇÃO DE RECEITA\\n\\n'+resumo+'\\n\\nMotivo: '+motivo+'\\n\\nBaldes já existentes permanecerão com a receita anterior.'))return;
  const agora=new Date(),antReg=receitaDefRegistro(rid),reg={id:rid,numero:receitaNumero(rid,antes),ativo:true,origem:(antReg&&antReg.origem)||'receita_padrao',origemBaldeId:(antReg&&antReg.origemBaldeId)||null,origemTesteId:(antReg&&antReg.origemTesteId)||null,receita:clonarReceita(depois),criadoEm:(antReg&&antReg.criadoEm)||agora.toLocaleString('pt-BR'),criadoTs:(antReg&&antReg.criadoTs)||agora.getTime(),criadoPor:(antReg&&antReg.criadoPor)||getOp(),atualizadoEm:agora.toLocaleString('pt-BR'),atualizadoTs:agora.getTime(),atualizadoPor:getOp()};ESTOQUE_SYNC.localPush('receitas',reg);receitaRegistrarAudit('editada',rid,motivo,antes,depois,{mudancas});st.receitaEditId=null;st.receitaEditOriginal=null;alert('Receita alterada e registrada no histórico de alterações.');abrirReceitaCompleta(rid);
}
async function aprovarTesteComoReceita''','salvar edição',flags=re.S)

# ── Receita Teste: leitura/população/diferenças/salvamento ───────────
rep("function testeLerValores(){ const v={};TESTE_CAMPOS.forEach(c=>v[c.k]=testeNumero(c.id));return v; }","""function testeLerValores(){ const v={};TESTE_CAMPOS.forEach(c=>v[c.k]=testeNumero(c.id));return v; }
function testeLerBatimento(){const o={};for(const c of BATIMENTO_CAMPOS){const el=document.getElementById('teste-b'+c.k.slice(1)),n=Number(el&&el.value);if(!isFinite(n)||n<0)return null;o[c.k]=Math.round(n*10)/10;}return o;}""",'ler batimento teste')

# popula campos de batimento antes de zerar observação
sub(r'''(function abrirTesteEditor\(rid\)\{.*?if\(r\.fermentoFixo!=null\).*?else\{document\.getElementById\('teste-fermento'\).*?\}\n)(\s*document\.getElementById\('teste-obs'\))''',r'''\1  const bt=batTemposReceita(r);BATIMENTO_CAMPOS.forEach(c=>{const el=document.getElementById('teste-b'+c.k.slice(1));if(el)el.value=bt[c.k];});
\2''','popular batimento teste',flags=re.S)

sub(r'''function testeAlteracoes\(rid,v,temp,horas\)\{.*?\n\}\nfunction testeFmtAlt''','''function testeAlteracoes(rid,v,temp,horas,bat){
  const r=RECEITAS[rid]||RECEITAS.r3,base=testeValoresBase(rid),out=[];
  TESTE_CAMPOS.forEach(c=>{let de=base[c.k];if(c.k==='fermento')de=testeFermentoBase(rid,temp,horas);const para=v[c.k];if(de==null||Number(de)!==Number(para))out.push({k:c.k,nome:c.nome,de:de==null?null:Number(de),para:Number(para),unidade:'g'});});
  if(r.fermentoFixo!=null){const baseTemp=r.fermentoTemp!=null?Number(r.fermentoTemp):17;if(Number(temp)!==baseTemp)out.push({k:'temp',nome:'Temperatura',de:baseTemp,para:Number(temp),unidade:'°C'});if(r.fermentoHoras!=null&&Number(horas)!==Number(r.fermentoHoras))out.push({k:'horas',nome:'Fermentação',de:Number(r.fermentoHoras),para:Number(horas),unidade:'h'});}
  if(bat){const bb=batTemposReceita(r),bn=batTemposNormalizar(bat,bb);BATIMENTO_CAMPOS.forEach(c=>{if(Number(bb[c.k])!==Number(bn[c.k]))out.push({k:'bat_'+c.k,nome:c.nome,de:Number(bb[c.k]),para:Number(bn[c.k]),unidade:' min'});});}
  return out;
}
function testeFmtAlt''','alterações teste',flags=re.S)

sub(r'''function atualizarResumoTeste\(\)\{.*?\n\}\nfunction salvarReceitaTeste\(\)\{''','''function atualizarResumoTeste(){
  const rid=st.testeBase,r=RECEITAS[rid],box=document.getElementById('teste-resumo');if(!r||!box)return;
  const v=testeLerValores(),faltam=TESTE_CAMPOS.filter(c=>v[c.k]==null),temp=testeNumero('teste-temp'),horas=testeNumero('teste-horas'),bat=testeLerBatimento();
  if(faltam.length){box.innerHTML='<div class="teste-total">Preencha todos os pesos</div><div class="teste-diffs">Falta: '+faltam.map(x=>_escHtml(x.nome)).join(', ')+'</div>';return;}
  const total=Object.values(v).reduce((s,n)=>s+(Number(n)||0),0),alts=(temp!=null&&horas!=null&&bat)?testeAlteracoes(rid,v,temp,horas,bat):[],dif=alts.length?alts.map(testeFmtAlt).join('<br>'):'Nenhuma alteração identificada ainda.',fer=(temp==null||horas==null)?'<br><span style="color:var(--red)">Defina temperatura e horas da fermentação.</span>':'',batAviso=bat?'':'<br><span style="color:var(--red)">Confira os tempos do batimento.</span>';
  box.innerHTML='<div class="teste-total">Total do teste: '+formatPeso(total)+'</div><div class="teste-diffs"><b>Alterações em relação à '+_escHtml(r.rotulo)+':</b><br>'+dif+fer+batAviso+'</div>';
}
function salvarReceitaTeste(){''','resumo teste',flags=re.S)

sub(r'''function salvarReceitaTeste\(\)\{.*?\n\}\nfunction voltarLotesFarinha''','''function salvarReceitaTeste(){
  const rid=st.testeBase,base=RECEITAS[rid];if(!base){ir('teste-base');return;}
  const v=testeLerValores();for(const c of TESTE_CAMPOS){const n=v[c.k];if(n==null||n<0||!Number.isInteger(n)){alert('Confira '+c.nome+'. Use gramas inteiras, sem valor negativo.');document.getElementById(c.id).focus();return;}}
  const temp=testeNumero('teste-temp'),horas=testeNumero('teste-horas'),bat=testeLerBatimento();if(temp==null||temp<=0){alert('Informe a temperatura da fermentação deste teste.');document.getElementById('teste-temp').focus();return;}if(horas==null||horas<=0){alert('Informe quantas horas de fermentação serão usadas neste teste.');document.getElementById('teste-horas').focus();return;}if(!bat){alert('Confira os quatro tempos do batimento deste teste.');return;}
  const farTxt='Bagatelle '+v.bag+' g, Feuilletage '+v.feu+' g, Italiana 00 '+v.ita+' g';
  const r=montarReceita({nome:'TESTE · '+base.rotulo,rotulo:'TESTE · '+base.rotulo,farinhas:farTxt,fermentoFixo:v.fermento,fermentoHoras:horas,teste:true,baseReceita:rid,batimento:clonarReceita(bat)},v.bag,v.feu,v.ita,{agua:v.agua,acucar:v.acucar,leite:v.leite,sal:v.sal,manteiga:v.manteiga,aprov:v.aprov,semLaminar:v.semLaminar,fermento:v.fermento});
  r.passosLiquidos=r.passosLiquidos.filter(p=>!(p.nome==='Massa laminada'&&Number(p.g)===0));r.passosLiquidos.forEach((p,i)=>p.id=i+1);
  const agora=new Date(),obsTxt=String(document.getElementById('teste-obs').value||'').trim().slice(0,1200),observacoes=obsTxt?[{id:FB.novoId('obs'),em:agora.toLocaleString('pt-BR'),emTs:agora.getTime(),op:getOp(),texto:obsTxt}]:[];
  st.testeReceita=r;st.testeMeta={id:FB.novoId('teste'),baseReceita:rid,baseNome:base.nome,baseRotulo:base.rotulo,criadoEm:agora.toLocaleString('pt-BR'),criadoTs:agora.getTime(),atualizadoTs:agora.getTime(),criadoPor:getOp(),valores:clonarReceita(v),fermentacao:{temp:Number(temp),fermento_g:v.fermento,horas:Number(horas)},batimento:clonarReceita(bat),alteracoes:testeAlteracoes(rid,v,temp,horas,bat),observacoes};
  st.receita='teste';st.temp=Number(temp);st.fermento=v.fermento;st.fermentoHoras=Number(horas);st.subModulo='secos';st.farinhasLotes=null;RECEITA=r.passosSecos;
  const h=document.getElementById('hdr-rec');if(h)h.textContent='Secos · TESTE · '+base.rotulo;abrirLotesFarinha();
}
function voltarLotesFarinha''','salvar teste',flags=re.S)

# ── configuração do lembrete de estoque ──────────────────────────────
anchor='function carregarConfig(){'
stock_funcs='''const ESTOQUE_DIAS=['Domingo','Segunda-feira','Terça-feira','Quarta-feira','Quinta-feira','Sexta-feira','Sábado'];
function estoqueConfigLembrete(){const a=LS.g('fdo_estoque_configuracoes',[]),r=Array.isArray(a)?a.find(x=>x&&x.id==='lembrete_contagem'):null;return r||{id:'lembrete_contagem',operadorId:'',dia:1,ativo:false};}
function carregarConfigLembreteEstoque(){
  const sel=document.getElementById('inp-est-cont-op'),dia=document.getElementById('inp-est-cont-dia');if(!sel||!dia)return;const cfg=estoqueConfigLembrete(),ops=OP.lista().filter(o=>o&&o.ativo&&o.perms&&o.perms.estoque_contagem);sel.innerHTML='<option value="">Sem lembrete</option>'+ops.map(o=>'<option value="'+_escHtml(o.id)+'">'+_escHtml(o.nome)+'</option>').join('');sel.value=ops.some(o=>o.id===cfg.operadorId)?cfg.operadorId:'';dia.value=String(Number.isInteger(Number(cfg.dia))?Number(cfg.dia):1);
}
function salvarConfigLembreteEstoque(){
  const sel=document.getElementById('inp-est-cont-op'),d=document.getElementById('inp-est-cont-dia');if(!sel||!d)return;const id=String(sel.value||''),dia=Number(d.value),op=OP.porId(id),agora=new Date(),reg={id:'lembrete_contagem',operadorId:(op&&op.ativo&&op.perms&&op.perms.estoque_contagem)?id:'',operadorNome:(op&&op.nome)||'',dia:(dia>=0&&dia<=6)?dia:1,ativo:!!(op&&op.ativo&&op.perms&&op.perms.estoque_contagem),em:agora.toLocaleString('pt-BR'),atualizadoTs:agora.getTime(),op:getOp()};ESTOQUE_SYNC.localPush('configuracoes',reg);
}
function estoqueContagemFeitaNaData(data){return estoqueContagens().some(c=>c&&c.data===data);}
function estoqueLembreteChave(data,opId){return 'fdo_est_lembrete_'+data+'_'+String(opId||'');}
function estoqueChecarLembreteContagem(){
  const cfg=estoqueConfigLembrete(),op=OP.atual();if(!cfg.ativo||!op||op.id!==cfg.operadorId||!OP.pode('estoque_contagem'))return;const agora=new Date(),hoje=estoqueHojeISO();if(agora.getDay()!==Number(cfg.dia)||estoqueContagemFeitaNaData(hoje))return;try{if(sessionStorage.getItem(estoqueLembreteChave(hoje,op.id))==='depois')return;}catch(e){}const bg=document.getElementById('estoque-lembrete-bg'),txt=document.getElementById('estoque-lembrete-txt');if(txt)txt.textContent='Hoje é '+ESTOQUE_DIAS[agora.getDay()].toLowerCase()+', dia de fazer a contagem do estoque. Responsável: '+op.nome+'.';if(bg)bg.classList.add('on');
}
function estoqueLembreteFechar(){const bg=document.getElementById('estoque-lembrete-bg');if(bg)bg.classList.remove('on');}
function estoqueLembreteAgora(){estoqueLembreteFechar();abrirEstoqueContagem();}
function estoqueLembreteDepois(){const op=OP.atual(),hoje=estoqueHojeISO();try{if(op)sessionStorage.setItem(estoqueLembreteChave(hoje,op.id),'depois');}catch(e){}estoqueLembreteFechar();}

'''+anchor
rep(anchor,stock_funcs,'funções lembrete estoque')

# carregarConfig: não lê mais inputs globais de batimento
old="""  document.getElementById('inp-bt1').value=getBatT1();
  document.getElementById('inp-bt2').value=getBatT2();
  document.getElementById('inp-bt3').value=getBatT3();
  document.getElementById('inp-bt4').value=getBatT4();
  document.getElementById('inp-bdiv').value=getBatDiv();"""
new="""  carregarConfigLembreteEstoque();
  document.getElementById('inp-bdiv').value=getBatDiv();"""
rep(old,new,'carregar config')

old="""  // Tempos do batimento (minutos) e divisor de partes
  const numPos=(id,def)=>{ const v=parseInt(document.getElementById(id).value,10); return (isFinite(v)&&v>=0)?v:def; };
  LS.s('fdo_bat_t1',numPos('inp-bt1',4));
  LS.s('fdo_bat_t2',numPos('inp-bt2',6));
  LS.s('fdo_bat_t3',numPos('inp-bt3',3));
  LS.s('fdo_bat_t4',numPos('inp-bt4',2));
  const dv=parseInt(document.getElementById('inp-bdiv').value,10); LS.s('fdo_bat_div',(isFinite(dv)&&dv>=1)?dv:4);"""
new="""  // v26.2: responsável/dia da conferência; tempos do batimento ficam nas receitas.
  salvarConfigLembreteEstoque();
  const dv=parseInt(document.getElementById('inp-bdiv').value,10); LS.s('fdo_bat_div',(isFinite(dv)&&dv>=1)?dv:4);"""
rep(old,new,'salvar config')

# start: confere lembrete após aplicar permissões
rep("  if(id==='start' && typeof aplicarPermsStart==='function') aplicarPermsStart();","  if(id==='start' && typeof aplicarPermsStart==='function'){ aplicarPermsStart(); setTimeout(()=>{try{estoqueChecarLembreteContagem();}catch(e){}},180); }",'hook lembrete start')

# ESTOQUE_SYNC ganha configuração sincronizada
rep("    contagens:{local:'fdo_estoque_contagens',path:'fdo_v25/estoque/contagens'},","    contagens:{local:'fdo_estoque_contagens',path:'fdo_v25/estoque/contagens'},\n    configuracoes:{local:'fdo_estoque_configuracoes',path:'fdo_v25/estoque/configuracoes'},",'sync config estoque')
rep("    this.save(nome,arr);this.ready[nome]=true;FB.repaint();this.flush();\n    if(nome==='movimentos')estoqueReconciliarSaidasLotes();","""    this.save(nome,arr);this.ready[nome]=true;FB.repaint();this.flush();
    if(nome==='movimentos')estoqueReconciliarSaidasLotes();
    if(nome==='receitas')setTimeout(()=>{try{migrarBatimentoReceitasV262();}catch(e){console.warn('[RECEITAS] migração batimento',e)}},0);
    if(nome==='configuracoes')setTimeout(()=>{try{const vis=document.querySelector('.scr:not(.off)');if(vis&&vis.id==='s-start')estoqueChecarLembreteContagem();}catch(e){}},0);""",'apply sync v262')

# dia da conferência segue configuração, não segunda fixa
sub(r'''function estoqueAtualizarDiaContagem\(\)\{.*?\n\}\nfunction salvarEstoqueContagem\(\)\{''','''function estoqueAtualizarDiaContagem(){
  const v=document.getElementById('estoque-cont-data').value,el=document.getElementById('estoque-cont-dia');if(!el)return;if(!v){el.textContent='';return;}const d=new Date(v+'T12:00:00'),cfg=estoqueConfigLembrete(),dia=cfg.ativo?Number(cfg.dia):1,ok=d.getDay()===dia;el.textContent=ok?(ESTOQUE_DIAS[dia]+' · conferência programada'):('Atenção: a data escolhida não é '+ESTOQUE_DIAS[dia].toLowerCase()+'.');el.style.color=ok?'var(--grn)':'var(--gold)';
}
function salvarEstoqueContagem(){''','dia configurável contagem',flags=re.S)
rep("  const d=new Date(data+'T12:00:00');if(d.getDay()!==1&&!confirm('A data escolhida não é segunda-feira. Deseja registrar mesmo assim?'))return;","  const d=new Date(data+'T12:00:00'),cfg=estoqueConfigLembrete(),dia=cfg.ativo?Number(cfg.dia):1;if(d.getDay()!==dia&&!confirm('A data escolhida não é '+ESTOQUE_DIAS[dia].toLowerCase()+'. Deseja registrar mesmo assim?'))return;",'validação dia contagem')

# ── cronômetro usa configuração congelada do balde/receita ──────────
rep("let batCronInt=null, batBatStartMs=0, batAvisados=[], batTempoSeg=0, batAudioCtx=null;","let batCronInt=null, batBatStartMs=0, batAvisados=[], batTempoSeg=0, batAudioCtx=null, batTemposRun=null;",'estado batimento')
rep("  st.batLote=id; st.batStart=Date.now(); st.batRodando=false; batLimparRun();","  st.batLote=id; st.batStart=Date.now(); st.batRodando=false; batLimparRun(); batTemposRun=batTemposDoLote(lote);",'congelar tempos ao abrir batimento')
rep("  document.getElementById('bat-lote-meta').textContent=[lote.criado||'', p.op?('op. '+p.op):'', p.total_g?('total '+formatPeso(p.total_g)):''].filter(Boolean).join(' · ');","  document.getElementById('bat-lote-meta').textContent=[lote.criado||'', p.op?('op. '+p.op):'', p.total_g?('total '+formatPeso(p.total_g)):'','batimento '+batTemposTexto(batTemposRun)].filter(Boolean).join(' · ');",'meta batimento novo')
rep("  LS.s('fdo_bat_run',{ loteId:st.batLote, startMs:batBatStartMs, fase:fase, temp:st.batTemp, tempoSeg:batTempoSeg, avisados:batAvisados.slice(), savedAt:Date.now() });","  LS.s('fdo_bat_run',{ loteId:st.batLote, startMs:batBatStartMs, fase:fase, temp:st.batTemp, tempoSeg:batTempoSeg, avisados:batAvisados.slice(), tempos:clonarReceita(batTemposRun||batTemposBaseLegado()), savedAt:Date.now() });",'persistir tempos run')
sub(r'''function batAgenda\(\)\{\n  const t1=getBatT1\(\), t2=getBatT2\(\), t3=getBatT3\(\), t4=getBatT4\(\);''',"""function batAgenda(){
  const bt=batTemposNormalizar(batTemposRun,batTemposBaseLegado()),t1=bt.t1,t2=bt.t2,t3=bt.t3,t4=bt.t4;""",'agenda por receita')
rep("  st.batLote=run.loteId; st.batStart=run.startMs||Date.now(); st.batTemp=(run.temp!=null?run.temp:20);","  st.batLote=run.loteId; st.batStart=run.startMs||Date.now(); st.batTemp=(run.temp!=null?run.temp:20); batTemposRun=batTemposNormalizar(run.tempos||batTemposDoLote(lote),batTemposBaseLegado());",'restaurar tempos run')
rep("  document.getElementById('bat-lote-meta').textContent=[lote.criado||'', p.op?('op. '+p.op):''].filter(Boolean).join(' · ');","  document.getElementById('bat-lote-meta').textContent=[lote.criado||'', p.op?('op. '+p.op):'','batimento '+batTemposTexto(batTemposRun)].filter(Boolean).join(' · ');",'meta batimento restaurado')
rep("    tempoSeg:batTempoSeg, tempoTxt:fmtMMSS(batTempoSeg),","    tempoSeg:batTempoSeg, tempoTxt:fmtMMSS(batTempoSeg),\n    temposProgramados:clonarReceita(batTemposRun||batTemposDoLote(lote)),",'histórico tempos batimento')
rep("  batPararMicPeso(); st.batRodando=false; batLimparRun(); liberarWakeLock();","  batPararMicPeso(); st.batRodando=false; batLimparRun(); batTemposRun=null; liberarWakeLock();",'limpar tempos sair')

# ── boot: congela baldes antigos pendentes ───────────────────────────
rep("  migrarLotesAntigos(); congelarSnapshotsReceitasLegadas(); aplicarReceitasDefinitivas(); garantirPermissoesV260();","  migrarLotesAntigos(); congelarSnapshotsReceitasLegadas(); aplicarReceitasDefinitivas(); congelarBatimentoBaldesPendentesV262(); garantirPermissoesV260();",'boot v262')

# ── backup ───────────────────────────────────────────────────────────
rep("'fdo_estoque_contagens','fdo_receitas_observacoes'","'fdo_estoque_contagens','fdo_estoque_configuracoes','fdo_receitas_observacoes'",'backup config estoque')
rep("versao:'26.1'","versao:'26.2'",'versão backup')

# Salva index
P.write_text(html,encoding='utf-8')

# Service Worker
swp=ROOT/'sw.js';sw=swp.read_text(encoding='utf-8')
if "const CACHE='fdo-v26-1';" not in sw: raise SystemExit('cache v26.1 não encontrado')
sw=sw.replace("const CACHE='fdo-v26-1';","const CACHE='fdo-v26-2';",1);swp.write_text(sw,encoding='utf-8')

# Validador principal: v26.2 + preservação da v26.1
vp=ROOT/'tools/validate_fdo.py';v=vp.read_text(encoding='utf-8')
v=v.replace("# v26.1 — receitas definitivas versionadas, auditáveis e arquiváveis\nfor marker in (\n    'atualização v26.1'", """# v26.2 — lembrete de estoque + batimento por receita
for marker in (
    'atualização v26.2','id=\"inp-est-cont-op\"','id=\"inp-est-cont-dia\"','id=\"estoque-lembrete-bg\"',
    'function estoqueChecarLembreteContagem()','fdo_estoque_configuracoes','fdo_v25/estoque/configuracoes',
    'id=\"receita-edit-batimento\"','function batTemposReceita(r)','function batTemposDoLote(l)',
    'function congelarBatimentoBaldesPendentesV262()','function migrarBatimentoReceitasV262()',
    'temposProgramados:clonarReceita','versao:\'26.2\''
):
    if marker not in html: fail('v26.2 sem marcador: '+marker)
if 'id=\"inp-bt1\"' in html or 'id=\"inp-bt2\"' in html or 'id=\"inp-bt3\"' in html or 'id=\"inp-bt4\"' in html:
    fail('Tempos globais do batimento ainda aparecem nas Configurações')

# v26.1 — receitas definitivas versionadas, auditáveis e arquiváveis permanecem
for marker in (
    'NOVIDADES v26.1'""",1)
v=v.replace("print('VALIDAÇÃO FDO v26.1 OK')","print('VALIDAÇÃO FDO v26.2 OK')",1)
vp.write_text(v,encoding='utf-8')

# Teste v26.1 deve verificar que a funcionalidade anterior permanece, não o cabeçalho atual.
tp=ROOT/'tools/test_receitas_v26_1.js';t=tp.read_text(encoding='utf-8')
t=t.replace("has('atualização v26.1','cabeçalho v26.1');","has('NOVIDADES v26.1','histórico funcional v26.1 preservado');",1)
tp.write_text(t,encoding='utf-8')

# Novo teste v26.2
test=r'''const fs=require('fs');
const assert=require('assert');
const vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
function has(x,msg){assert(html.includes(x),msg)}
has('atualização v26.2','cabeçalho v26.2');
has('id="inp-est-cont-op"','responsável da contagem configurável');
has('id="inp-est-cont-dia"','dia da contagem configurável');
has('id="estoque-lembrete-bg"','pop-up da contagem');
has("configuracoes:{local:'fdo_estoque_configuracoes',path:'fdo_v25/estoque/configuracoes'}",'configuração sincronizada');
has('function estoqueChecarLembreteContagem()','checagem do lembrete');
has('id="receita-edit-batimento"','batimento no editor da receita');
has('id="teste-bt1"','batimento na Receita Teste');
has('function migrarBatimentoReceitasV262()','migração dos tempos antigos');
has('function congelarBatimentoBaldesPendentesV262()','congelamento dos baldes pendentes');
has('temposProgramados:clonarReceita','histórico guarda tempos programados');
has('tempos:clonarReceita(batTemposRun','retomada guarda tempos');
assert(!html.includes('id="inp-bt1"'),'batimento não pode continuar como configuração global visível');
assert(!html.includes('id="inp-bt2"'),'bt2 global removido');
assert(!html.includes('id="inp-bt3"'),'bt3 global removido');
assert(!html.includes('id="inp-bt4"'),'bt4 global removido');

const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function extractFunction(src,name){
  const start=src.indexOf('function '+name+'(');assert(start>=0,'função ausente: '+name);
  const brace=src.indexOf('{',start);let depth=0,quote='',esc=false;
  for(let i=brace;i<src.length;i++){
    const c=src[i];if(quote){if(esc)esc=false;else if(c==='\\')esc=true;else if(c===quote)quote='';continue;}
    if(c==='"'||c==="'"||c==='`'){quote=c;continue;}if(c==='{')depth++;else if(c==='}'&&--depth===0)return src.slice(start,i+1);
  }throw new Error('fim não encontrado '+name);
}
const decl=scripts.match(/const BATIMENTO_CAMPOS=\[[\s\S]*?\];/)[0];
const funcs=['batTemposNormalizar','batTemposBaseLegado','batAgenda'].map(n=>extractFunction(scripts,n)).join('\n');
const sandbox={result:null,batTemposRun:{t1:4,t2:5,t3:2,t4:1},getBatT1:()=>4,getBatT2:()=>6,getBatT3:()=>3,getBatT4:()=>2};
vm.createContext(sandbox);vm.runInContext(decl+'\n'+funcs+'\nresult=batAgenda().map(x=>x.min);',sandbox);
assert.deepStrictEqual(Array.from(sandbox.result),[4,9,11,12],'agenda precisa somar os quatro intervalos da receita');
console.log('TESTE v26.2 OK · lembrete configurável + batimento por receita + snapshots');
'''
(ROOT/'tools/test_v26_2.js').write_text(test,encoding='utf-8')

print('Patch v26.2 aplicado')
