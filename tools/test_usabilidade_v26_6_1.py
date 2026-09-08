"""Testes reais de DOM e fluxo, isolados da nuvem e com dados inteiramente sintéticos.
Default: servidor local + localStorage real (CI). FDO_MEMORY_DOM=1: DOM em memória
para ambientes sem navegação; não equivale ao teste de instalação/Service Worker.
"""
from pathlib import Path
import os, json, re, shutil, threading, http.server, argparse, traceback
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('FDO_TEST_ARTIFACT_DIR','/tmp/fdo-usabilidade-tests'));OUT.mkdir(parents=True,exist_ok=True)
MEMORY=os.environ.get('FDO_MEMORY_DOM')=='1'
parser=argparse.ArgumentParser();parser.add_argument('--baseline');args=parser.parse_args()
SEED={
 'fdo_key':'TESTE_SEM_ACESSO_REAL','fdo_geo_ativo':False,'fdo_device_uid_v25':'teste-aparelho',
 'fdo_device_auth_v25':{'uid':'teste-aparelho','aprovado':True,'nome':'Teste isolado'},
 'fdo_migr_v248':True,'fdo_cfg_pin':'99881','fdo_pin_ativo':False,
 'fdo_farinha_lotes_atuais':{'bagatelle':'TESTE-BAG-01','italiana00':'TESTE-00-02'},
 'fdo_operadores':[{'id':'teste-op','nome':'Operador de teste','ativo':True,'pin':'8877','perms':{k:True for k in ['porcionamento','batimento','laminacao','modelagem','fermentacao','historico','calculadora','assistente','estoque','apagar','estoque_entrada','estoque_contagem','receita_obs','receita_editar']}}],
 'fdo_op_atual':'teste-op'
}
INIT_BASE="""Object.defineProperty(Navigator.prototype,'onLine',{get:()=>false,configurable:true});"""
class Quiet(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
 def log_message(self,*a):pass
server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Quiet);threading.Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/'
results=[];pages=[];errors=[]
def check(name,condition,detail=None):
 if not condition:
  for i,(_,page) in enumerate(pages):
   try:page.screenshot(path=str(OUT/('falha-'+str(i)+'.png')));OUT.joinpath('dom-'+str(i)+'.txt').write_text(page.locator('body').inner_text())
   except Exception:pass
  raise AssertionError(name+': '+repr(detail))
 results.append(name);print('OK',name,flush=True)
def memory_html(src,stored=None):
 values=stored if stored is not None else {k:json.dumps(v,ensure_ascii=False) for k,v in SEED.items()}
 pre=INIT_BASE+"""
 const __store=VALUES; const __session={};
 function __storage(d){return {getItem:k=>Object.prototype.hasOwnProperty.call(d,k)?d[k]:null,setItem:(k,v)=>{d[k]=String(v);},removeItem:k=>{delete d[k];},clear:()=>{Object.keys(d).forEach(k=>delete d[k]);},key:i=>Object.keys(d)[i]||null,get length(){return Object.keys(d).length;}};}
 Object.defineProperty(window,'localStorage',{value:__storage(__store),configurable:true});
 Object.defineProperty(window,'sessionStorage',{value:__storage(__session),configurable:true});
 """.replace('VALUES',json.dumps(values,ensure_ascii=False))
 def vendor(m):return '<script>'+ROOT.joinpath(m.group(1)).read_text().replace('</script','<\\/script')+'</script>'
 src=src.replace('<body>','<body><script>'+pre+'</script>',1)
 return re.sub(r'<script src="(vendor/[^"<>]+)"[^>]*></script>',vendor,src)
def new_page(browser,src=None,stored=None):
 ctx=browser.new_context(viewport={'width':390,'height':844},device_scale_factor=1,locale='pt-BR',timezone_id='America/Sao_Paulo',service_workers='block')
 ctx.route('**/*',lambda route: route.continue_() if route.request.url.startswith(URL) else route.abort())
 page=ctx.new_page();pages.append((ctx,page));page.set_default_timeout(4000)
 page.on('pageerror',lambda e:errors.append(str(e)))
 page.on('dialog',lambda d:d.accept() if d.type!='prompt' else d.accept(''))
 if MEMORY:page.set_content(memory_html(src or ROOT.joinpath('index.html').read_text(),stored),wait_until='domcontentloaded',timeout=10000)
 else:
  init=INIT_BASE+"""if(!localStorage.getItem('teste-seed')){const s=SEED;Object.entries(s).forEach(([k,v])=>localStorage.setItem(k,JSON.stringify(v)));localStorage.setItem('teste-seed','1');}""".replace('SEED',json.dumps(SEED,ensure_ascii=False))
  ctx.add_init_script(init)
  if src is not None:
   path=ROOT/'_test_baseline_usabilidade.html';path.write_text(src);page.goto(URL+path.name,wait_until='domcontentloaded');path.unlink()
  else:page.goto(URL+'index.html',wait_until='domcontentloaded')
 page.wait_for_function("DEVICE.bootLiberado===true && document.querySelector('.scr:not(.off)')?.id==='s-start'",timeout=15000)
 page.evaluate("FB.db=null; falar=()=>{}; falarForcado=()=>{}; iniciarVoz=()=>{}; pedirWakeLock=()=>{}; pararVoz=()=>{};")
 return page

def js(p,code):return p.evaluate(code)
def picture(p,name):
 p.evaluate("""()=>{let x=document.getElementById('teste-marca');if(!x){x=document.createElement('div');x.id='teste-marca';x.style='position:fixed;right:8px;bottom:4px;background:#222;color:#fff;padding:3px 7px;z-index:9000;font:11px Arial';x.textContent='DADOS DE TESTE';document.body.appendChild(x);}}""")
 p.screenshot(path=str(OUT/(name+'.png')),full_page=False)
def start_secos(p):
 js(p,"iniciarReceita('r4');st.farinhasLotes={bagatelle:{principal:document.getElementById('far-lote-bag').value,adicional:null},italiana00:{principal:document.getElementById('far-lote-ita').value,adicional:null}};iniciarSecos();for(let i=0;i<RECEITA.length;i++)st.done.add(i);irPasso(RECEITA.length-1);avancar();")
def authorize(p):
 js(p,"autorizarVariosBaldes();st.pinBuf='99881';verificarPin();")
def state(p):return js(p,"({screen:uxTelaAtual(),lotes:LS.g('fdo_lotes',[]).length,partidas:posPartidas().length,formas:posFormas().length})")
try:
 with sync_playwright() as pw:
  executable=shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
  browser=pw.chromium.launch(executable_path=executable,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'],timeout=15000)
  p=new_page(browser)
  check('Boot offline autorizado',state(p)['screen']=='start')
  if args.baseline:
   before=new_page(browser,Path(args.baseline).read_text())
   cfg="JSON.stringify({receitas:RECEITAS,fermento:TEMP_FERMENTO,opcoes:OPCOES_FERMENTO,produtos:POS_PRODUTOS})"
   check('Receitas, fermentos, tempos e produtos idênticos à base',js(before,cfg)==js(p,cfg))
  js(p,"iniciarReceita('r4')")
  rect=p.locator('#far-lotes-confirm-btn').bounding_box()
  check('Mesmos lotes cabe no alto sem rolagem',rect is not None and rect['y']+rect['height']<500,rect)
  check('Dois lotes visíveis para conferência','TESTE-BAG-01' in p.locator('#far-lotes-resumo').inner_text() and 'TESTE-00-02' in p.locator('#far-lotes-resumo').inner_text())
  picture(p,'01-lotes-no-alto')
  js(p,"document.getElementById('far-lote-bag').value='TESTE-NOVO';farResumoRapido()")
  check('Texto não chama lote alterado de mesmo lote','CONFIRMAR' in p.locator('#far-lotes-confirm-btn').inner_text())
  start_secos(p)
  js(p,"voltarPasso()")
  check('Voltar da confirmação retorna ao último ingrediente',js(p,"st.modo==='normal'&&st.step===RECEITA.length-1&&st.sessionStart>0"))
  js(p,"avancar();st.qtdBaldes=3;finalizarSecos()")
  check('Operador sem PIN administrativo não gera múltiplos',state(p)['lotes']==0)
  authorize(p);p.locator('#baldes-qtd').fill('3')
  picture(p,'02-finalizacao-administrativa')
  js(p,"Promise.all([finalizarSecos(),finalizarSecos()])")
  lotes=js(p,"LS.g('fdo_lotes',[])")
  check('Três baldes têm IDs e números distintos',len(lotes)==3 and len({l['id'] for l in lotes})==3 and len({l['num'] for l in lotes})==3,lotes)
  check('Múltiplos não inventam durações individuais',all(l['etapas']['porcionamento_secos']['dur'] is None and l['producaoConjunta']['total']==3 for l in lotes))
  check('Baixa individual no estoque',js(p,"LS.g('fdo_estoque_movimentos',[]).filter(x=>x.tipo==='saida_receita').length") ==3)
  js(p,"finalizarSecos()")
  check('Confirmação repetida após concluir não duplica',state(p)['lotes']==3)
  js(p,"abrirEtiquetasBaldes('balde');setEtqMassasQtd(2)")
  check('Seletor oferece 1 a 8',p.locator('#etq-qtds button').count()==8)
  check('Contagem distingue etiquetas e baldes','6 etiquetas' in p.locator('#etq-qtd-resumo').inner_text())
  payload=js(p,"""()=>{const enc=encodeEtiqueta,draw=desenharEtiqueta,ids=[];desenharEtiqueta=l=>{ids.push(l.id);return draw(l)};encodeEtiqueta=()=>new Uint8Array([1]);const b=etqPayloadSelecionado();encodeEtiqueta=enc;desenharEtiqueta=draw;return {ids,len:b.length};}""")
  check('Impressão em grupo percorre os baldes corretos',len(set(payload['ids']))==3 and payload['len']==3,payload)
  check('Reimpressão não cria baldes nem baixa extra',state(p)['lotes']==3 and js(p,"LS.g('fdo_estoque_movimentos',[]).filter(x=>x.tipo==='saida_receita').length")==3)
  js(p,"fecharEtiqueta();voltarTela()")
  check('Retorno de produção concluída não reabre a confirmação',state(p)['screen']=='porc-menu')
  # Failure after the second bucket record; restart resumes IDs and stock.
  q=new_page(browser);start_secos(q);authorize(q);q.locator('#baldes-qtd').fill('3')
  js(q,"""()=>{const original=registrarSaidaEstoqueLote;registrarSaidaEstoqueLote=l=>{if(l.num===2)throw new Error('FALHA SINTÉTICA');return original(l);};}""")
  js(q,"finalizarSecos()")
  check('Falha parcial deixa diário recuperável',js(q,"!!geracaoBaldesPendente()&&LS.g('fdo_lotes',[]).length===2"))
  initial_ids=js(q,"LS.g('fdo_lotes',[]).map(l=>l.id)")
  if MEMORY:
   saved=js(q,"Object.fromEntries(Array.from({length:localStorage.length},(_,i)=>{const k=localStorage.key(i);return [k,localStorage.getItem(k)]}))")
   q=new_page(browser,stored=saved)
  else:
   q.reload(wait_until='domcontentloaded');q.wait_for_function("DEVICE.bootLiberado===true && uxTelaAtual()==='start'",timeout=15000);js(q,"FB.db=null;falar=()=>{};falarForcado=()=>{};iniciarVoz=()=>{};pedirWakeLock=()=>{};pararVoz=()=>{};")
  js(q,"ir('porc-menu');retomarGeracaoBaldes()")
  check('Retomada de múltiplos pede nova autorização',state(q)['screen']=='pin')
  js(q,"st.pinBuf='99881';verificarPin()")
  q.wait_for_function("LS.g('fdo_baldes_pendentes_v2661',{}).concluido===true")
  final_ids=js(q,"LS.g('fdo_lotes',[]).map(l=>l.id)")
  check('Retomada conserva IDs e não duplica baldes',len(final_ids)==3 and set(initial_ids)<=set(final_ids))
  check('Retomada reconcilia estoque sem duplicar baixa',js(q,"LS.g('fdo_estoque_movimentos',[]).filter(x=>x.tipo==='saida_receita').length")==3)
  # First lamination + one legacy multi-part record, untouched.
  js(p,"""()=>{const ls=LS.g('fdo_lotes',[]);ls.forEach(l=>{l.etapas.batimento={feito:true,partes:4,emTs:Date.now()};});LS.s('fdo_lotes',ls);const t=Date.now()-86400000;LS.s('fdo_laminacoes',[{id:'lam-legada',nome:'ANTERIOR',receita:'r4',receitaNome:'Receita anterior',dataTs:t,totalPartes:4,composicao:[],etapas:{laminacao:{feito:true}}}]);abrirLaminacao();}""")
  picture(p,'03-laminacao-duas-etapas')
  js(p,"abrirPrimeiraLaminacao();lamAjustar(LS.g('fdo_lotes',[])[0].id,1);lamAjustar(LS.g('fdo_lotes',[])[0].id,1);lamAjustar(LS.g('fdo_lotes',[])[0].id,1)")
  check('Primeira etapa limita a seleção a duas massas',js(p,"lamTotalSel()") ==2)
  picture(p,'04-escolha-das-massas')
  js(p,"Promise.all([criarLaminacao(),criarLaminacao()])")
  check('Primeira etapa termina sem abrir corte',state(p)['screen']=='lam-concluida')
  check('Uma nova massa física e legado inalterado',js(p,"LS.g('fdo_laminacoes',[]).filter(x=>x.modeloFisico==='duas_massas_v1').length===1&&LS.g('fdo_laminacoes',[]).find(x=>x.id==='lam-legada').totalPartes===4&&!LS.g('fdo_laminacoes',[]).find(x=>x.id==='lam-legada').modeloFisico"))
  js(p,"abrirLaminacaoFinal()")
  check('Corte de dia anterior continua acessível','ANTERIOR' in p.locator('#lam-feitas-list').inner_text())
  picture(p,'05-massas-para-corte')
  js(p,"abrirCorteLaminacao(st.ultimaLamId);st.corteLinhas=[{produtoId:'croissant_115',qtd:'36'},{produtoId:'croissant_100',qtd:'40'}];renderCorteLaminacao()")
  picture(p,'06-corte-quantidade-real')
  js(p,"Promise.all([salvarCorteLaminacao(),salvarCorteLaminacao()])")
  check('Duplo toque no corte não duplica produtos',state(p)['partidas']==2)
  check('Múltiplos cortes offline têm sequências diferentes',js(p,"new Set(posPartidas().map(x=>x.seqDia)).size") ==2)
  check('Registrar corte não fabrica eventos de frio',js(p,"posPartidas().every(x=>x.situacao==='cortada'&&!x.eventos.freezerRapido)"))
  check('Corte parcial permanece pendente',js(p,"!corteConcluido(LS.g('fdo_laminacoes',[]).find(x=>x.id===st.ultimaLamId))"))
  picture(p,'07-fatia-proxima-acao')
  js(p,"abrirEtiquetaPartida(posPartidas()[0].id);setEtqMassasQtd(2)")
  check('Duas etiquetas grandes equivalem a oito menores','8 identificações menores' in p.locator('#etq-qtd-resumo').inner_text())
  picture(p,'08-etiquetas-quatro-faixas')
  p.locator('#etq-img').screenshot(path=str(OUT/'etiqueta-fatias-previa.png'))
  js(p,"fecharEtiqueta()")
  check('Etiqueta volta ao resultado exato do corte',state(p)['screen']=='corte-resultado')
  js(p,"concluirCorteLaminacao()")
  check('Só confirmação explícita conclui o corte',js(p,"corteConcluido(LS.g('fdo_laminacoes',[]).find(x=>x.id===st.ultimaLamId))"))
  # Cold sequence and cancellation.
  js(p,"st.testePartida=posPartidas()[0].id;posFreezerRapido(st.testePartida);posFreezerConservador(st.testePartida)")
  snapshot=js(p,"JSON.stringify(posPartidas().find(x=>x.id===st.testePartida))")
  js(p,"(()=>{const pr=window.prompt;window.prompt=()=>null;posIniciarDescongelamento(st.testePartida);window.prompt=pr;})()")
  check('Cancelar descongelamento não grava nem muda timestamp',snapshot==js(p,"JSON.stringify(posPartidas().find(x=>x.id===st.testePartida))"))
  js(p,"(()=>{const pr=window.prompt;window.prompt=()=>'';posIniciarDescongelamento(st.testePartida);window.prompt=pr;})()")
  check('Confirmar sem temperatura mantém dado ausente',js(p,"posPartidas().find(x=>x.id===st.testePartida).eventos.descongelamentoInicio.tempAmbiente===null"))
  js(p,"entrarModelagem();posFiltrar('modelagem')")
  picture(p,'09-conferencia-antes-modelagem')
  js(p,"posIniciarModelagem(st.testePartida)")
  check('Modelagem exige conferência do operador',js(p,"posPartidas().find(x=>x.id===st.testePartida).situacao==='modelagem'"))
  # Same product: only confirmed ready pieces may complement the selected source.
  js(p,"""()=>{let x=posPartidas().find(x=>x.id===st.testePartida);x.qtd=10;const clone=(id,estado,qtd)=>({...JSON.parse(JSON.stringify(x)),id,nome:id,situacao:estado,qtd,eventos:{}});posSalvarPartidas([x,clone('FRIO-NÃO-USAR','freezer_conservador',100),clone('DESCONGELANDO-NÃO-USAR','descongelando',100),clone('PRONTA','modelagem',8)]);st.testePedido=16;window.prompt=()=>String(st.testePedido);}""")
  js(p,"Promise.all([montarForma(st.testePartida),montarForma(st.testePartida)])")
  check('Forma não consome fatias no freezer ou não conferidas',js(p,"posFormas().length===1&&posFormas()[0].totalUnidades===16&&posFormas()[0].composicao.every(c=>!c.partidaId.includes('NÃO-USAR'))"))
  check('Saldo das duas origens corretas',js(p,"posSaldo(posPartidas().find(x=>x.id==='PRONTA'))===2&&posSaldo(posPartidas().find(x=>x.id==='FRIO-NÃO-USAR'))===100"))
  js(p,"posFiltrar('formas')");picture(p,'10-formas')
  # UI back is visible; busy and access screens cannot be bypassed.
  js(p,"abrirLaminacao();abrirPrimeiraLaminacao();st.criandoLam=true;voltarTela()")
  check('Voltar bloqueado durante gravação',state(p)['screen']=='laminacao')
  js(p,"st.criandoLam=false;voltarTela()")
  check('Voltar normal preserva seleção',state(p)['screen']=='lam-menu')
  js(p,"abrirPrimeiraLaminacao();history.back()")
  p.wait_for_timeout(150)
  check('Botão físico do navegador usa retorno seguro',state(p)['screen']=='lam-menu',state(p))
  js(p,"ir('login');voltarTela()")
  check('Retorno não contorna login',state(p)['screen']=='login')
  # Counts, single-bucket compatibility, permission reset and corrected cut retry.
  r=new_page(browser);start_secos(r)
  js(r,"st.qtdBaldes=0;finalizarSecos()")
  check('Quantidade zero rejeitada',state(r)['lotes']==0)
  js(r,"st.qtdBaldes=1.5;finalizarSecos()")
  check('Quantidade fracionária rejeitada',state(r)['lotes']==0)
  js(r,"st.qtdBaldes=1;finalizarSecos()")
  check('Operador comum gera um balde sem autorização extra',state(r)['lotes']==1)
  check('Balde simples preserva fotografia e tempo medido',js(r,"(()=>{const l=LS.g('fdo_lotes',[])[0];return !!l.receitaSnapshot&&l.etapas.porcionamento_secos.dur!==null&&!l.producaoConjunta&&!!l.etapas.porcionamento_secos.farinhas_lotes.bagatelle.principal;})()"))
  js(r,"abrirEtiqueta(st.ultimoLoteId);setEtqMassasQtd(8)")
  check('Oito etiquetas são aceitas e persistidas',js(r,"getEtqMassasQtd()") ==8)
  p.set_viewport_size({'width':360,'height':740})
  js(p,"LS.s('fdo_op_atual','teste-op');ir('start');abrirLaminacao();abrirPrimeiraLaminacao()")
  check('Tela estreita não transborda horizontalmente',js(p,"document.documentElement.scrollWidth<=360"))
  js(p,"abrirCorteLaminacao('lam-legada');st.corteLinhas=[{produtoId:'croissant_115',qtd:'36'}];renderCorteLaminacao();st._seqOriginal=FB.proxPosSeq;FB.proxPosSeq=async()=>{throw new Error('Falha sintética de reserva');};void 0")
  js(p,"salvarCorteLaminacao()")
  check('Falha de reserva não grava fatias novas',js(p,"posPartidasDaLam('lam-legada').length") ==0)
  js(p,"FB.proxPosSeq=st._seqOriginal;corteQtdMudou(0,'37');salvarCorteLaminacao()")
  check('Correção após falha usa a quantidade atualmente exibida',js(p,"posPartidasDaLam('lam-legada').length===1&&posPartidasDaLam('lam-legada')[0].qtd===37"))
  js(p,"abrirEtiquetaPartida(posPartidasDaLam('lam-legada')[0].id)")
  check('Botão de impressão mantém altura suficiente em tela pequena',js(p,"(()=>{const e=document.getElementById('etq-print-btn');return e.clientHeight>=e.scrollHeight;})()"))
  picture(p,'11-etiquetas-tela-estreita')
  check('Nenhum erro JavaScript não tratado',not errors,errors)
  browser.close()
 report={'resultado':'OK','modo':'DOM em memória' if MEMORY else 'navegador com origem local real','testes':results,'quantidade':len(results),'erros':errors,'impressoraFisica':'não testada','AndroidFisico':'não testado'}
 OUT.joinpath('resultado.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
 print('USABILIDADE v26.6.1 OK:',len(results),'verificações',flush=True)
except Exception:
 OUT.joinpath('falha.txt').write_text(traceback.format_exc()+'\nPAGE ERRORS\n'+repr(errors))
 for _,p in pages[-2:]:
  try:p.screenshot(path=str(OUT/'falha.png'))
  except Exception:pass
 raise
finally:server.shutdown()
