"""Testes reais de DOM e fluxo, isolados da nuvem e com dados inteiramente sintéticos.
Default: servidor local + localStorage real (CI). FDO_MEMORY_DOM=1: DOM em memória
para ambientes sem navegação; não equivale ao teste de instalação/Service Worker.
"""
from pathlib import Path
import os, json, re, shutil, threading, http.server, argparse, traceback
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('FDO_TEST_ARTIFACT_DIR','/tmp/fdo-fluxo-tests'));OUT.mkdir(parents=True,exist_ok=True)
MEMORY=os.environ.get('FDO_MEMORY_DOM')=='1'
parser=argparse.ArgumentParser();parser.add_argument('--baseline');args=parser.parse_args()
SEED={
 'fdo_key':'TESTE_SEM_ACESSO_REAL','fdo_geo_ativo':False,'fdo_device_uid_v25':'teste-aparelho',
 'fdo_device_auth_v25':{'uid':'teste-aparelho','aprovado':True,'nome':'Teste isolado'},
 'fdo_migr_v248':True,'fdo_cfg_pin':'99881','fdo_pin_ativo':False,
 'fdo_farinha_lotes_atuais':{'bagatelle':'TESTE-BAG-01','italiana00':'TESTE-00-02'},
 'fdo_operadores':[{'id':'teste-op','nome':'Operador de teste','ativo':True,'pin':'8877','perms':{k:True for k in ['porcionamento','batimento','laminacao','modelagem','fermentacao','historico','calculadora','assistente','estoque','forneamento','apagar','estoque_entrada','estoque_contagem','receita_obs','receita_editar']}}],
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
  check('Boot e permissão de Forneamento',js(p,"uxTelaAtual()==='start'&&OP.pode('forneamento')"))
  if args.baseline:
   before=new_page(browser,Path(args.baseline).read_text())
   cfg="JSON.stringify({receitas:RECEITAS,fermento:TEMP_FERMENTO,opcoes:OPCOES_FERMENTO,produtos:POS_PRODUTOS})"
   check('Receitas, tempos, pesos, fermentos e produtos sem alteração',js(p,cfg)==js(before,cfg))
  # Dados sintéticos: 8 é a divisão efetivamente registrada APENAS neste teste.
  js(p,"""()=>{const t=Date.now()-7200000;const bucket=(id,num)=>({id,num,receita:'r4',receitaNome:RECEITAS.r4.nome,criadoTs:t,etapas:{batimento:{feito:true,partes:8,emTs:t},fermentacao:{feito:true,emTs:t-1000,tempMin:24}}});LS.s('fdo_lotes',[bucket('b1',101),bucket('b2',102)]);const lam=(id,n,composicao)=>({id,nome:'TESTE L'+n,dataTs:t+1000,receita:'r4',receitaNome:RECEITAS.r4.nome,totalPartes:2,modeloFisico:'duas_massas_v1',massasComManteiga:1,composicao,etapas:{laminacao:{feito:true,emTs:t+1000},corte:{feito:true,emTs:t+2000}},corteEventos:[{feito:true,emTs:t+2000}]});LS.s('fdo_laminacoes',[lam('l1',1,[{loteId:'b1',loteNum:101,partes:2}]),lam('l2',2,[{loteId:'b1',loteNum:101,partes:1},{loteId:'b2',loteNum:102,partes:1}]),{id:'l-legado',nome:'LEGADO',totalPartes:4,dataTs:t-1000,composicao:[]}]);const part=(id,lam,qtd)=>({id,nome:id,laminacaoId:lam,laminacaoNome:'TESTE L'+lam.slice(1),produtoId:'croissant_115',produtoNome:'Croissant teste',qtd,criadoTs:t+2000,situacao:'modelagem',eventos:{modelagemInicio:{emTs:t+3000}},capacidadeForma:16});posSalvarPartidas([part('p1','l1',36),part('p2','l2',4)]);window.prompt=()=>String(st.testQty||16);window.confirm=()=>true;window.alert=t=>{st.lastAlert=t;};} """)
  js(p,"montarForma('p1')");js(p,"montarForma('p1')");js(p,"st.testQty=8;montarForma('p1')")
  check('Modelagem real cria 16 + 16 + 8, sem alterar rendimento',js(p,"posFormas().length===3&&posFormas().reduce((s,f)=>s+f.totalUnidades,0)===40&&posPartidas().every(p=>posSaldo(p)===0)"))
  check('Forma com sobras mantém duas origens',js(p,"posFormas().find(f=>f.totalUnidades===8).composicao.length===2"))
  js(p,"abrirFluxo('laminacoes')")
  check('Histórico lista massas e distingue o registro legado','Massa laminada TESTE L1' in p.locator('#fluxo-lista').inner_text() and 'registro anterior' in p.locator('#fluxo-lista').inner_text())
  picture(p,'01-historico-massas')
  js(p,"abrirRastreio('formas',posFormas().find(f=>f.totalUnidades===8).id)")
  text=p.locator('#rastreio-conteudo').inner_text()
  check('Rastreio chega aos dois baldes através das junções','junção' in text and '#101' in text and '#102' in text and 'p1' in text and 'p2' in text,text)
  picture(p,'02-origens-forma')
  js(p,"abrirRastreio('laminacoes','l1');voltarTela()")
  check('Voltar no rastreio retorna à forma anterior, não sai do histórico',js(p,"st.rastro.tipo==='formas'&&fluxoRegistro('formas',st.rastro.id,fluxoDados()).totalUnidades===8&&uxTelaAtual()==='rastreio'"))
  js(p,"abrirRastreio('baldes','b1')")
  check('Balde mostra saldo real de 5 massas após consumir 3', '8 massas registradas · 5 disponíveis' in p.locator('#rastreio-conteudo').inner_text())
  check('Desmembramento liga balde às duas massas laminadas', 'desmembramento' in p.locator('#rastreio-conteudo').inner_text() and js(p,"fluxoFilhos('baldes',fluxoDados().baldes[0],fluxoDados()).length===2"))
  check('Fermentação antiga mantida e explicitamente legada','Fermentação antiga vinculada ao balde' in p.locator('#rastreio-conteudo').inner_text())
  js(p,"abrirRastreio('laminacoes','l1')")
  check('Corte não aparece duplicado na linha do tempo',p.locator('#rastreio-conteudo').inner_text().count('Corte concluído')==2) # status + um evento
  js(p,"abrirFluxo('fatias');fluxoBuscar('p2')")
  check('Busca reduz às fatias desejadas', 'p2' in p.locator('#fluxo-lista').inner_text() and 'Fatias p1' not in p.locator('#fluxo-lista').inner_text())
  js(p,"abrirFermentacaoLotes()")
  check('Fermentação seleciona três formas, não dois baldes',p.locator('#ferm-lotes-list input[type=checkbox]').count()==3 and 'Balde' not in p.locator('#ferm-lotes-list').inner_text())
  check('Nenhuma etapa inicia por visitar a tela',js(p,"posFormas().every(f=>!f.eventos)&&!st.movendoFormas"))
  p.locator('#ferm-armario').fill('7');p.locator('#ferm-armario').dispatch_event('input')
  js(p,"fermArmarioMudou('7');fermSelecionarProntas();fermRevisarSelecao()")
  check('Revisão inicia com confirmação desmarcada',p.locator('#mov-formas-confirmar').is_disabled())
  p.locator('#mov-formas-conferido').check()
  js(p,"confirmarMovimentoFormas()")
  check('Offline não grava nem finge confirmação', 'Nenhuma etapa foi registrada' in p.locator('#mov-formas-status').inner_text() and js(p,"posFormas().every(f=>!f.eventos)"))
  # Transporte simulado: o núcleo de transação é real e será exercitado também no Emulator.
  js(p,"""()=>{st.baseBaldes=localStorage.getItem('fdo_lotes');st.remote=SYNC25.map(posFormas());st.transactions=0;SYNC25.flush=async()=>{};SYNC25.saveOut({fdo_lotes:{},fdo_laminacoes:{},fdo_partidas:{},fdo_formas:{}});SYNC25.ready.fdo_formas=true;SYNC25.raw.fdo_formas=clonarReceita(st.remote);Object.entries(st.remote).forEach(([k,v])=>SYNC25.itemJson.fdo_formas[k]=JSON.stringify(v));Object.defineProperty(Navigator.prototype,'onLine',{get:()=>true,configurable:true});FB.db={ref:path=>{if(path!=='fdo_v25/formas')throw Error('Caminho não previsto '+path);return {once:async()=>({val:()=>clonarReceita(st.remote)}),transaction:async(fn,callback,local)=>{if(local!==false)throw Error('Aplicação local prematura');st.transactions++;await new Promise(r=>setTimeout(r,5));const result=fn(clonarReceita(st.remote));if(result!==undefined)st.remote=result;return {committed:result!==undefined,snapshot:{val:()=>clonarReceita(st.remote)}};}};}};}""")
  js(p,"(async()=>{const op=confirmarMovimentoFormas();voltarTela();st.retornoBloqueado=uxTelaAtual()==='fermentacao';await Promise.all([op,confirmarMovimentoFormas()]);})()")
  check('Retorno é bloqueado durante gravação',js(p,'st.retornoBloqueado'))
  check('Duplo toque registra somente uma transação',js(p,"st.transactions===1&&fluxoOcupacao(7)===3&&uxTelaAtual()==='fermentacao-lotes'"))
  check('Formas guardam armário e operador reais do teste',js(p,"posFormas().every(f=>f.eventos.entradaArmario.armario===7&&f.eventos.entradaArmario.operadorId==='teste-op')"))
  js(p,"fermSelecionarArmario(7)");picture(p,'03-armario-em-fermentacao')
  js(p,"fermRevisarSelecao()")
  check('Temperaturas são vazias, não presumidas',p.locator('#ferm-temp-min').input_value()=='' and p.locator('#ferm-temp-max').input_value()=='')
  p.locator('#mov-formas-conferido').check();js(p,"confirmarMovimentoFormas()")
  check('Saída libera armário e deixa formas pré-selecionadas para assar',js(p,"fluxoOcupacao(7)===0&&uxTelaAtual()==='forneamento'&&fornoSelecionadas().length===3&&posFormas().every(f=>fluxoEstadoForma(f)==='aguardando_assamento')"))
  picture(p,'04-proximo-passo-assamento')
  js(p,"fornoRevisarSelecao()")
  check('Assamento não inicia sem confirmação física',js(p,"confirmarMovimentoFormas();posFormas().every(f=>!f.eventos.assamentoInicio)"))
  p.locator('#mov-formas-conferido').check();js(p,"confirmarMovimentoFormas()")
  check('Início de assamento aparece separado do fim',js(p,"fluxoFormasEstado('assando').length===3&&fluxoFormasEstado('assada').length===0"))
  js(p,"fornoSelecionarTodas();fornoRevisarSelecao()")
  p.locator('#mov-formas-conferido').check();js(p,"confirmarMovimentoFormas()")
  check('Concluir assamento mantém as mesmas três formas e 40 unidades',js(p,"fluxoFormasEstado('assada').length===3&&posFormas().length===3&&posFormas().reduce((s,f)=>s+f.totalUnidades,0)===40"))
  check('Revisões concluídas não reaparecem ao voltar',js(p,"!UX_NAV.pilha.includes('fermentacao')"))
  check('Processo não altera um byte dos baldes antigos',js(p,"st.baseBaldes===localStorage.getItem('fdo_lotes')"))
  js(p,"apagarForma(posFormas()[0].id)")
  check('Excluir forma avançada é bloqueado sem devolver as fatias',js(p,"posFormas().length===3&&posPartidas().every(p=>posSaldo(p)===0)&&st.lastAlert.includes('preservados')"))
  js(p,"FB.db=null;Object.defineProperty(Navigator.prototype,'onLine',{get:()=>false,configurable:true});abrirRastreio('formas',posFormas()[0].id)")
  check('Consulta offline mantém os quatro eventos e durações','Início do assamento' in p.locator('#rastreio-conteudo').inner_text() and 'Fermentação:' in p.locator('#rastreio-conteudo').inner_text())
  picture(p,'05-historico-apos-assamento')
  # Reabertura em outro contexto de navegador com cópia do armazenamento.
  stored=js(p,"Object.fromEntries(Array.from({length:localStorage.length},(_,i)=>localStorage.key(i)).map(k=>[k,localStorage.getItem(k)]))")
  if MEMORY:
   q=new_page(browser,stored=stored)
  else:
   q=p;js(q,"Object.defineProperty(Navigator.prototype,'onLine',{get:()=>false,configurable:true})");q.reload(wait_until='domcontentloaded');q.wait_for_function('DEVICE.bootLiberado===true');js(q,'FB.db=null;falar=()=>{};')
  check('Reabrir aplicativo não reinicia nem apaga horários',js(q,"fluxoFormasEstado('assada').length===3"))
  js(q,"abrirFluxo()")
  check('Painel diferencia assado de embalado/expedido','não significa produto embalado' in q.locator('#fluxo-lista').inner_text())
  picture(q,'06-painel-estagios')
  js(q,"abrirRastreio('formas','nao-existe')")
  check('Origem ausente é sinalizada, não inventada','não está disponível neste aparelho' in q.locator('#rastreio-conteudo').inner_text())
  # A nova permissão só é herdada quando ausente; recusa explícita permanece.
  js(q,"""()=>{let ops=LS.g('fdo_operadores',[]);ops[0].perms.forneamento=false;LS.s('fdo_operadores',ops);garantirPermissoesV260();} """)
  check('Permissão de Forneamento negada não é reativada na migração',js(q,"!OP.pode('forneamento')"))
  js(q,"""()=>{let ops=LS.g('fdo_operadores',[]);delete ops[0].perms.forneamento;LS.s('fdo_operadores',ops);garantirPermissoesV260();} """)
  check('Permissão ausente herda Fermentação',js(q,"OP.pode('forneamento')"))
  # Provas geométricas de telas e fontes ampliadas.
  for w,h,font in [(360,640,22),(390,844,22),(320,640,22),(360,640,30),(390,844,30),(320,640,30),(360,700,36),(390,844,36),(320,640,36)]:
   q.set_viewport_size({'width':w,'height':h});js(q,f"document.documentElement.style.fontSize='{font}px'")
   for route,button in [("abrirFluxo()",None),("abrirFermentacaoLotes()",'#ferm-avancar'),("abrirRevisaoFormas('saidaArmario',[posFormas()[0].id])",'#mov-formas-confirmar'),("entrarForneamento()",'#forno-avancar'),("abrirRastreio('formas',posFormas()[0].id)",None)]:
    js(q,route)
    geom=js(q,"""()=>{const el=document.querySelector('.scr:not(.off)');const back=el.querySelector('.ux-backbar');return {scroll:el.scrollWidth,width:el.clientWidth,screen:el.id,back:!!back&&back.getBoundingClientRect().bottom>0};}""")
    check(f'Sem estouro lateral {w}x{h}/{font} {geom["screen"]}',geom['scroll']<=w+1,geom)
    check(f'Voltar visível {w}/{font} {geom["screen"]}',geom['back'],geom)
    if button:
     rect=q.locator(button).bounding_box()
     check(f'Ação fixa acessível {w}x{h}/{font} {geom["screen"]}',rect and rect['y']>=0 and rect['y']+rect['height']<=h+1,rect)
  check('Sem exceções JavaScript no navegador',not errors,errors)
  for ctx,page in pages:ctx.close()
  browser.close()
 print('TESTE NAVEGADOR FLUXO v26.7 OK —',len(results),'verificações')
 OUT.joinpath('resultado-fluxo.json').write_text(json.dumps({'ok':True,'quantidade':len(results),'verificacoes':results,'modo':'memoria' if MEMORY else 'origem-real'},ensure_ascii=False,indent=2))
except Exception:
 OUT.joinpath('erro.txt').write_text(traceback.format_exc());raise
finally:server.shutdown()
