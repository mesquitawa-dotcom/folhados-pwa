from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/'index.html'
SW=ROOT/'sw.js'
VALID=ROOT/'tools'/'validate_fdo.py'
WORKFLOW=ROOT/'.github'/'workflows'/'validate-fdo.yml'
NEW_TEST=ROOT/'tools'/'test_estoque_v26_0.js'
SELF=ROOT/'tools'/'apply_v26_0.py'
SELF_WORKFLOW=ROOT/'.github'/'workflows'/'apply-v26-0.yml'

STYLES=(ROOT/'tools'/'_v26_styles.css').read_text(encoding='utf-8')
SCREENS=(ROOT/'tools'/'_v26_screens.html').read_text(encoding='utf-8')
MODULE=(ROOT/'tools'/'_v26_module.js').read_text(encoding='utf-8')
TEST=(ROOT/'tools'/'test_estoque_v26_0.js').read_text(encoding='utf-8')

def fail(msg):
    raise RuntimeError(msg)

def replace_once(text, old, new, label):
    n=text.count(old)
    if n!=1: fail(f"{label}: esperado 1 marcador, encontrado {n}")
    return text.replace(old,new,1)

html=HTML.read_text(encoding='utf-8')
if 'atualização v26.0' in html and 'id="s-estoque"' in html:
    fail('v26.0 já parece aplicada; abortando para não duplicar')
if 'atualização v25.3' not in html:
    fail('base inesperada: v25.3 não encontrada')

old_head="""       FOLHADOS D'OURO — atualização v25.3
       NOVIDADES v25.3:
"""
new_head="""       FOLHADOS D'OURO — atualização v26.0
       NOVIDADES v26.0:
       • Consulta da receita completa na própria seleção do porcionamento, com Observações ao final.
       • Estoque simples: entradas, baixas automáticas por balde e saldo calculado dos insumos.
       • Conferência física semanal independente para insumos e caixas, permitindo comparar previsto × encontrado.
       • Farinhas controladas por marca, sem usar o lote da rastreabilidade como dimensão do estoque.
       NOVIDADES v25.3:
"""
html=replace_once(html,old_head,new_head,'cabeçalho')

html=replace_once(html,'  </style>',STYLES+'\n  </style>','inserção do CSS')
stock_card="""    <div class="modulo ativo" data-perm="estoque" onclick="entrarEstoque()">
      <div class="modulo-icon">📦</div>
      <div class="modulo-info"><div class="modulo-nome">Estoque</div><div class="modulo-desc">Entradas, consumo das receitas e conferência semanal</div></div>
      <div class="modulo-badge badge-ativo">Ativo</div>
    </div>
"""
model_anchor="""    <div class="modulo inativo">
      <div class="modulo-icon">✂️</div>"""
html=replace_once(html,model_anchor,stock_card+model_anchor,'cartão Estoque')

for rid in ('r1','r2','r3','r4','r5'):
    start=html.find(f'<div class="modulo ativo" onclick="iniciarReceita(\'{rid}\')">')
    if start<0: fail('cartão de receita não encontrado: '+rid)
    nxt=html.find('    <div class="modulo ativo"',start+10)
    if nxt<0: fail('fim do cartão não encontrado: '+rid)
    seg=html[start:nxt]
    old='<div class="modulo-badge badge-ativo">Ativo</div>'
    if seg.count(old)!=1: fail('selo Ativo inesperado em '+rid)
    seg=seg.replace(old,f'<button class="receita-ver" onclick="event.stopPropagation();abrirReceitaCompleta(\'{rid}\')">📋 Receita</button>',1)
    html=html[:start]+seg+html[nxt:]

screen_anchor='<!-- ═══ RECEITA TESTE — base + edição do lote experimental (v25.3) ═══ -->'
html=replace_once(html,screen_anchor,SCREENS+'\n'+screen_anchor,'telas v26.0')
html=replace_once(html,'const st={',MODULE+'\n\nconst st={','módulo JavaScript v26.0')

old_liberar="""  liberar(comNuvem){
    if(comNuvem){if(!this.cloudStarted){this.cloudStarted=true;SYNC25.init();}else if(SYNC25.iniciado)FB.aoVoltarOnline();}
    if(this.bootLiberado)return;this.bootLiberado=true;const cb=this.bootCb;if(typeof cb==='function')cb();
  },"""
new_liberar="""  liberar(comNuvem){
    if(comNuvem){
      if(!this.cloudStarted){this.cloudStarted=true;SYNC25.init();if(typeof ESTOQUE_SYNC!=='undefined')ESTOQUE_SYNC.init();}
      else if(SYNC25.iniciado)FB.aoVoltarOnline();
    }
    if(this.bootLiberado)return;this.bootLiberado=true;const cb=this.bootCb;if(typeof cb==='function')cb();
  },"""
html=replace_once(html,old_liberar,new_liberar,'DEVICE.liberar')

html=replace_once(html,"""  repaint(){
    try{
""","""  repaint(){
    try{
      garantirPermissoesV260();
      estoqueReconciliarSaidasLotes();
""",'FB.repaint início')
html=replace_once(html,"""      if(id==='s-history' && typeof renderHist==='function') renderHist();
""","""      if(id==='s-estoque' && typeof renderEstoque==='function') renderEstoque();
      else if(id==='s-estoque-mov' && typeof renderEstoqueMovimentos==='function') renderEstoqueMovimentos();
      else if(id==='s-receita-completa' && typeof renderReceitaCompleta==='function') renderReceitaCompleta();
      else if(id==='s-history' && typeof renderHist==='function') renderHist();
""",'casos de repaint')

html=replace_once(html,"""  {k:'assistente',    icon:'🤖', label:'Assistente IA'}
];""","""  {k:'assistente',    icon:'🤖', label:'Assistente IA'},
  {k:'estoque',       icon:'📦', label:'Estoque'}
];""",'permissão de módulo Estoque')
html=replace_once(html,"""  {k:'geo_bypass', icon:'📍', label:'Pode acessar fora da fábrica'}
];""","""  {k:'geo_bypass',      icon:'📍', label:'Pode acessar fora da fábrica'},
  {k:'estoque_entrada', icon:'＋', label:'Pode registrar entradas de estoque'},
  {k:'estoque_contagem',icon:'✓', label:'Pode registrar conferência semanal'},
  {k:'receita_obs',     icon:'📝', label:'Pode editar observações das receitas'}
];""",'permissões especiais de estoque')

html=replace_once(html,'function ir(id){',"""function ir(id){
  if(id==='estoque' && typeof renderEstoque==='function')renderEstoque();
  else if(id==='estoque-mov' && typeof renderEstoqueMovimentos==='function')renderEstoqueMovimentos();
  else if(id==='receita-completa' && typeof renderReceitaCompleta==='function')renderReceitaCompleta();
""",'ganchos de navegação')

old_save="const todos=LS.g('fdo_lotes',[]);todos.unshift(lote);LS.s('fdo_lotes',todos);return lote;"
new_save="const todos=LS.g('fdo_lotes',[]);todos.unshift(lote);LS.s('fdo_lotes',todos);registrarSaidaEstoqueLote(lote);return lote;"
html=replace_once(html,old_save,new_save,'baixa automática ao criar balde')

if not re.search(r"FB\.aoVoltarOnline=\(\)=>SYNC25\.online\(\);",html):
    fail('FB.aoVoltarOnline original não encontrado')
html=re.sub(r"FB\.aoVoltarOnline=\(\)=>SYNC25\.online\(\);","FB.aoVoltarOnline=()=>{SYNC25.online();if(typeof ESTOQUE_SYNC!=='undefined')ESTOQUE_SYNC.online();};",html,count=1)

boot=html.find('function bootApp(')
if boot<0: fail('bootApp não encontrado')
pos=html.find('migrarLotesAntigos();',boot)
if pos<0: fail('chamada migrarLotesAntigos não encontrada no boot')
end=pos+len('migrarLotesAntigos();')
html=html[:end]+' garantirPermissoesV260();'+html[end:]

html=html.replace("versao:'25.3'","versao:'26.0'",1)
exp=html.find('function exportarBackup')
if exp<0: fail('exportarBackup não encontrado')
km=re.search(r"const chaves=\[(.*?)\];",html[exp:],re.S)
if not km: fail('lista de chaves do backup não encontrada')
a=exp+km.start(1);b=exp+km.end(1);inside=html[a:b]
for key in ('fdo_estoque_movimentos','fdo_estoque_contagens','fdo_receitas_observacoes','fdo_estoque_outbox_v26','fdo_estoque_inicio_ts_v26'):
    if key not in inside: inside += ",'%s'"%key
html=html[:a]+inside+html[b:]

HTML.write_text(html,encoding='utf-8')

sw=SW.read_text(encoding='utf-8')
sw=replace_once(sw,"const CACHE='fdo-v25-3';","const CACHE='fdo-v26-0';",'cache do Service Worker')
SW.write_text(sw,encoding='utf-8')

valid=VALID.read_text(encoding='utf-8')
new_checks="""# v26.0 — consulta da receita completa + estoque separado da conferência física
for marker in (
    'atualização v26.0','id="s-receita-completa"','abrirReceitaCompleta(\'r1\')',
    'id="receita-full-obs"','id="s-estoque"','data-perm="estoque"',
    'fdo_v25/estoque/movimentos','fdo_v25/estoque/contagens',
    "'saida_receita_'+lote.id",'function garantirPermissoesV260()',
    "n==='wagner'","n==='maycon'","versao:'26.0'"
):
    if marker not in html: fail('v26.0 sem marcador: '+marker)
if html.count("abrirReceitaCompleta('r") < 5: fail('v26.0 sem consulta nas cinco receitas padrão')

"""
valid=replace_once(valid,'# v25.3 — Receita Teste rastreável, sem alterar R1–R5',new_checks+'# v25.3 — Receita Teste rastreável, sem alterar R1–R5','validação v26.0')
valid=valid.replace("if \"versao:'25.0'\" in html: fail('Backup ainda declara versão 25.0')","if \"versao:'25.0'\" in html or \"versao:'25.3'\" in html: fail('Backup declara versão antiga')",1)
valid=valid.replace("print('VALIDAÇÃO FDO OK')","print('VALIDAÇÃO FDO v26.0 OK')",1)
VALID.write_text(valid,encoding='utf-8')

wf=WORKFLOW.read_text(encoding='utf-8')
step="""      - name: Testar estoque e consulta de receita v26.0
        run: node tools/test_estoque_v26_0.js
"""
anchor="""      - name: Testar compatibilidade da Receita Teste v25.3
        run: node tools/test_compat_teste_v25_3.js
"""
wf=replace_once(wf,anchor,anchor+step,'workflow de validação')
WORKFLOW.write_text(wf,encoding='utf-8')
NEW_TEST.write_text(TEST,encoding='utf-8')
for temp in (ROOT/'tools'/'_v26_styles.css',ROOT/'tools'/'_v26_screens.html',ROOT/'tools'/'_v26_module.js'):
    try: temp.unlink()
    except FileNotFoundError: pass

try: SELF.unlink()
except FileNotFoundError: pass
try: SELF_WORKFLOW.unlink()
except FileNotFoundError: pass
print('PATCH v26.0 APLICADO')
