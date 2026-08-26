from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'index.html'
TEST = ROOT / 'tools' / 'test_estoque_v26_0.js'
SELF = ROOT / 'tools' / 'patch_review_v26_0.py'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: esperado 1 marcador, encontrado {count}')
    return text.replace(old, new, 1)


html = HTML.read_text(encoding='utf-8')

html = replace_once(
    html,
    ".est-cont-field{display:grid;grid-template-columns:1fr 7.5rem auto;align-items:center;gap:.5rem;background:var(--bg3);border:1px solid var(--brd);border-radius:.48rem;padding:.55rem .65rem;margin-bottom:.45rem}",
    ".est-cont-field{display:grid;grid-template-columns:minmax(0,1fr) 7rem 3.8rem;align-items:center;gap:.5rem;background:var(--bg3);border:1px solid var(--brd);border-radius:.48rem;padding:.55rem .65rem;margin-bottom:.45rem}",
    'grade da conferência',
)
html = replace_once(
    html,
    "@media(max-width:430px){.rec-full-fer{grid-template-columns:1fr}.rec-full-fer b{grid-column:1}.est-cont-field{grid-template-columns:1fr 6.6rem auto}.est-actions{grid-template-columns:1fr}}",
    "@media(max-width:430px){.rec-full-fer{grid-template-columns:1fr}.rec-full-fer b{grid-column:1}.est-cont-field{grid-template-columns:minmax(0,1fr) 5.6rem}.est-cont-field small{grid-column:2;text-align:right}.est-actions{grid-template-columns:1fr}}",
    'layout móvel da conferência',
)

html = replace_once(
    html,
    "    if(this.pending()&&navigator.onLine){setTimeout(()=>this.flush(),0);return;}\n    FB.status(ok?'ok':'err',ok?'✓ Sincronizado':'⚠ Estoque salvo aqui · nuvem pendente');",
    "    if(this.pending()&&navigator.onLine){\n      if(!ok)FB.status('err','⚠ Estoque salvo aqui · nuvem pendente');\n      setTimeout(()=>this.flush(),ok?150:5000);return;\n    }\n    FB.status(ok?'ok':'err',ok?'✓ Sincronizado':'⚠ Estoque salvo aqui · nuvem pendente');",
    'intervalo de retentativa da sincronização',
)

old_reconcile = """function estoqueReconciliarSaidasLotes(){
  const inicio=Number(ESTOQUE_SYNC.inicioTs||LS.g('fdo_estoque_inicio_ts_v26',0))||0;if(!inicio)return;
  let n=0;LS.g('fdo_lotes',[]).forEach(l=>{if(l&&Number(l.criadoTs)>=inicio&&registrarSaidaEstoqueLote(l))n++;});return n;
}"""
new_reconcile = """let estoqueReconciliando=false;
function estoqueReconciliarSaidasLotes(){
  if(estoqueReconciliando)return 0;
  const inicio=Number(ESTOQUE_SYNC.inicioTs||LS.g('fdo_estoque_inicio_ts_v26',0))||0;if(!inicio)return 0;
  estoqueReconciliando=true;
  try{
    let n=0;LS.g('fdo_lotes',[]).forEach(l=>{if(l&&Number(l.criadoTs)>=inicio&&registrarSaidaEstoqueLote(l))n++;});return n;
  }finally{estoqueReconciliando=false;}
}"""
html = replace_once(html, old_reconcile, new_reconcile, 'proteção contra reentrada da reconciliação')

old_dates = """function estoqueUltimaContagem(){return estoqueContagens().slice().sort((a,b)=>(Number(b.emTs)||0)-(Number(a.emTs)||0))[0]||null;}
function estoqueDataCurta(ts){return ts?new Date(ts).toLocaleDateString('pt-BR'):'—';}"""
new_dates = """function estoqueUltimaContagem(){return estoqueContagens().slice().sort((a,b)=>(Number(b.emTs)||0)-(Number(a.emTs)||0))[0]||null;}
function estoqueDataCurta(ts){return ts?new Date(ts).toLocaleDateString('pt-BR'):'—';}
function estoqueHojeISO(){const d=new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');}
function estoqueDataISO(iso){
  if(!/^\\d{4}-\\d{2}-\\d{2}$/.test(String(iso||'')))return '';
  const [a,m,d]=String(iso).split('-').map(Number);return new Date(a,m-1,d).toLocaleDateString('pt-BR');
}"""
html = replace_once(html, old_dates, new_dates, 'funções de data local')

html = replace_once(
    html,
    "  const info=document.getElementById('estoque-ultima');if(info)info.textContent=cont?('Última conferência: '+estoqueDataCurta(cont.emTs)+' · '+(cont.op||'—')):'Ainda não há conferência física semanal.';",
    "  const info=document.getElementById('estoque-ultima');if(info)info.textContent=cont?('Conferência de '+(estoqueDataISO(cont.data)||estoqueDataCurta(cont.emTs))+' · '+(cont.op||'—')):'Ainda não há conferência física semanal.';",
    'data exibida da conferência',
)
html = replace_once(
    html,
    "  const hoje=new Date(),d=document.getElementById('estoque-cont-data');d.value=hoje.toISOString().slice(0,10);",
    "  const d=document.getElementById('estoque-cont-data');d.value=estoqueHojeISO();",
    'data inicial local da conferência',
)

old_liberar = """  liberar(comNuvem){
    if(comNuvem){
      if(!this.cloudStarted){this.cloudStarted=true;SYNC25.init();if(typeof ESTOQUE_SYNC!=='undefined')ESTOQUE_SYNC.init();}
      else if(SYNC25.iniciado)FB.aoVoltarOnline();
    }
    if(this.bootLiberado)return;this.bootLiberado=true;const cb=this.bootCb;if(typeof cb==='function')cb();
  },"""
new_liberar = """  liberar(comNuvem){
    if(comNuvem){
      if(!this.cloudStarted){this.cloudStarted=true;SYNC25.init();if(typeof ESTOQUE_SYNC!=='undefined')ESTOQUE_SYNC.init();}
      else if(SYNC25.iniciado)FB.aoVoltarOnline();
    }else if(typeof ESTOQUE_SYNC!=='undefined'){
      ESTOQUE_SYNC.garantirInicio();
    }
    if(this.bootLiberado)return;this.bootLiberado=true;const cb=this.bootCb;if(typeof cb==='function')cb();
  },"""
html = replace_once(html, old_liberar, new_liberar, 'início offline do estoque')

HTML.write_text(html, encoding='utf-8')

test = TEST.read_text(encoding='utf-8')
anchor = "ok(html.includes(\"n==='wagner'\")&&html.includes(\"n==='maycon'\"),'migração de permissões Wagner/Maycon ausente');\n"
checks = """ok(html.includes('let estoqueReconciliando=false'),'proteção contra reentrada da reconciliação ausente');
ok(html.includes('ok?150:5000'),'retentativa do estoque sem intervalo de segurança');
ok(html.includes('function estoqueHojeISO()'),'data local da conferência semanal ausente');
ok(html.includes("else if(typeof ESTOQUE_SYNC!=='undefined')"),'início offline do estoque ausente');
ok(html.includes('grid-template-columns:minmax(0,1fr) 5.6rem'),'layout móvel da conferência não protegido');
ok(html.includes("estoqueDataISO(cont.data)||estoqueDataCurta(cont.emTs)"),'data selecionada da conferência não é exibida');
"""
test = replace_once(test, anchor, anchor + checks, 'testes de robustez v26.0')
TEST.write_text(test, encoding='utf-8')

try:
    SELF.unlink()
except FileNotFoundError:
    pass

print('REVISÃO DE ROBUSTEZ v26.0 APLICADA')
