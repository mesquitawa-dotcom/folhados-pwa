from pathlib import Path

INDEX = Path('index.html')
SW = Path('sw.js')
text = INDEX.read_text(encoding='utf-8')


def replace_once(old, new, label):
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    text = text.replace(old, new, 1)

# Version note
replace_once(
"       FOLHADOS D'OURO — atualização v24.8\n       NOVIDADES v24.8:",
"       FOLHADOS D'OURO — atualização v24.10\n       NOVIDADES v24.10:\n       • Rastreabilidade das farinhas: antes do porcionamento, confirma os\n         lotes da Bagatelle e da Italiana 00, lembrando os últimos usados.\n       • Troca rara no meio do balde: permite registrar um segundo lote; o\n         próximo porcionamento passa a sugerir automaticamente o lote novo.\n       • Cada balde guarda uma fotografia dos lotes de farinha utilizados e\n         o Histórico passa a exibi-los para rastreabilidade.\n       NOVIDADES v24.8:",
"version header")

# CSS for compact lot confirmation screen
marker_css = "    /* ════ PRE TEMP SCREEN (NOVA TELA) ════ */"
css = r'''    /* ════ v24.10 — LOTES DAS FARINHAS ════ */
    #s-farinha-lotes{padding:0}
    .far-lotes-body{flex:1;overflow-y:auto;padding:.2rem 1rem 1rem;display:flex;flex-direction:column;gap:.65rem}
    .far-lote-card{background:var(--bg3);border:1px solid var(--brd);border-radius:.55rem;padding:.85rem}
    .far-lote-nome{font-size:.9rem;color:var(--gl);font-weight:bold;margin-bottom:.2rem}
    .far-lote-hint{font-size:.68rem;color:var(--mut);line-height:1.35;margin-bottom:.55rem}
    .far-extra{display:none;margin-top:.55rem;padding-top:.55rem;border-top:1px solid var(--brd)}
    .far-extra.show{display:block}
    .far-lotes-note{font-size:.68rem;color:var(--mut);line-height:1.4;text-align:center;padding:0 .3rem}

'''
if marker_css not in text:
    raise SystemExit('css marker not found')
text = text.replace(marker_css, css + marker_css, 1)

# New screen after recipe selection, before liquids selection
marker_html = "<!-- ═══ PORCIONAMENTO DE LÍQUIDOS — seleção de lote ═══ -->"
screen = r'''<!-- ═══ LOTES DAS FARINHAS — confirmação rápida antes dos secos (v24.10) ═══ -->
<div id="s-farinha-lotes" class="scr off">
  <div class="start-top">
    <div class="start-icon">🌾</div>
    <div class="start-brand">Folhados d'Ouro</div>
    <div class="start-title">Lotes das Farinhas</div>
    <div class="start-sub" id="far-lotes-rec">Confirme os lotes em uso</div>
  </div>
  <div class="far-lotes-body">
    <div class="far-lote-card">
      <div class="far-lote-nome">Farinha francesa · Bagatelle</div>
      <div class="far-lote-hint">O último lote usado já aparece preenchido.</div>
      <input id="far-lote-bag" class="inp" type="text" maxlength="40" autocomplete="off" autocapitalize="characters" placeholder="Ex.: lote 12345">
      <button class="link-btn" style="width:100%;margin-top:.55rem" onclick="farToggleExtra('bag')">+ Entrou outro lote neste balde</button>
      <div id="far-extra-bag" class="far-extra">
        <div class="far-lote-hint">Informe o lote que entrou depois. Ele será sugerido como lote atual no próximo porcionamento.</div>
        <input id="far-lote-bag-extra" class="inp" type="text" maxlength="40" autocomplete="off" autocapitalize="characters" placeholder="Novo lote Bagatelle">
      </div>
    </div>
    <div class="far-lote-card">
      <div class="far-lote-nome">Farinha Italiana 00</div>
      <div class="far-lote-hint">O último lote usado já aparece preenchido.</div>
      <input id="far-lote-ita" class="inp" type="text" maxlength="40" autocomplete="off" autocapitalize="characters" placeholder="Ex.: lote 070">
      <button class="link-btn" style="width:100%;margin-top:.55rem" onclick="farToggleExtra('ita')">+ Entrou outro lote neste balde</button>
      <div id="far-extra-ita" class="far-extra">
        <div class="far-lote-hint">Informe o lote que entrou depois. Ele será sugerido como lote atual no próximo porcionamento.</div>
        <input id="far-lote-ita-extra" class="inp" type="text" maxlength="40" autocomplete="off" autocapitalize="characters" placeholder="Novo lote Italiana 00">
      </div>
    </div>
    <button class="btn-main" id="far-lotes-confirm-btn" onclick="confirmarLotesFarinha()">✓ Confirmar lotes e começar</button>
    <div class="far-lotes-note">Normalmente basta conferir os dois números e tocar no botão. Só altere quando abrir farinha de outro lote.</div>
  </div>
  <div class="start-footer">
    <button class="link-btn" onclick="ir('receitas')">← Trocar receita</button>
  </div>
</div>

'''
if marker_html not in text:
    raise SystemExit('html marker not found')
text = text.replace(marker_html, screen + marker_html, 1)

# Back from weather to flour lots
replace_once(
'''  <div class="start-footer">\n    <button class="link-btn" onclick="ir('start')">← Voltar</button>\n  </div>\n</div>\n\n<div id="s-temp" class="scr off">'''.replace('\\n','\n'),
'''  <div class="start-footer">\n    <button class="link-btn" onclick="abrirLotesFarinha()">← Lotes das farinhas</button>\n  </div>\n</div>\n\n<div id="s-temp" class="scr off">'''.replace('\\n','\n'),
"pre-temp back button")

# State snapshot
replace_once(
"  fermLote:null,fermStart:0,fermMin:24,fermMax:28,lamSel:{},\n  loginOpId:null,loginFiltro:''};",
"  fermLote:null,fermStart:0,fermMin:24,fermMax:28,lamSel:{},farinhasLotes:null,\n  loginOpId:null,loginFiltro:''};",
"state field")

# Sync current flour lots between production devices
replace_once(
"const FB_SYNC_KEYS=['fdo_lotes','fdo_laminacoes','fdo_lote_seq','fdo_operadores'];",
"const FB_SYNC_KEYS=['fdo_lotes','fdo_laminacoes','fdo_lote_seq','fdo_operadores','fdo_farinha_lotes_atuais'];",
"firebase sync keys")

# Persist exact lots inside each balde
replace_once(
"      op:getOp(), temp:st.temp, fermento_g:st.fermento, fermento_horas:st.fermentoHoras, baldes_secos:st.baldeSecos||1,",
"      op:getOp(), temp:st.temp, fermento_g:st.fermento, fermento_horas:st.fermentoHoras, baldes_secos:st.baldeSecos||1,\n      farinhas_lotes:st.farinhasLotes?JSON.parse(JSON.stringify(st.farinhasLotes)):null,",
"balde flour lot snapshot")

# Recipe selection now goes to flour lots first
old_recipe = '''function iniciarReceita(rid){
  st.receita = RECEITAS[rid] ? rid : 'r1';
  st.subModulo='secos';
  RECEITA = RECEITAS[st.receita].passosSecos;
  const h=document.getElementById('hdr-rec');
  if(h) h.textContent='Secos · '+RECEITAS[st.receita].rotulo;
  buscarPrevisaoMadrugada();
}

// Nova função que busca e renderiza o cálculo automático na tela intermediária'''
new_recipe = r'''function iniciarReceita(rid){
  st.receita = RECEITAS[rid] ? rid : 'r1';
  st.subModulo='secos';
  st.farinhasLotes=null; // nova seleção de receita = nova confirmação dos lotes
  RECEITA = RECEITAS[st.receita].passosSecos;
  const h=document.getElementById('hdr-rec');
  if(h) h.textContent='Secos · '+RECEITAS[st.receita].rotulo;
  abrirLotesFarinha();
}

// LOTES DAS FARINHAS (v24.10) — confirmação rápida com memória do último lote.
// O lote atual é sincronizado entre aparelhos. Cada balde recebe uma cópia
// própria, preservando a rastreabilidade mesmo quando o lote atual mudar.
function normalizarLoteFarinha(v){
  return String(v==null?'':v).replace(/[\u0000-\u001f\u007f]/g,'').trim().replace(/\s+/g,' ').slice(0,40);
}
function lotesFarinhaAtuais(){
  const x=LS.g('fdo_farinha_lotes_atuais',{})||{};
  return {bagatelle:normalizarLoteFarinha(x.bagatelle), italiana00:normalizarLoteFarinha(x.italiana00)};
}
function farMostrarExtra(tipo,mostrar){
  const el=document.getElementById(tipo==='bag'?'far-extra-bag':'far-extra-ita');
  if(el) el.classList.toggle('show',!!mostrar);
}
function farToggleExtra(tipo){
  const el=document.getElementById(tipo==='bag'?'far-extra-bag':'far-extra-ita');
  if(!el)return;
  const mostrar=!el.classList.contains('show');
  farMostrarExtra(tipo,mostrar);
  if(mostrar){
    const inp=document.getElementById(tipo==='bag'?'far-lote-bag-extra':'far-lote-ita-extra');
    if(inp){setTimeout(()=>inp.focus(),50);}
  }
}
function abrirLotesFarinha(){
  const ult=lotesFarinhaAtuais();
  const snap=st.farinhasLotes||{};
  const bag=snap.bagatelle||{};
  const ita=snap.italiana00||{};
  const bagPrincipal=normalizarLoteFarinha(bag.principal)||ult.bagatelle;
  const itaPrincipal=normalizarLoteFarinha(ita.principal)||ult.italiana00;
  const bagExtra=normalizarLoteFarinha(bag.adicional);
  const itaExtra=normalizarLoteFarinha(ita.adicional);
  document.getElementById('far-lote-bag').value=bagPrincipal;
  document.getElementById('far-lote-ita').value=itaPrincipal;
  document.getElementById('far-lote-bag-extra').value=bagExtra;
  document.getElementById('far-lote-ita-extra').value=itaExtra;
  farMostrarExtra('bag',!!bagExtra); farMostrarExtra('ita',!!itaExtra);
  const r=RECEITAS[st.receita]||RECEITAS.r1;
  const sub=document.getElementById('far-lotes-rec'); if(sub)sub.textContent=r.nome+' · confirme antes de pesar';
  const btn=document.getElementById('far-lotes-confirm-btn');
  if(btn)btn.textContent=(bagPrincipal&&itaPrincipal)?'✓ MESMOS LOTES — COMEÇAR':'✓ CONFIRMAR LOTES E COMEÇAR';
  ir('farinha-lotes');
}
function confirmarLotesFarinha(){
  const bag=normalizarLoteFarinha(document.getElementById('far-lote-bag').value);
  const ita=normalizarLoteFarinha(document.getElementById('far-lote-ita').value);
  const bag2=normalizarLoteFarinha(document.getElementById('far-lote-bag-extra').value);
  const ita2=normalizarLoteFarinha(document.getElementById('far-lote-ita-extra').value);
  if(!bag){ alert('Informe o lote da farinha Bagatelle.'); document.getElementById('far-lote-bag').focus(); return; }
  if(!ita){ alert('Informe o lote da farinha Italiana 00.'); document.getElementById('far-lote-ita').focus(); return; }
  st.farinhasLotes={
    bagatelle:{principal:bag,adicional:bag2||null},
    italiana00:{principal:ita,adicional:ita2||null}
  };
  // Se houve troca no meio do balde, o lote novo vira automaticamente o atual.
  LS.s('fdo_farinha_lotes_atuais',{
    bagatelle:bag2||bag,
    italiana00:ita2||ita,
    atualizadoTs:Date.now(),
    op:getOp()
  });
  buscarPrevisaoMadrugada();
}
function lotesFarinhaResumo(p){
  const f=p&&p.farinhas_lotes; if(!f)return '';
  function um(nome,d){
    if(!d)return '';
    const a=normalizarLoteFarinha(d.principal), b=normalizarLoteFarinha(d.adicional);
    if(!a)return '';
    return nome+' '+_escHtml(a)+(b?(' → '+_escHtml(b)):'');
  }
  return [um('Bagatelle',f.bagatelle),um('00',f.italiana00)].filter(Boolean).join(' · ');
}

// Nova função que busca e renderiza o cálculo automático na tela intermediária'''
replace_once(old_recipe, new_recipe, "recipe flow and flour functions")

# Show flour lot traceability in history
replace_once(
'''    const meta=[
      l.criado||'—',
      p.op?('op. '+p.op):'',
      p.temp?(p.temp+'°C'):'',
      (p.baldes_secos&&p.baldes_secos>1)?(p.baldes_secos+'x secos'):'',
      p.total_g?('total '+formatPeso(p.total_g)):''
    ].filter(Boolean).join(' · ');''',
'''    const farResumo=lotesFarinhaResumo(p);
    const meta=[
      l.criado||'—',
      p.op?('op. '+p.op):'',
      p.temp?(p.temp+'°C'):'',
      farResumo,
      (p.baldes_secos&&p.baldes_secos>1)?(p.baldes_secos+'x secos'):'',
      p.total_g?('total '+formatPeso(p.total_g)):''
    ].filter(Boolean).join(' · ');''',
"history flour lot summary")

INDEX.write_text(text, encoding='utf-8')

sw = SW.read_text(encoding='utf-8')
old_cache = "const CACHE='fdo-v24-9';"
if sw.count(old_cache) != 1:
    raise SystemExit(f'service worker cache: expected 1 occurrence, found {sw.count(old_cache)}')
sw = sw.replace(old_cache, "const CACHE='fdo-v24-10';", 1)
SW.write_text(sw, encoding='utf-8')

print('Patch v24.10 applied successfully.')
