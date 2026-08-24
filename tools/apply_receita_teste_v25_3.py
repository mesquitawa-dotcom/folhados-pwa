from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'index.html'
SW=ROOT/'sw.js'
VALID=ROOT/'tools'/'validate_fdo.py'
SYNC_TEST=ROOT/'tools'/'test_sync_v25_1.js'

html=INDEX.read_text(encoding='utf-8')
sw=SW.read_text(encoding='utf-8')
valid=VALID.read_text(encoding='utf-8')
sync_test=SYNC_TEST.read_text(encoding='utf-8')


def rep(txt, old, new, label):
    n=txt.count(old)
    if n!=1:
        raise SystemExit(f'{label}: esperado 1 marcador, encontrado {n}')
    return txt.replace(old,new,1)

# ---------------------------------------------------------------------------
# index.html — versão/cabeçalho
# ---------------------------------------------------------------------------
html=rep(html,
"""       FOLHADOS D'OURO — atualização v25.2
       NOVIDADES v25.2:
""",
"""       FOLHADOS D'OURO — atualização v25.3
       NOVIDADES v25.3:
       • Receita Teste: parte de qualquer R1–R5 e permite alterar os pesos sem modificar as receitas padrão.
       • Cada balde de teste guarda a fotografia completa da receita executada, diferenças e observações.
       • Balde, etiquetas, histórico e laminação preservam a identificação TESTE; observações podem ser acrescentadas depois.
       NOVIDADES v25.2:
""",
'cabecalho v25.3')

# ---------------------------------------------------------------------------
# CSS da Receita Teste
# ---------------------------------------------------------------------------
css_anchor="""    #s-receitas .modulo-nome{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    #s-receitas .modulo-desc{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:.68rem}
    /* ════ v24.10 — LOTES DAS FARINHAS ════ */
"""
css_new="""    #s-receitas .modulo-nome{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    #s-receitas .modulo-desc{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:.68rem}
    /* ════ v25.3 — RECEITA TESTE ════ */
    #s-teste-base .modulo-nome{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
    #s-teste-edit{padding:0}
    .badge-teste{background:rgba(248,113,113,.12);color:#f5b8a8;border:1px solid #5a1a0e}
    .teste-body{flex:1;overflow-y:auto;padding:.2rem 1rem 1rem;display:flex;flex-direction:column;gap:.7rem}
    .teste-card{background:var(--bg3);border:1px solid var(--brd);border-radius:.55rem;padding:.85rem}
    .teste-card-title{font-size:.8rem;color:var(--gold);font-weight:bold;letter-spacing:.08rem;text-transform:uppercase;margin-bottom:.55rem}
    .teste-grid{display:grid;grid-template-columns:1fr 1fr;gap:.55rem}
    .teste-field{display:flex;flex-direction:column;gap:.22rem;min-width:0}
    .teste-field.full{grid-column:1/-1}
    .teste-label{font-size:.66rem;color:var(--mut);line-height:1.25}
    .teste-inp{background:var(--bg2);border:.1rem solid var(--brd);color:var(--text);font-family:Georgia,serif;font-size:1rem;padding:.7rem .65rem;border-radius:.4rem;width:100%;outline:none;min-height:2.7rem}
    .teste-inp:focus{border-color:var(--gold)}
    textarea.teste-inp{min-height:5rem;resize:vertical;font-size:.85rem;line-height:1.4}
    .teste-note{font-size:.68rem;color:var(--mut);line-height:1.45}
    .teste-resumo{background:rgba(201,151,58,.08);border:1px solid rgba(201,151,58,.28);border-left:.25rem solid var(--gold);border-radius:.45rem;padding:.75rem .8rem}
    .teste-total{font-size:1.05rem;color:var(--gl);font-weight:bold;margin-bottom:.4rem}
    .teste-diffs{font-size:.7rem;color:var(--text);line-height:1.5}
    .teste-diffs b{color:var(--gold)}
    .teste-hist{margin-top:.6rem;padding:.65rem .7rem;background:rgba(248,113,113,.06);border:1px solid #4a1a12;border-left:.22rem solid var(--red);border-radius:.35rem}
    .teste-hist-title{font-size:.72rem;font-weight:bold;color:#f5b8a8;letter-spacing:.08rem;margin-bottom:.35rem}
    .teste-hist-row{font-size:.68rem;color:var(--text);line-height:1.45;margin-top:.3rem}
    .teste-hist-row b{color:var(--gold)}
    .teste-obs-btn{margin-top:.55rem;background:transparent;border:1px solid #5a3008;color:var(--gold);font-family:Georgia,serif;font-size:.65rem;font-weight:bold;padding:.5rem .65rem;border-radius:.3rem;cursor:pointer;min-height:2.2rem}
    /* ════ v24.10 — LOTES DAS FARINHAS ════ */
"""
html=rep(html,css_anchor,css_new,'css receita teste')

# ---------------------------------------------------------------------------
# Card Receita Teste na lista R1-R5
# ---------------------------------------------------------------------------
r5_block="""    <div class="modulo ativo" onclick="iniciarReceita('r5')">
      <div class="modulo-icon">5️⃣</div>
      <div class="modulo-info">
        <div class="modulo-nome">1 kg sem laminar</div>
        <div class="modulo-desc">Laminada 2,5 kg + sem laminar 1 kg · Bagatelle 3370 g · Italiana 4118 g · fermento 64 g / 17 h</div>
      </div>
      <div class="modulo-badge badge-ativo">Ativo</div>
    </div>
"""
r5_plus=r5_block+"""    <div class="modulo ativo" onclick="abrirTesteBase()">
      <div class="modulo-icon">🧪</div>
      <div class="modulo-info">
        <div class="modulo-nome">Receita Teste</div>
        <div class="modulo-desc">Copie uma R1–R5, altere somente o necessário e guarde exatamente o que foi feito</div>
      </div>
      <div class="modulo-badge badge-teste">Teste</div>
    </div>
"""
html=rep(html,r5_block,r5_plus,'card receita teste')

# ---------------------------------------------------------------------------
# Telas: escolha da base + editor
# ---------------------------------------------------------------------------
screens="""<!-- ═══ RECEITA TESTE — base + edição do lote experimental (v25.3) ═══ -->
<div id="s-teste-base" class="scr off">
  <div class="start-top">
    <div class="start-icon">🧪</div>
    <div class="start-brand">Folhados d'Ouro</div>
    <div class="start-title">Receita Teste</div>
    <div class="start-sub">Qual receita será a base?</div>
  </div>
  <div class="modulos-label">A receita original não será alterada</div>
  <div class="modulos">
    <div class="modulo ativo" onclick="abrirTesteEditor('r1')"><div class="modulo-icon">1️⃣</div><div class="modulo-info"><div class="modulo-nome">Receita 1</div><div class="modulo-desc">Usar R1 como ponto de partida</div></div></div>
    <div class="modulo ativo" onclick="abrirTesteEditor('r2')"><div class="modulo-icon">2️⃣</div><div class="modulo-info"><div class="modulo-nome">Receita 2 - MASSA 3 KG</div><div class="modulo-desc">Usar R2 como ponto de partida</div></div></div>
    <div class="modulo ativo" onclick="abrirTesteEditor('r3')"><div class="modulo-icon">3️⃣</div><div class="modulo-info"><div class="modulo-nome">Receita 3 - PADRÃO</div><div class="modulo-desc">Usar R3 como ponto de partida</div></div><div class="modulo-badge badge-ativo">Padrão</div></div>
    <div class="modulo ativo" onclick="abrirTesteEditor('r4')"><div class="modulo-icon">4️⃣</div><div class="modulo-info"><div class="modulo-nome">Massa 3 kg sem manteiga</div><div class="modulo-desc">Usar R4 como ponto de partida</div></div></div>
    <div class="modulo ativo" onclick="abrirTesteEditor('r5')"><div class="modulo-icon">5️⃣</div><div class="modulo-info"><div class="modulo-nome">1 kg sem laminar</div><div class="modulo-desc">Usar R5 como ponto de partida</div></div></div>
  </div>
  <div class="start-footer"><button class="link-btn" onclick="ir('receitas')">← Voltar</button></div>
</div>
<div id="s-teste-edit" class="scr off">
  <div class="start-top" style="padding-bottom:.55rem">
    <div class="start-brand">Folhados d'Ouro · 🧪 Teste</div>
    <div class="start-title" id="teste-edit-title">Receita Teste</div>
    <div class="start-sub">Altere somente o que será diferente neste lote</div>
  </div>
  <div class="teste-body">
    <div class="teste-card">
      <div class="teste-card-title">Farinhas · gramas</div>
      <div class="teste-grid">
        <label class="teste-field"><span class="teste-label">Bagatelle</span><input id="teste-bag" class="teste-inp" type="number" inputmode="numeric" min="0" step="1" oninput="atualizarResumoTeste()"></label>
        <label class="teste-field"><span class="teste-label">Italiana 00</span><input id="teste-ita" class="teste-inp" type="number" inputmode="numeric" min="0" step="1" oninput="atualizarResumoTeste()"></label>
        <label class="teste-field full"><span class="teste-label">Feuilletage</span><input id="teste-feu" class="teste-inp" type="number" inputmode="numeric" min="0" step="1" oninput="atualizarResumoTeste()"></label>
      </div>
    </div>
    <div class="teste-card">
      <div class="teste-card-title">Secos · gramas</div>
      <div class="teste-grid">
        <label class="teste-field"><span class="teste-label">Fermento seco</span><input id="teste-fermento" class="teste-inp" type="number" inputmode="numeric" min="0" step="1" oninput="testeFermentoMudou()"></label>
        <label class="teste-field"><span class="teste-label">Açúcar</span><input id="teste-acucar" class="teste-inp" type="number" inputmode="numeric" min="0" step="1" oninput="atualizarResumoTeste()"></label>
        <label class="teste-field"><span class="teste-label">Sal refinado</span><input id="teste-sal" class="teste-inp" type="number" inputmode="numeric" min="0" step="1" oninput="atualizarResumoTeste()"></label>
        <label class="teste-field"><span class="teste-label">Manteiga</span><input id="teste-manteiga" class="teste-inp" type="number" inputmode="numeric" min="0" step="1" oninput="atualizarResumoTeste()"></label>
      </div>
    </div>
    <div class="teste-card">
      <div class="teste-card-title">Líquidos e massas · gramas</div>
      <div class="teste-grid">
        <label class="teste-field"><span class="teste-label">Água / gelo</span><input id="teste-agua" class="teste-inp" type="number" inputmode="numeric" min="0" step="1" oninput="atualizarResumoTeste()"></label>
        <label class="teste-field"><span class="teste-label">Leite em pó</span><input id="teste-leite" class="teste-inp" type="number" inputmode="numeric" min="0" step="1" oninput="atualizarResumoTeste()"></label>
        <label class="teste-field"><span class="teste-label">Aproveita / massa laminada</span><input id="teste-aprov" class="teste-inp" type="number" inputmode="numeric" min="0" step="1" oninput="atualizarResumoTeste()"></label>
        <label class="teste-field"><span class="teste-label">Massa sem laminar</span><input id="teste-sem-laminar" class="teste-inp" type="number" inputmode="numeric" min="0" step="1" oninput="atualizarResumoTeste()"></label>
      </div>
    </div>
    <div class="teste-card">
      <div class="teste-card-title">Fermentação do teste</div>
      <div class="teste-grid">
        <label class="teste-field"><span class="teste-label">Temperatura °C</span><input id="teste-temp" class="teste-inp" type="number" inputmode="decimal" step="0.1" oninput="atualizarResumoTeste()" placeholder="ex.: 20"></label>
        <label class="teste-field"><span class="teste-label">Horas</span><input id="teste-horas" class="teste-inp" type="number" inputmode="decimal" min="0.1" step="0.1" oninput="atualizarResumoTeste()" placeholder="ex.: 14"></label>
      </div>
      <div class="teste-note" style="margin-top:.5rem">Ao informar um fermento que já existe nas opções normais, temperatura e horas são preenchidas automaticamente. Confira visualmente antes de iniciar.</div>
    </div>
    <div class="teste-card">
      <div class="teste-card-title">Observações do teste</div>
      <textarea id="teste-obs" class="teste-inp" maxlength="1200" placeholder="Ex.: sem massa de aproveitamento; ajuste de hidratação; objetivo deste teste..."></textarea>
      <div class="teste-note" style="margin-top:.45rem">Depois do resultado final, novas observações poderão ser acrescentadas pelo Histórico. Os pesos executados não poderão ser alterados.</div>
    </div>
    <div class="teste-resumo" id="teste-resumo"><div class="teste-total">Preencha o teste</div></div>
    <div class="teste-note" style="text-align:center">As receitas R1–R5 permanecem intactas. O sistema salvará uma fotografia independente deste teste.</div>
    <button class="btn-main" onclick="salvarReceitaTeste()">✓ Confirmar e iniciar teste</button>
  </div>
  <div class="start-footer"><button class="link-btn" onclick="ir('teste-base')">← Trocar base</button></div>
</div>
"""
html=rep(html,
"""<!-- ═══ LOTES DAS FARINHAS — confirmação rápida antes dos secos (v24.10) ═══ -->
""",
screens+"""<!-- ═══ LOTES DAS FARINHAS — confirmação rápida antes dos secos (v24.10) ═══ -->
""",
'telas receita teste')

html=rep(html,
"""    <button class="link-btn" onclick="ir('receitas')">← Trocar receita</button>
""",
"""    <button class="link-btn" onclick="voltarLotesFarinha()">← Trocar receita</button>
""",
'voltar lotes farinha')

# ---------------------------------------------------------------------------
# Estado e helpers de receita ativa/snapshot
# ---------------------------------------------------------------------------
html=rep(html,
"""  fermLote:null,fermStart:0,fermMin:24,fermMax:28,lamSel:{},farinhasLotes:null,
  loginOpId:null,loginFiltro:'',criandoLote:false,criandoLam:false};
""",
"""  fermLote:null,fermStart:0,fermMin:24,fermMax:28,lamSel:{},farinhasLotes:null,
  testeBase:null,testeReceita:null,testeMeta:null,
  loginOpId:null,loginFiltro:'',criandoLote:false,criandoLam:false};
""",
'estado teste')

html=rep(html,
"""// Receita ativa (apontador para o array de passos da FASE atual: secos OU líquidos).
let RECEITA = RECEITAS.r1.passosSecos;
""",
"""// Receita ativa (apontador para o array de passos da FASE atual: secos OU líquidos).
let RECEITA = RECEITAS.r1.passosSecos;
function clonarReceita(v){ return v==null?v:JSON.parse(JSON.stringify(v)); }
function receitaAtualObj(){ return (st.receita==='teste'&&st.testeReceita)?st.testeReceita:(RECEITAS[st.receita]||RECEITAS.r1); }
function receitaDoLote(lote){
  if(lote&&lote.receitaSnapshot&&Array.isArray(lote.receitaSnapshot.passos)) return lote.receitaSnapshot;
  return RECEITAS[lote&&lote.receita]||null;
}
""",
'helpers receita snapshot')

html=rep(html,
"""function montarSystem(){
  const r=RECEITAS[st.receita]||RECEITAS.r1;
""",
"""function montarSystem(){
  const r=receitaAtualObj();
""",
'montarSystem receita ativa')

# ---------------------------------------------------------------------------
# Backup v25.3
# ---------------------------------------------------------------------------
html=rep(html,"versao:'25.2'","versao:'25.3'",'versao backup')

# ---------------------------------------------------------------------------
# Criação do balde: snapshot + metadados do teste
# ---------------------------------------------------------------------------
html=rep(html,
"""function totalReceitaFull(rid){ const r=RECEITAS[rid]||RECEITAS[st.receita]||RECEITAS.r1; return (r.passos||[]).reduce((s,p)=>s+(p.g||0),0); }
// PORCIONAMENTO DE SECOS concluído → cria um novo LOTE numerado (com etiqueta)
async function criarLoteSecos(){
  const r=RECEITAS[st.receita]||RECEITAS.r1;
""",
"""function totalReceitaFull(rid){ const r=(rid==='teste'&&st.testeReceita)?st.testeReceita:(RECEITAS[rid]||receitaAtualObj()); return (r.passos||[]).reduce((s,p)=>s+(p.g||0),0); }
// PORCIONAMENTO DE SECOS concluído → cria um novo LOTE numerado (com etiqueta)
async function criarLoteSecos(){
  const r=receitaAtualObj();
  const ehTeste=st.receita==='teste'&&!!st.testeReceita&&!!st.testeMeta;
""",
'criar lote receita ativa')

html=rep(html,
"""  };
  const todos=LS.g('fdo_lotes',[]);todos.unshift(lote);LS.s('fdo_lotes',todos);return lote;
}
function loteAtivo(l){
""",
"""  };
  if(ehTeste){ lote.receitaSnapshot=clonarReceita(st.testeReceita); lote.teste=clonarReceita(st.testeMeta); }
  const todos=LS.g('fdo_lotes',[]);todos.unshift(lote);LS.s('fdo_lotes',todos);return lote;
}
function loteAtivo(l){
""",
'snapshot no lote')

# ---------------------------------------------------------------------------
# Batimento e etiqueta leem snapshot quando houver
# ---------------------------------------------------------------------------
html=rep(html,"const r=RECEITAS[lote.receita];\n  if(r){ const f=(r.passos||[]).find(p=>p.cat==='FERMENTO');", "const r=receitaDoLote(lote);\n  if(r){ const f=(r.passos||[]).find(p=>p.cat==='FERMENTO');",'fermento snapshot')
html=rep(html,"const r=RECEITAS[lote.receita]; if(!r) return {sal:null,manteiga:null};", "const r=receitaDoLote(lote); if(!r) return {sal:null,manteiga:null};",'sal manteiga snapshot')
html=rep(html,"const r=RECEITAS[lote.receita]; if(!r) return null;\n  const ferm=loteFermentoG(lote);", "const r=receitaDoLote(lote); if(!r) return null;\n  const ferm=loteFermentoG(lote);",'balde1 snapshot')
html=rep(html,"const r=RECEITAS[lote.receita]; if(!r) return null;\n  let s=0; r.passos.forEach(p=>{ if((p.grupo||'').startsWith('BALDE 2'))", "const r=receitaDoLote(lote); if(!r) return null;\n  let s=0; r.passos.forEach(p=>{ if((p.grupo||'').startsWith('BALDE 2'))",'balde2 snapshot')
html=rep(html,"function loteLiquidos(lote){\n  const r=RECEITAS[lote.receita]; if(!r) return null;", "function loteLiquidos(lote){\n  const r=receitaDoLote(lote); if(!r) return null;",'liquidos etiqueta snapshot')
html=rep(html,"function loteMassas(lote){\n  const r=RECEITAS[lote.receita]; if(!r) return null;", "function loteMassas(lote){\n  const r=receitaDoLote(lote); if(!r) return null;",'massas etiqueta snapshot')

# ---------------------------------------------------------------------------
# Etiqueta: TESTE bem visível + diferenças compactas
# ---------------------------------------------------------------------------
html=rep(html,
"""function desenharEtiqueta(lote){
""",
"""function testeTokenEtiqueta(a){
  const ab={bag:'Bag',feu:'Feu',ita:'Ita',fermento:'Ferm',acucar:'Aç',sal:'Sal',manteiga:'Mant',agua:'Água',leite:'Leite',aprov:'Aprov',semLaminar:'SemLam',temp:'Temp',horas:'Horas'};
  const nome=ab[a&&a.k]||(a&&a.nome)||'Alt'; const v=a&&a.para;
  if(a&&a.unidade==='g') return nome+' '+v+'g';
  if(a&&a.unidade==='°C') return nome+' '+v+'°C';
  if(a&&a.unidade==='h') return nome+' '+v+'h';
  return nome+' '+v;
}
function testeLinhasEtiqueta(lote,pi){
  const a=(lote&&lote.teste&&Array.isArray(lote.teste.alteracoes))?lote.teste.alteracoes:[];
  const toks=a.map(testeTokenEtiqueta), linhas=[];
  const lim=Math.min(toks.length,10);
  for(let i=0;i<lim;i+=2) linhas.push(toks.slice(i,i+2).join(' · '));
  if(toks.length>10) linhas.push('+'+(toks.length-10)+' alterações no histórico');
  if(pi&&pi.temp!=null&&pi.fermento_horas!=null) linhas.push(pi.temp+'ºC · '+pi.fermento_horas+'h · fermento '+pi.fermento_g+'g');
  return linhas;
}
function desenharEtiqueta(lote){
""",
'helpers etiqueta teste')

html=rep(html,
"""  x.textAlign='center';
  x.font='bold 56px Arial, sans-serif'; x.fillText('BALDE #'+d.num, ETQ_W/2, 66);
  x.font='24px Arial, sans-serif';
  let rec=d.receita; if(rec.length>34) rec=rec.slice(0,34);
""",
"""  x.textAlign='center';
  x.font=lote.teste?'bold 40px Arial, sans-serif':'bold 56px Arial, sans-serif'; x.fillText((lote.teste?'TESTE · ':'')+'BALDE #'+d.num, ETQ_W/2, 66);
  x.font='24px Arial, sans-serif';
  let rec=lote.teste?('Base '+(lote.teste.baseRotulo||lote.teste.baseReceita||d.receita)):d.receita; if(rec.length>34) rec=rec.slice(0,34);
""",
'etiqueta titulo teste')

html=rep(html,
"""  // valores: líquidos (balde 2) + massas (laminada / sem laminar)
  const linhas=[];
  if(liq){
    if(liq.agua!=null)  linhas.push('Água/gelo:  '+formatPeso(liq.agua));
    if(liq.leite!=null) linhas.push('Leite em pó:  '+formatPeso(liq.leite));
  }
  if(mas){
    if(mas.laminada!=null)                        linhas.push('Massa laminada:  '+formatPeso(mas.laminada));
    if(mas.semLaminar!=null && mas.semLaminar>0)  linhas.push('Massa sem laminar:  '+formatPeso(mas.semLaminar));
  }
  if(pi.temp!=null && pi.fermento_horas!=null) linhas.push(pi.temp+'ºC  '+pi.fermento_horas+' horas fermentação');
  if(linhas.length){
    x.textAlign='left'; x.font='24px Arial, sans-serif';
    let yy=188;
    linhas.forEach(t=>{ x.fillText(t, 40, yy); yy+=33; });
""",
"""  // valores normais; no TESTE, a etiqueta prioriza exatamente o que mudou.
  const linhas=[];
  if(lote.teste){
    linhas.push(...testeLinhasEtiqueta(lote,pi));
  }else{
    if(liq){
      if(liq.agua!=null)  linhas.push('Água/gelo:  '+formatPeso(liq.agua));
      if(liq.leite!=null) linhas.push('Leite em pó:  '+formatPeso(liq.leite));
    }
    if(mas){
      if(mas.laminada!=null)                        linhas.push('Massa laminada:  '+formatPeso(mas.laminada));
      if(mas.semLaminar!=null && mas.semLaminar>0)  linhas.push('Massa sem laminar:  '+formatPeso(mas.semLaminar));
    }
    if(pi.temp!=null && pi.fermento_horas!=null) linhas.push(pi.temp+'ºC  '+pi.fermento_horas+' horas fermentação');
  }
  if(linhas.length){
    x.textAlign='left'; x.font=lote.teste?'19px Arial, sans-serif':'24px Arial, sans-serif';
    let yy=188; const passo=lote.teste?27:33;
    linhas.forEach(t=>{ x.fillText(t, 40, yy); yy+=passo; });
""",
'etiqueta linhas teste')

html=rep(html,
"""  let rec=d.receita; if(rec.length>30) rec=rec.slice(0,30);
""",
"""  let rec=lote.teste?('TESTE · '+(lote.teste.baseRotulo||lote.teste.baseReceita||d.receita)):d.receita; if(rec.length>30) rec=rec.slice(0,30);
""",
'etiqueta massas teste')

# ---------------------------------------------------------------------------
# Funções do editor de Receita Teste
# ---------------------------------------------------------------------------
editor_js="""// ════════════════════════════════════════════════════════════
// RECEITA TESTE v25.3 — cópia independente de R1–R5, sem alterar padrões.
// Pesos críticos são digitados manualmente e confirmados visualmente.
// ════════════════════════════════════════════════════════════
const TESTE_CAMPOS=[
  {k:'bag',id:'teste-bag',nome:'Bagatelle',passo:'Bagatelle'},
  {k:'feu',id:'teste-feu',nome:'Feuilletage',passo:'Feuilletage'},
  {k:'ita',id:'teste-ita',nome:'Italiana 00',passo:'Italiana 00'},
  {k:'fermento',id:'teste-fermento',nome:'Fermento seco',passo:'Fermento seco'},
  {k:'acucar',id:'teste-acucar',nome:'Açúcar',passo:'Açúcar'},
  {k:'sal',id:'teste-sal',nome:'Sal refinado',passo:'Sal refinado'},
  {k:'manteiga',id:'teste-manteiga',nome:'Manteiga',passo:'Manteiga'},
  {k:'agua',id:'teste-agua',nome:'Água / gelo',passo:'Água com gelo'},
  {k:'leite',id:'teste-leite',nome:'Leite em pó',passo:'Leite em pó'},
  {k:'aprov',id:'teste-aprov',nome:'Aproveita / massa laminada',passo:'Massa laminada'},
  {k:'semLaminar',id:'teste-sem-laminar',nome:'Massa sem laminar',passo:'Massa sem laminar'},
];
function testeValorPasso(r,nome){ const p=(r&&r.passos||[]).find(x=>x.nome===nome); return p?Number(p.g)||0:0; }
function testeValoresBase(rid){
  const r=RECEITAS[rid]||RECEITAS.r3, v={};
  TESTE_CAMPOS.forEach(c=>v[c.k]=testeValorPasso(r,c.passo));
  return v;
}
function limparTesteAtivo(){ st.testeBase=null; st.testeReceita=null; st.testeMeta=null; }
function abrirTesteBase(){ limparTesteAtivo(); st.farinhasLotes=null; ir('teste-base'); }
function testeNumero(id){
  const el=document.getElementById(id); const s=String(el&&el.value!=null?el.value:'').trim().replace(',','.');
  if(!s) return null; const n=Number(s); return isFinite(n)?n:null;
}
function testeLerValores(){ const v={}; TESTE_CAMPOS.forEach(c=>v[c.k]=testeNumero(c.id)); return v; }
function abrirTesteEditor(rid){
  const r=RECEITAS[rid]; if(!r)return;
  limparTesteAtivo(); st.testeBase=rid; st.farinhasLotes=null;
  const v=testeValoresBase(rid);
  TESTE_CAMPOS.forEach(c=>{const el=document.getElementById(c.id);if(el)el.value=v[c.k];});
  const temp=document.getElementById('teste-temp'), horas=document.getElementById('teste-horas');
  if(r.fermentoFixo!=null){ temp.value=17; horas.value=r.fermentoHoras!=null?r.fermentoHoras:''; }
  else{ temp.value=''; horas.value=''; }
  document.getElementById('teste-obs').value='';
  document.getElementById('teste-edit-title').textContent='TESTE · base '+r.rotulo;
  atualizarResumoTeste(); ir('teste-edit');
}
function testeFermentoMudou(){
  const f=testeNumero('teste-fermento');
  const o=OPCOES_FERMENTO.find(x=>Number(x.fermento)===Number(f));
  if(o){ document.getElementById('teste-temp').value=o.temp; document.getElementById('teste-horas').value=o.horas; }
  atualizarResumoTeste();
}
function testeFermentoBase(rid,temp,horas){
  const r=RECEITAS[rid]; if(!r)return null;
  if(r.fermentoFixo!=null)return Number(r.fermentoFixo);
  const o=OPCOES_FERMENTO.find(x=>Number(x.temp)===Number(temp)&&Number(x.horas)===Number(horas));
  return o?Number(o.fermento):null;
}
function testeAlteracoes(rid,v,temp,horas){
  const r=RECEITAS[rid]||RECEITAS.r3, base=testeValoresBase(rid), out=[];
  TESTE_CAMPOS.forEach(c=>{
    let de=base[c.k];
    if(c.k==='fermento') de=testeFermentoBase(rid,temp,horas);
    const para=v[c.k];
    if(de==null || Number(de)!==Number(para)) out.push({k:c.k,nome:c.nome,de:de==null?null:Number(de),para:Number(para),unidade:'g'});
  });
  if(r.fermentoFixo!=null){
    if(Number(temp)!==17) out.push({k:'temp',nome:'Temperatura',de:17,para:Number(temp),unidade:'°C'});
    if(r.fermentoHoras!=null&&Number(horas)!==Number(r.fermentoHoras)) out.push({k:'horas',nome:'Fermentação',de:Number(r.fermentoHoras),para:Number(horas),unidade:'h'});
  }
  return out;
}
function testeFmtAlt(a){
  const u=a.unidade||''; const de=a.de==null?'definido no teste':(String(a.de)+u+' → ');
  return '<b>'+_escHtml(a.nome)+':</b> '+de+String(a.para)+u;
}
function atualizarResumoTeste(){
  const rid=st.testeBase, r=RECEITAS[rid], box=document.getElementById('teste-resumo'); if(!r||!box)return;
  const v=testeLerValores(); const faltam=TESTE_CAMPOS.filter(c=>v[c.k]==null);
  const temp=testeNumero('teste-temp'), horas=testeNumero('teste-horas');
  if(faltam.length){box.innerHTML='<div class="teste-total">Preencha todos os pesos</div><div class="teste-diffs">Falta: '+faltam.map(x=>_escHtml(x.nome)).join(', ')+'</div>';return;}
  const total=Object.values(v).reduce((s,n)=>s+(Number(n)||0),0);
  const alts=(temp!=null&&horas!=null)?testeAlteracoes(rid,v,temp,horas):[];
  const dif=alts.length?alts.map(testeFmtAlt).join('<br>'):'Nenhuma alteração de peso identificada ainda.';
  const fer=(temp==null||horas==null)?'<br><span style="color:var(--red)">Defina temperatura e horas da fermentação.</span>':'';
  box.innerHTML='<div class="teste-total">Total do teste: '+formatPeso(total)+'</div><div class="teste-diffs"><b>Alterações em relação à '+_escHtml(r.rotulo)+':</b><br>'+dif+fer+'</div>';
}
function salvarReceitaTeste(){
  const rid=st.testeBase, base=RECEITAS[rid]; if(!base){ir('teste-base');return;}
  const v=testeLerValores();
  for(const c of TESTE_CAMPOS){ const n=v[c.k]; if(n==null||n<0||!Number.isInteger(n)){alert('Confira '+c.nome+'. Use gramas inteiras, sem valor negativo.');document.getElementById(c.id).focus();return;} }
  const temp=testeNumero('teste-temp'), horas=testeNumero('teste-horas');
  if(temp==null||temp<=0){alert('Informe a temperatura da fermentação deste teste.');document.getElementById('teste-temp').focus();return;}
  if(horas==null||horas<=0){alert('Informe quantas horas de fermentação serão usadas neste teste.');document.getElementById('teste-horas').focus();return;}
  const farTxt='Bagatelle '+v.bag+' g, Feuilletage '+v.feu+' g, Italiana 00 '+v.ita+' g';
  const r=montarReceita({nome:'TESTE · '+base.rotulo,rotulo:'TESTE · '+base.rotulo,farinhas:farTxt,fermentoFixo:v.fermento,fermentoHoras:horas,teste:true,baseReceita:rid},
    v.bag,v.feu,v.ita,{agua:v.agua,acucar:v.acucar,leite:v.leite,sal:v.sal,manteiga:v.manteiga,aprov:v.aprov,semLaminar:v.semLaminar,fermento:v.fermento});
  // Zero de massa de aproveitamento continua registrado no snapshot, mas não vira um passo inútil de pesagem.
  r.passosLiquidos=r.passosLiquidos.filter(p=>!(p.nome==='Massa laminada'&&Number(p.g)===0));
  r.passosLiquidos.forEach((p,i)=>p.id=i+1);
  const agora=new Date(), obsTxt=String(document.getElementById('teste-obs').value||'').trim().slice(0,1200);
  const observacoes=obsTxt?[{id:FB.novoId('obs'),em:agora.toLocaleString('pt-BR'),emTs:agora.getTime(),op:getOp(),texto:obsTxt}]:[];
  st.testeReceita=r;
  st.testeMeta={id:FB.novoId('teste'),baseReceita:rid,baseNome:base.nome,baseRotulo:base.rotulo,criadoEm:agora.toLocaleString('pt-BR'),criadoTs:agora.getTime(),atualizadoTs:agora.getTime(),criadoPor:getOp(),valores:clonarReceita(v),fermentacao:{temp:Number(temp),fermento_g:v.fermento,horas:Number(horas)},alteracoes:testeAlteracoes(rid,v,temp,horas),observacoes};
  st.receita='teste'; st.temp=Number(temp); st.fermento=v.fermento; st.fermentoHoras=Number(horas); st.subModulo='secos'; st.farinhasLotes=null;
  RECEITA=r.passosSecos;
  const h=document.getElementById('hdr-rec');if(h)h.textContent='Secos · TESTE · '+base.rotulo;
  abrirLotesFarinha();
}
function voltarLotesFarinha(){ if(st.receita==='teste'&&st.testeReceita)ir('teste-edit'); else ir('receitas'); }

"""
html=rep(html,
"""// Escolhe qual receita rodar (r1, r2 ou r3), ajusta o cabeçalho e vai para a previsão de temperatura
function iniciarReceita(rid){
""",
editor_js+"""// Escolhe qual receita rodar (R1–R5), ajusta o cabeçalho e segue para os lotes de farinha.
function iniciarReceita(rid){
""",
'funcoes editor teste')

html=rep(html,
"""function iniciarReceita(rid){
  st.receita = RECEITAS[rid] ? rid : 'r1';
  st.subModulo='secos';
""",
"""function iniciarReceita(rid){
  limparTesteAtivo();
  st.receita = RECEITAS[rid] ? rid : 'r1';
  st.subModulo='secos';
""",
'limpar teste ao iniciar padrao')

html=rep(html,
"""  const r=RECEITAS[st.receita]||RECEITAS.r1;
  const sub=document.getElementById('far-lotes-rec'); if(sub)sub.textContent=r.nome+' · confirme antes de pesar';
""",
"""  const r=receitaAtualObj();
  const sub=document.getElementById('far-lotes-rec'); if(sub)sub.textContent=r.nome+' · confirme antes de pesar';
""",
'lotes farinha receita ativa')

html=rep(html,
"""  buscarPrevisaoMadrugada();
}
function lotesFarinhaResumo(p){
""",
"""  if(st.receita==='teste'&&st.testeReceita) iniciarSecos();
  else buscarPrevisaoMadrugada();
}
function lotesFarinhaResumo(p){
""",
'bypass clima no teste')

html=rep(html,
"""function escolherTemp(){
  const r=RECEITAS[st.receita]||RECEITAS.r1;
""",
"""function escolherTemp(){
  const r=receitaAtualObj();
""",
'escolher temp ativa')

html=rep(html,
"""function iniciarSecos(){
  if(!getKey()){ir('config');return;}
  st.subModulo='secos';
  RECEITA = RECEITAS[st.receita].passosSecos;
  const h=document.getElementById('hdr-rec'); if(h) h.textContent='Secos · '+RECEITAS[st.receita].rotulo;
""",
"""function iniciarSecos(){
  if(!getKey()){ir('config');return;}
  st.subModulo='secos';
  const r=receitaAtualObj();
  RECEITA = r.passosSecos;
  const h=document.getElementById('hdr-rec'); if(h) h.textContent='Secos · '+r.rotulo;
""",
'iniciar secos teste')

html=rep(html,
"""  st.liqLote=id;
  st.receita = RECEITAS[lote.receita] ? lote.receita : 'r1';
  st.subModulo='liquidos';
  const p=porcInfo(lote); st.temp=(p&&p.temp!=null)?p.temp:st.temp;
  RECEITA = RECEITAS[st.receita].passosLiquidos;
""",
"""  st.liqLote=id;
  const snap=receitaDoLote(lote);
  if(lote.teste&&snap){ st.receita='teste'; st.testeReceita=clonarReceita(snap); st.testeMeta=clonarReceita(lote.teste); st.testeBase=lote.teste.baseReceita||null; }
  else{ limparTesteAtivo(); st.receita = RECEITAS[lote.receita] ? lote.receita : 'r1'; }
  st.subModulo='liquidos';
  const p=porcInfo(lote); st.temp=(p&&p.temp!=null)?p.temp:st.temp; st.fermento=p&&p.fermento_g!=null?p.fermento_g:st.fermento; st.fermentoHoras=p&&p.fermento_horas!=null?p.fermento_horas:st.fermentoHoras;
  const r=snap||RECEITAS[st.receita]||RECEITAS.r1;
  RECEITA = r.passosLiquidos;
""",
'iniciar liquidos snapshot')

html=rep(html,
"""    st.sessionStart=0; st.modo='normal'; st.baldeSecos=1; st.liqLote=null;
    mostrarPerguntaSecos(false);
""",
"""    st.sessionStart=0; st.modo='normal'; st.baldeSecos=1; st.liqLote=null; limparTesteAtivo();
    mostrarPerguntaSecos(false);
""",
'voltar passo limpa teste')

html=rep(html,
"""function encerrar(){salvarSessao(false);pararVoz();liberarWakeLock();st.sessionStart=0;st.modo='normal';st.baldeSecos=1;st.liqLote=null;mostrarPerguntaSecos(false);ir('start');}
""",
"""function encerrar(){salvarSessao(false);pararVoz();liberarWakeLock();st.sessionStart=0;st.modo='normal';st.baldeSecos=1;st.liqLote=null;limparTesteAtivo();mostrarPerguntaSecos(false);ir('start');}
""",
'encerrar limpa teste')

html=rep(html,
"""function salvarSessao(ok){const all=LS.g('fdo_sess',[]);all.unshift({data:new Date().toLocaleString('pt-BR'),modulo:'Porcionamento '+(RECEITAS[st.receita]?RECEITAS[st.receita].rotulo:'R1')+' · '+(st.subModulo==='liquidos'?'Líquidos':'Secos'),op:getOp(),temp:st.temp,baldes_secos:st.baldeSecos||1,total_g:totalReceitaFull(st.receita),concluidos:st.done.size,total:RECEITA.length,dur:Math.round((Date.now()-st.sessionStart)/60000),ok});LS.s('fdo_sess',all.slice(0,60));}
""",
"""function salvarSessao(ok){const all=LS.g('fdo_sess',[]),r=receitaAtualObj();all.unshift({data:new Date().toLocaleString('pt-BR'),modulo:'Porcionamento '+(r?r.rotulo:'R1')+' · '+(st.subModulo==='liquidos'?'Líquidos':'Secos'),op:getOp(),temp:st.temp,baldes_secos:st.baldeSecos||1,total_g:totalReceitaFull(st.receita),concluidos:st.done.size,total:RECEITA.length,dur:Math.round((Date.now()-st.sessionStart)/60000),ok});LS.s('fdo_sess',all.slice(0,60));}
""",
'sessao teste')

# ---------------------------------------------------------------------------
# Histórico: diferenças + observações acrescentáveis (sem editar snapshot)
# ---------------------------------------------------------------------------
hist_helpers="""function testeAltHistorico(t){
  const a=t&&Array.isArray(t.alteracoes)?t.alteracoes:[];
  if(!a.length)return 'Sem alteração em relação à base.';
  return a.map(x=>{const u=x.unidade||'';const de=x.de==null?'definido no teste':(String(x.de)+u+' → ');return '<b>'+_escHtml(x.nome||'Alteração')+':</b> '+de+String(x.para)+u;}).join('<br>');
}
function testeObsHistorico(t){
  const a=t&&Array.isArray(t.observacoes)?t.observacoes:[];
  if(!a.length)return '<span style="color:var(--mut)">Nenhuma observação registrada.</span>';
  return a.map(o=>'<div style="margin-top:.2rem">'+_escHtml(o.em||'')+(o.op?' · '+_escHtml(o.op):'')+' — '+_escHtml(o.texto||'')+'</div>').join('');
}
function renderTesteHistorico(l){
  const t=l&&l.teste;if(!t)return '';
  return `<div class="teste-hist"><div class="teste-hist-title">🧪 TESTE · BASE ${_escHtml(t.baseRotulo||t.baseReceita||'—')}</div><div class="teste-hist-row"><b>Alterações executadas</b><br>${testeAltHistorico(t)}</div><div class="teste-hist-row"><b>Observações</b>${testeObsHistorico(t)}</div><button class="teste-obs-btn" onclick="adicionarObsTeste('${l.id}')">+ Acrescentar observação</button></div>`;
}
function adicionarObsTeste(id){
  const todos=LS.g('fdo_lotes',[]),l=todos.find(x=>x.id===id);if(!l||!l.teste)return;
  const txt=String(prompt('Nova observação sobre o resultado deste teste:')||'').trim().slice(0,1200);if(!txt)return;
  const agora=new Date();l.teste.observacoes=Array.isArray(l.teste.observacoes)?l.teste.observacoes:[];
  l.teste.observacoes.push({id:FB.novoId('obs'),em:agora.toLocaleString('pt-BR'),emTs:agora.getTime(),op:getOp(),texto:txt});
  l.teste.atualizadoTs=agora.getTime();LS.s('fdo_lotes',todos);renderHist();
}
"""
html=rep(html,"function renderHist(){\n",hist_helpers+"function renderHist(){\n",'helpers historico teste')

html=rep(html,
"""    const btnDel = podeApagar ? (cancelado
      ? `<button class="lote-del" onclick="restaurarLote('${l.id}')" title="Restaurar balde">↩</button>`
      : `<button class="lote-del" onclick="apagarLote('${l.id}')" title="Cancelar balde">🗑</button>`) : '';
    return `<div class="lote-card ${cancelado?'cancelado':''}">
""",
"""    const btnDel = podeApagar ? (cancelado
      ? `<button class="lote-del" onclick="restaurarLote('${l.id}')" title="Restaurar balde">↩</button>`
      : `<button class="lote-del" onclick="apagarLote('${l.id}')" title="Cancelar balde">🗑</button>`) : '';
    const testeHtml=renderTesteHistorico(l);
    return `<div class="lote-card ${cancelado?'cancelado':''}">
""",
'historico prepara teste')

html=rep(html,
"""      <div class="lote-meta">${meta}</div>
      ${cancelado?`<div class="lote-cancelado">CANCELADO · ${l.cancelado.em||''} · ${_escHtml(l.cancelado.op||'')}</div>`:''}
      <div class="lote-etapas">${chips}</div>
""",
"""      <div class="lote-meta">${meta}</div>
      ${cancelado?`<div class="lote-cancelado">CANCELADO · ${l.cancelado.em||''} · ${_escHtml(l.cancelado.op||'')}</div>`:''}
      ${testeHtml}
      <div class="lote-etapas">${chips}</div>
""",
'historico mostra teste')

# Testes não contaminam média das receitas padrão.
html=rep(html,
"""  feitos.forEach(x=>{
    const seg=Number(x.b.tempoSeg);
""",
"""  feitos.forEach(x=>{
    if(x.lote&&x.lote.teste) return;
    const seg=Number(x.b.tempoSeg);
""",
'media ignora teste')

# ---------------------------------------------------------------------------
# Laminação: testes diferentes nunca se misturam mesmo com a mesma base.
# ---------------------------------------------------------------------------
html=rep(html,
"""// Chave de compatibilidade completa do balde.
function lamChave(l){ return l?((l.receita||'')+'§'+lamDiaMassa(l)+'§'+lamFermChave(l)):null; }
""",
"""// Chave de compatibilidade completa do balde. Testes usam o ID do teste para não misturar experiências diferentes.
function loteReceitaChave(l){ return l&&l.teste&&l.teste.id?('teste:'+l.teste.id):((l&&l.receita)||''); }
function lamChave(l){ return l?(loteReceitaChave(l)+'§'+lamDiaMassa(l)+'§'+lamFermChave(l)):null; }
""",
'laminacao chave teste')

html=rep(html,
"""    chaves.add(lamChave(l));
    receitas.add(l.receita);
    composicao.push({loteId:id, loteNum:l.num, dataLote:dia, partes:q, receita:l.receita});
""",
"""    chaves.add(lamChave(l));
    receitas.add(loteReceitaChave(l));
    composicao.push({loteId:id, loteNum:l.num, dataLote:dia, partes:q, receita:l.receita, receitaChave:loteReceitaChave(l), testeId:l.teste&&l.teste.id||null});
""",
'laminacao composicao teste')

html=rep(html,
"""  let receitaNome='Misto', receita='misto';
  if(receitas.size===1){ receita=[...receitas][0]; receitaNome=(RECEITAS[receita]&&RECEITAS[receita].rotulo)||''; }
  const lam={
""",
"""  let receitaNome='Misto', receita='misto', testeId=null;
  if(receitas.size===1){
    const primeiro=todos.find(x=>x.id===composicao[0].loteId);
    receita=(primeiro&&primeiro.receita)||'misto';
    receitaNome=(primeiro&&(primeiro.receitaNome||primeiro.rotulo))||((RECEITAS[receita]&&RECEITAS[receita].rotulo)||'');
    testeId=primeiro&&primeiro.teste&&primeiro.teste.id||null;
  }
  const lam={
""",
'laminacao nome teste')

html=rep(html,
"""    receita, receitaNome, composicao, totalPartes:total, temMassaAnterior:temAnterior, op:getOp(),
""",
"""    receita, receitaNome, testeId, composicao, totalPartes:total, temMassaAnterior:temAnterior, op:getOp(),
""",
'laminacao salva teste')

# ---------------------------------------------------------------------------
# Sync v25: observações posteriores participam do relógio e se unem no merge.
# ---------------------------------------------------------------------------
html=rep(html,
"""  ts(x){if(!x)return 0;let m=Math.max(Number(x.criadoTs)||0,Number(x.dataTs)||0,Number(x.deletedTs)||0,Number(x.cancelado&&x.cancelado.emTs)||0,Number(x.restaurado&&x.restaurado.emTs)||0);Object.values(x.etapas||{}).forEach(v=>m=Math.max(m,Number(v&&v.emTs)||0));return m},
""",
"""  ts(x){if(!x)return 0;let m=Math.max(Number(x.criadoTs)||0,Number(x.dataTs)||0,Number(x.deletedTs)||0,Number(x.cancelado&&x.cancelado.emTs)||0,Number(x.restaurado&&x.restaurado.emTs)||0);Object.values(x.etapas||{}).forEach(v=>m=Math.max(m,Number(v&&v.emTs)||0));const t=x.teste||null;if(t){m=Math.max(m,Number(t.criadoTs)||0,Number(t.atualizadoTs)||0);(t.observacoes||[]).forEach(v=>m=Math.max(m,Number(v&&v.emTs)||0));}return m},
""",
'sync timestamp teste')

html=rep(html,
"""    const ra=a.restaurado,rb=b.restaurado;if(ra||rb)base.restaurado=(Number(rb&&rb.emTs)||0)>=(Number(ra&&ra.emTs)||0)?this.clone(rb||ra):this.clone(ra);
    return base;
""",
"""    const ra=a.restaurado,rb=b.restaurado;if(ra||rb)base.restaurado=(Number(rb&&rb.emTs)||0)>=(Number(ra&&ra.emTs)||0)?this.clone(rb||ra):this.clone(ra);
    const ta=a.teste,tb=b.teste;if(ta||tb){
      const novo=this.ts(b)>=this.ts(a)?this.clone(tb||ta):this.clone(ta||tb),obs=[],seen=new Set();
      [...((ta&&ta.observacoes)||[]),...((tb&&tb.observacoes)||[])].forEach(o=>{if(!o)return;const k=o.id||((o.emTs||'')+'|'+(o.texto||''));if(seen.has(k))return;seen.add(k);obs.push(this.clone(o));});
      obs.sort((x,y)=>(Number(x.emTs)||0)-(Number(y.emTs)||0));
      base.teste={...(novo||{}),observacoes:obs,atualizadoTs:Math.max(Number(ta&&ta.atualizadoTs)||0,Number(tb&&tb.atualizadoTs)||0,...obs.map(o=>Number(o.emTs)||0))};
    }
    return base;
""",
'sync merge observacoes teste')

# ---------------------------------------------------------------------------
# Service Worker / cache
# ---------------------------------------------------------------------------
sw=rep(sw,"const CACHE='fdo-v25-2';","const CACHE='fdo-v25-3';",'cache v25.3')

# ---------------------------------------------------------------------------
# Validador: marcadores v25.3 + cálculo do exemplo recebido (15.448 g)
# ---------------------------------------------------------------------------
valid=rep(valid,
"""errors=[]

def fail(msg): errors.append(msg)

# v25.2 — Firebase Authentication + autorização do aparelho + rules as code
""",
"""errors=[]

def fail(msg): errors.append(msg)

# v25.3 — Receita Teste rastreável, sem alterar R1–R5
for marker in ('Receita Teste','s-teste-base','s-teste-edit','receitaSnapshot','testeAlteracoes(','adicionarObsTeste(','loteReceitaChave(','testeLinhasEtiqueta('):
    if marker not in html: fail('v25.3 sem marcador: '+marker)

# v25.2 — Firebase Authentication + autorização do aparelho + rules as code
""",
'validator marcadores v25.3')

valid=rep(valid,
"""        expected={'r1':15464,'r2':15690,'r3':15544,'r4':15564,'r5':15714}
        if totals!=expected: fail(f'Totais das receitas alterados: esperado {expected}, obtido {totals}')

if errors:
""",
"""        expected={'r1':15464,'r2':15690,'r3':15544,'r4':15564,'r5':15714}
        if totals!=expected: fail(f'Totais das receitas alterados: esperado {expected}, obtido {totals}')

# 7) Exemplo de Receita Teste informado para a v25.3: total precisa fechar em 15.448 g.
if start>=0 and end>start:
    teste_js=inline[start:end]+"""\nconst __t=montarReceita({nome:'TESTE',rotulo:'TESTE',farinhas:''},4113,0,5027,{agua:4110,acucar:1030,leite:204,sal:204,manteiga:714,aprov:0,semLaminar:0,fermento:46});\nconsole.log((__t.passos||[]).reduce((s,p)=>s+(p.g||0),0));\n"""
    with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8') as f:
        f.write(teste_js); tfile=f.name
    tr=subprocess.run(['node',tfile],capture_output=True,text=True)
    if tr.returncode: fail('Falha ao simular Receita Teste: '+tr.stderr.strip())
    else:
        try: ttotal=int(float(tr.stdout.strip().splitlines()[-1]))
        except Exception: ttotal=-1
        if ttotal!=15448: fail(f'Receita Teste de referência deveria totalizar 15448 g, obtido {ttotal}')

if errors:
""",
'validator total teste')

valid=rep(valid,
"""print('VALIDAÇÃO FDO OK')
print('Receitas: R1=15464 R2=15690 R3=15544 R4=15564 R5=15714 g')
""",
"""print('VALIDAÇÃO FDO OK')
print('Receitas: R1=15464 R2=15690 R3=15544 R4=15564 R5=15714 g')
print('Receita Teste de referência v25.3: 15448 g')
""",
'validator saida teste')

# ---------------------------------------------------------------------------
# Teste sync: duas observações feitas em momentos/aparelhos diferentes não somem.
# ---------------------------------------------------------------------------
sync_test=rep(sync_test,
"""// 4) Laminação online: duas operações não podem consumir as mesmas partes.
(async()=>{
""",
"""// 4) Receita Teste: observações posteriores não podem ser perdidas no merge.
{
  const a={id:'lt',criadoTs:1,teste:{id:'t1',criadoTs:1,atualizadoTs:100,observacoes:[{id:'o1',emTs:100,texto:'primeira'}]}};
  const b={id:'lt',criadoTs:1,teste:{id:'t1',criadoTs:1,atualizadoTs:200,observacoes:[{id:'o2',emTs:200,texto:'segunda'}]}};
  const m=S.merge('fdo_lotes',a,b);
  assert(m.teste&&m.teste.observacoes.length===2,'merge perdeu observação da Receita Teste');
  assert(S.ts(m)===200,'timestamp da observação do teste não entrou no relógio de sincronização');
}

// 5) Laminação online: duas operações não podem consumir as mesmas partes.
(async()=>{
""",
'sync test observacoes')

sync_test=rep(sync_test,
"""  // 5) Contador online: transações consecutivas têm números únicos.
""",
"""  // 6) Contador online: transações consecutivas têm números únicos.
""",
'sync renumera teste')

# ---------------------------------------------------------------------------
# Sanidade do patch antes de gravar
# ---------------------------------------------------------------------------
for marker in [
    'FOLHADOS D\'OURO — atualização v25.3',
    'id="s-teste-base"','id="s-teste-edit"','function salvarReceitaTeste()',
    'receitaSnapshot=clonarReceita','function adicionarObsTeste(id)',
    "const CACHE='fdo-v25-3';"
]:
    src=sw if marker.startswith('const CACHE') else html
    if marker not in src:
        raise SystemExit('Marcador final ausente: '+marker)

# Garante que definições das cinco receitas padrão continuam literalmente presentes.
for linha in [
"r1: montarReceita({ nome:'Receita 1',              rotulo:'R1', farinhas:'Bagatelle 45%, Feuilletage 45%, Italiana 10%' },            3600,3600,800),",
"r2: montarReceita({ nome:'Receita 2 - MASSA 3 KG', rotulo:'R2', farinhas:'Bagatelle 3500 g, Italiana 4270 g (sem Feuilletage)' },     3500,0,4270,{agua:3500, acucar:876, aprov:3000}),",
"r3: montarReceita({ nome:'Receita 3 - PADRÃO',     rotulo:'R3', farinhas:'Bagatelle 3600 g, Italiana 4400 g (sem Feuilletage)' },     3600,0,4400,{agua:3600}),",
"r4: montarReceita({ nome:'Massa 3 kg sem manteiga', rotulo:'R4', farinhas:'Bagatelle 3500 g, Italiana 4270 g (sem manteiga)', fermentoFixo:70, fermentoHoras:14 },",
"r5: montarReceita({ nome:'1 kg sem laminar', rotulo:'R5', farinhas:'Bagatelle 3370 g, Italiana 4118 g (sem Feuilletage)', fermentoFixo:64, fermentoHoras:17 },",
]:
    if linha not in html: raise SystemExit('Definição padrão alterada/ausente: '+linha[:24])

INDEX.write_text(html,encoding='utf-8')
SW.write_text(sw,encoding='utf-8')
VALID.write_text(valid,encoding='utf-8')
SYNC_TEST.write_text(sync_test,encoding='utf-8')
print('PATCH_RECEITA_TESTE_V25_3_OK')
