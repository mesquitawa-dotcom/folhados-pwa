"""Smoke do Ponto v26.9 com dados sintéticos; nunca acessa Firebase real."""
from pathlib import Path
import http.server,os,shutil,threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('FDO_TEST_ARTIFACT_DIR','/tmp/fdo-ponto-piloto'))
OUT.mkdir(parents=True,exist_ok=True)

class Quiet(http.server.SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass

server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Quiet)
threading.Thread(target=server.serve_forever,daemon=True).start()
base='http://127.0.0.1:'+str(server.server_port)+'/'
MOCK=r"""
window.firebase={apps:[],initializeApp(c){this.apps.push(c);}};
window.firebase.appCheck=function(){return{activate(){}}};
window.firebase.appCheck.ReCaptchaEnterpriseProvider=function(){};
window.firebase.auth=function(){return{
 setPersistence:async()=>{},
 onAuthStateChanged(fn){Promise.resolve().then(()=>fn({uid:window.FAKE_ROLE==='ger'?'gerente':'emp1'}));return()=>{}},
 signInAnonymously:async()=>({user:{uid:'emp1'}})
}};
window.firebase.auth.Auth={Persistence:{LOCAL:'local'}};
const DATA={
 'fdo_ponto_gerentes/emp1':null,
 'fdo_ponto_gerentes/gerente':{ativo:true},
 'fdo_ponto_vinculos/emp1':{funcionarioId:'jack',ativo:true},
 'fdo_ponto_colaboradores/jack':{nome:'Jacqueline',tipo:'mensalista',ativo:true},
 'fdo_ponto_colaboradores':{jack:{nome:'Jacqueline',tipo:'mensalista',ativo:true}},
 'fdo_ponto_financeiro':{jack:{'2026-01-01~v1':{tipo:'mensalista',centavos:230000}}},
 'fdo_ponto_config/area':{lat:-20.5294456,lng:-47.3940625,raio:150},
 '.info/serverTimeOffset':0
};
let seq=0;
window.firebase.database=function(){return{
 ref(path){return{
  once:async()=>({val:()=>DATA[path]??null}),
  push(value){const id='teste'+(++seq);if(value){DATA[path+'/'+id]={...value,servidorTs:Date.now()};return Promise.resolve()}
   return {key:id}},
  set:async value=>{DATA[path]={...value,servidorTs:Date.now()}},
  update:async value=>{DATA[path]={...(DATA[path]||{}),...value}}
 }}
}};
window.firebase.database.ServerValue={TIMESTAMP:{'.sv':'timestamp'}};
"""
errors=[]
try:
 with sync_playwright() as pw:
  exe=shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
  browser=pw.chromium.launch(executable_path=exe,headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  for role in ['emp','ger']:
   ctx=browser.new_context(viewport={'width':390,'height':844},locale='pt-BR',timezone_id='America/Sao_Paulo',service_workers='block')
   ctx.route('**/*',lambda r:r.fulfill(status=200,content_type='application/javascript',body='') if '/vendor/firebase-' in r.request.url else (r.continue_() if r.request.url.startswith(base) else r.abort()))
   ctx.add_init_script('window.FAKE_ROLE='+repr(role)+';'+MOCK)
   ctx.grant_permissions(['geolocation']);ctx.set_geolocation({'latitude':-20.5294456,'longitude':-47.3940625,'accuracy':15})
   p=ctx.new_page();p.on('pageerror',lambda e:errors.append(str(e)))
   p.goto(base+'ponto.html',wait_until='domcontentloaded')
   if role=='emp':
    p.locator('#funcionario').wait_for(state='visible',timeout=15000)
    assert p.locator('#nome-func').inner_text()=='Jacqueline'
    assert 'REGISTRAR ENTRADA' in p.locator('#principal').inner_text()
    p.screenshot(path=str(OUT/'ponto-funcionario.png'),full_page=True)
    p.locator('#principal').click()
    p.wait_for_function("document.querySelector('#principal').textContent.includes('SAÍDA')",timeout=15000)
    ctx.set_geolocation({'latitude':-20.49,'longitude':-47.35,'accuracy':15})
    p.locator('#principal').click()
    p.wait_for_function("document.querySelector('#feedback').textContent.includes('fora da fábrica')",timeout=15000)
   else:
    p.locator('#gerencia').wait_for(state='visible',timeout=15000)
    p.locator('#aba-cadastro').evaluate("(e)=>e.classList.remove('off')")
    assert p.locator('#emp-selecionado').locator('option').count()>1
    p.screenshot(path=str(OUT/'ponto-gerencia.png'),full_page=True)
   ctx.close()
  assert not errors,errors
  print('SMOKE PONTO v26.9 OK · entrada, saída externa pendente, cadastro gerencial e telas renderizadas')
  browser.close()
finally:server.shutdown()
