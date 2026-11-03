"""Etiqueta v26.8.1: identificação do reaproveitamento e legibilidade do balde.
Dados sintéticos locais; sem acesso a Firebase/produção.
"""
from pathlib import Path
import base64, http.server, json, os, re, shutil, threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('FDO_TEST_ARTIFACT_DIR','/tmp/fdo-etiquetas-v26-8-1'))
OUT.mkdir(parents=True,exist_ok=True)
SEED={
 'fdo_key':'TESTE_SEM_ACESSO_REAL','fdo_geo_ativo':False,
 'fdo_device_uid_v25':'teste-aparelho',
 'fdo_device_auth_v25':{'uid':'teste-aparelho','aprovado':True,'nome':'Teste'},
 'fdo_migr_v248':True,'fdo_pin_ativo':False,
 'fdo_operadores':[{'id':'teste-op','nome':'Operador de teste','ativo':True,'pin':'8877',
   'perms':{k:True for k in ['porcionamento','historico','calculadora']}}],
 'fdo_op_atual':'teste-op'
}
INIT="Object.defineProperty(Navigator.prototype,'onLine',{get:()=>false,configurable:true});"
checks=[];errors=[]

def check(nome,valor,detail=None):
    if not valor: raise AssertionError(nome+(': '+repr(detail) if detail is not None else ''))
    checks.append(nome);print('OK',nome,flush=True)

def px(font):
    m=re.search(r'(\d+)px',font or '')
    return int(m.group(1)) if m else 0

def save_data_url(data_url,name):
    raw=data_url.split(',',1)[1]
    (OUT/name).write_bytes(base64.b64decode(raw))

class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**kw):super().__init__(*a,directory=str(ROOT),**kw)
    def log_message(self,*a):pass

server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Quiet)
threading.Thread(target=server.serve_forever,daemon=True).start()
URL=f'http://127.0.0.1:{server.server_port}/'

try:
  with sync_playwright() as pw:
    exe=shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
    browser=pw.chromium.launch(executable_path=exe,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
    ctx=browser.new_context(viewport={'width':390,'height':844},locale='pt-BR',timezone_id='America/Sao_Paulo',service_workers='block')
    ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith(URL) else r.abort())
    ctx.add_init_script(INIT+'const seed='+json.dumps(SEED)+';Object.entries(seed).forEach(([k,v])=>localStorage.setItem(k,JSON.stringify(v)));')
    p=ctx.new_page();p.set_default_timeout(5000);p.on('pageerror',lambda e:errors.append(str(e)))
    p.on('dialog',lambda d:d.accept('') if d.type=='prompt' else d.accept())
    p.goto(URL+'index.html',wait_until='domcontentloaded')
    p.wait_for_function("DEVICE.bootLiberado===true && uxTelaAtual()==='start'",timeout=15000)
    p.evaluate("FB.db=null;falar=()=>{};falarForcado=()=>{};iniciarVoz=()=>{};pararVoz=()=>{};pedirWakeLock=()=>{};")

    result=p.evaluate("""()=>{
      const v=aprovCalcularR2(650);
      const r=montarReceita(
        {nome:'Receita 2 - MASSA 3 KG',rotulo:'R2',farinhas:'Bagatelle '+v.bag+' g, Italiana '+v.ita+' g'},
        v.bag,v.feu,v.ita,{agua:v.agua,acucar:v.acucar,leite:v.leite,sal:v.sal,manteiga:v.manteiga,aprov:v.aprov,fermento:46}
      );
      r.aproveitamentoExecucao={versao:1,perfil:'r2_massa_manteiga_v1',tipo:'massa_laminada_com_manteiga',padrao_g:3000,usado_g:650,balancaPasso_g:2,ajustado:true};
      const lote={id:'teste-etq',num:27,receita:'r2',receitaNome:'Receita 2 - MASSA 3 KG',rotulo:'R2',
        criadoTs:new Date('2026-11-03T20:00:00-03:00').getTime(),receitaSnapshot:r,
        etapas:{porcionamento_secos:{feito:true,temp:20,fermento_g:46,fermento_horas:14,
          aproveitamento:{versao:1,padrao_g:3000,usado_g:650}}}};
      const proto=CanvasRenderingContext2D.prototype,orig=proto.fillText,calls=[];
      proto.fillText=function(t,x,y,...rest){calls.push({text:String(t),x,y,font:this.font,align:this.textAlign});return orig.call(this,t,x,y,...rest);};
      const massas=desenharEtiquetaMassas(lote),massasCalls=calls.splice(0,calls.length);
      const balde=desenharEtiqueta(lote),baldeCalls=calls.splice(0,calls.length);
      proto.fillText=orig;
      const legado=JSON.parse(JSON.stringify(lote));delete legado.etapas.porcionamento_secos.aproveitamento;delete legado.receitaSnapshot.aproveitamentoExecucao;
      legado.receitaSnapshot.passos.find(x=>x.nome==='Massa laminada').g=3000;
      const fallback=loteAproveitamentoEtiqueta(legado);
      const outra=JSON.parse(JSON.stringify(lote));outra.receita='r3';outra.rotulo='R3';delete outra.etapas.porcionamento_secos.aproveitamento;delete outra.receitaSnapshot.aproveitamentoExecucao;
      return {v,massasCalls,baldeCalls,massas:massas.toDataURL('image/png'),balde:balde.toDataURL('image/png'),
        aproveitamento:loteAproveitamentoEtiqueta(lote),fallback,outra:loteAproveitamentoEtiqueta(outra)};
    }""")

    check('R2 variável lê exatamente 650 g do snapshot',result['aproveitamento']==650,result['aproveitamento'])
    check('R2 legado pode recuperar 3.000 g da massa laminada',result['fallback']==3000,result['fallback'])
    check('Outra receita sem metadado não recebe reaproveitamento inventado',result['outra'] is None,result['outra'])

    mc=result['massasCalls']
    rec=[c for c in mc if c['text']=='Receita 2']
    reap=[c for c in mc if c['text']=='650 g']
    check('Etiqueta das massas imprime Receita 2 nas quatro faixas',len(rec)==4,len(rec))
    check('Etiqueta das massas imprime 650 g nas quatro faixas',len(reap)==4,len(reap))
    check('Nome ocupa a metade esquerda',all(105<=c['x']<=135 and c['align']=='center' for c in rec),rec)
    check('650 g ocupa a metade direita',all(345<=c['x']<=375 and c['align']=='center' for c in reap),reap)
    check('Primeira linha não repete MASSA 3 KG',not any('MASSA 3 KG' in c['text'] for c in mc))
    check('Data, temperatura e 14 horas permanecem na segunda linha',sum('20°C' in c['text'] and '14 horas' in c['text'] for c in mc)==4)

    bc=result['baldeCalls']
    def call(text):
      return next((c for c in bc if c['text']==text),None)
    agua=call('Água/gelo');leite=call('Leite em pó');massa=call('Massa laminada')
    check('Balde destaca Água/gelo',agua is not None and px(agua['font'])>=24,agua)
    check('Balde destaca Leite em pó',leite is not None and px(leite['font'])>=24,leite)
    check('Balde destaca Massa laminada',massa is not None and px(massa['font'])>=24,massa)
    check('Três linhas principais ficam separadas verticalmente',
      agua and leite and massa and [agua['y'],leite['y'],massa['y']]==[192,252,312],[agua,leite,massa])
    valores=[c for c in bc if c['align']=='right' and c['x']>=440 and c['y'] in (192,252,312)]
    check('Valores principais ficam maiores e alinhados à direita',
      len(valores)==3 and all(px(c['font'])>=30 for c in valores),valores)
    check('Massa laminada do balde mostra 650 g',any(c['text']=='650 g' and c['align']=='right' and c['y']==312 for c in bc))
    check('Cabeçalho do balde deixa de chamar a execução de MASSA 3 KG',not any('MASSA 3 KG' in c['text'] for c in bc))
    check('Temperatura e 14 horas permanecem visíveis',any('20ºC' in c['text'] and '14 horas' in c['text'] for c in bc))
    check('Nenhum erro JavaScript não tratado',not errors,errors)

    save_data_url(result['massas'],'etiqueta-massas-650g.png')
    save_data_url(result['balde'],'etiqueta-balde-650g.png')
    browser.close()
    (OUT/'resultado.json').write_text(json.dumps({'ok':True,'checks':checks,'massasCalls':mc,'baldeCalls':bc},ensure_ascii=False,indent=2))
    print('ETIQUETAS v26.8.1 OK:',len(checks),'verificações')
finally:
  server.shutdown()
