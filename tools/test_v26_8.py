"""Fluxo real v26.8: R2 com massa reaproveitada variável e navegação sem ciclo.
Dados sintéticos locais; não acessa Firebase/produção.
"""
from pathlib import Path
import http.server, json, os, shutil, threading
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]
OUT=Path(os.environ.get('FDO_TEST_ARTIFACT_DIR','/tmp/fdo-v26-8-tests'))
OUT.mkdir(parents=True,exist_ok=True)
SEED={
 'fdo_key':'TESTE_SEM_ACESSO_REAL','fdo_geo_ativo':False,
 'fdo_device_uid_v25':'teste-aparelho',
 'fdo_device_auth_v25':{'uid':'teste-aparelho','aprovado':True,'nome':'Teste'},
 'fdo_migr_v248':True,'fdo_pin_ativo':False,
 'fdo_farinha_lotes_atuais':{'bagatelle':'TESTE-BAG','italiana00':'TESTE-00'},
 'fdo_operadores':[{'id':'teste-op','nome':'Operador de teste','ativo':True,'pin':'8877',
   'perms':{k:True for k in ['porcionamento','historico','calculadora']}}],
 'fdo_op_atual':'teste-op'
}
INIT="Object.defineProperty(Navigator.prototype,'onLine',{get:()=>false,configurable:true});"
checks=[]; errors=[]
def check(nome,valor):
    assert valor,nome
    checks.append(nome);print('OK',nome,flush=True)

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
    ctx=browser.new_context(viewport={'width':360,'height':700},locale='pt-BR',timezone_id='America/Sao_Paulo',service_workers='block')
    ctx.route('**/*',lambda r:r.continue_() if r.request.url.startswith(URL) else r.abort())
    ctx.add_init_script(INIT+'const seed='+json.dumps(SEED)+';Object.entries(seed).forEach(([k,v])=>localStorage.setItem(k,JSON.stringify(v)));')
    p=ctx.new_page();p.set_default_timeout(5000);p.on('pageerror',lambda e:errors.append(str(e)))
    p.on('dialog',lambda d:d.accept('') if d.type=='prompt' else d.accept())
    p.goto(URL+'index.html',wait_until='domcontentloaded')
    p.wait_for_function("DEVICE.bootLiberado===true && uxTelaAtual()==='start'",timeout=15000)
    p.evaluate("FB.db=null;falar=()=>{};falarForcado=()=>{};iniciarVoz=()=>{};pararVoz=()=>{};pedirWakeLock=()=>{};")

    # Simula a R2 definitiva vigente observada no aparelho do usuário.
    p.evaluate("""()=>{
      const r=montarReceita(
        {nome:'Receita 2 - MASSA 3 KG',rotulo:'R2',farinhas:'Bagatelle 3500 g, Italiana 4280 g (sem Feuilletage)'},
        3500,0,4280,{agua:3580,acucar:878,leite:174,sal:174,manteiga:0,aprov:3000,fermento:84}
      );
      r.batimento=clonarReceita(RECEITAS.r2.batimento);
      LS.s('fdo_receitas_definitivas',[{id:'r2',numero:2,ativo:true,origem:'receita_padrao',receita:r,criadoTs:1,atualizadoTs:1}]);
      aplicarReceitasDefinitivas();
      window.fetch=async()=>{const d=new Date();d.setDate(d.getDate()+1);const day=d.toISOString().split('T')[0];
        return {ok:true,json:async()=>({hourly:{time:Array.from({length:7},(_,i)=>day+'T0'+i+':00'),temperature_2m:Array(7).fill(20)}})}};
    }""")

    p.locator('#s-start [data-perm="porcionamento"]').click()
    p.locator('#s-porc-menu [onclick="ir(\'receitas\')"]').click()
    p.locator('#receitas-list [onclick="iniciarReceita(\'r2\')"]').click()
    check('R2 verificada abre a etapa de massa reaproveitada',p.evaluate("uxTelaAtual()==='aproveitamento'"))
    check('Padrão inicia em 3.000 g',p.locator('#aprov-qtd').input_value()=='3000')
    check('Tela de reaproveitamento possui saída para Início',p.locator('#s-aproveitamento').get_by_text('⌂ Início').count()==1)

    p.locator('#aprov-qtd').fill('1200')
    check('Resumo mostra Bagatelle 3,870 kg', '3,870 kg' in p.locator('#aprov-resumo').inner_text())
    check('Resumo mostra manteiga 428 g', '428 g' in p.locator('#aprov-resumo').inner_text())
    p.locator('#aprov-continuar').click()
    check('Confirmação segue para lotes das farinhas',p.evaluate("uxTelaAtual()==='farinha-lotes'"))

    p.locator('#s-farinha-lotes [data-ux-voltar]').click()
    check('Voltar de lotes retorna ao reaproveitamento sem loop',p.evaluate("uxTelaAtual()==='aproveitamento'"))
    check('Voltar preserva os 1.200 g informados',p.locator('#aprov-qtd').input_value()=='1200')
    p.locator('#aprov-continuar').click()
    p.locator('#far-lotes-confirm-btn').click()
    p.wait_for_function("uxTelaAtual()==='pre-temp'")
    p.locator('#s-pre-temp [data-ux-voltar]').click()
    check('Voltar do clima retorna aos lotes',p.evaluate("uxTelaAtual()==='farinha-lotes'"))
    p.locator('#s-farinha-lotes [data-ux-voltar]').click()
    check('Segundo Voltar retorna ao reaproveitamento, não ao clima',p.evaluate("uxTelaAtual()==='aproveitamento'"))
    p.locator('#s-aproveitamento [data-ux-voltar]').click()
    check('Terceiro Voltar retorna à seleção de receitas',p.evaluate("uxTelaAtual()==='receitas'"))

    # Reentra e executa de verdade com 1.200 g.
    p.locator('#receitas-list [onclick="iniciarReceita(\'r2\')"]').click()
    p.locator('#aprov-qtd').fill('1200');p.locator('#aprov-continuar').click()
    p.locator('#far-lotes-confirm-btn').click();p.wait_for_function("uxTelaAtual()==='pre-temp'")
    p.locator('#pre-temp-continuar').click();p.wait_for_function("uxTelaAtual()==='temp'")
    idx=p.evaluate("OPCOES_FERMENTO.findIndex(o=>Number(o.horas)===14)")
    check('Existe opção operacional de 14 horas',idx>=0)
    p.evaluate('(i)=>setTempOpcao(i)',idx)
    p.wait_for_function("uxTelaAtual()==='active'")
    check('Secos usam Bagatelle 3,870 kg',p.evaluate("RECEITA.some(x=>x.nome==='Bagatelle'&&x.g===3870)"))
    check('Secos usam manteiga 428 g',p.evaluate("RECEITA.some(x=>x.nome==='Manteiga'&&x.g===428)"))

    for _ in range(20):
      if p.evaluate("st.modo==='pos_secos'"):break
      p.locator('#nav-normal .next').click()
    check('Porcionamento de secos chega à confirmação',p.evaluate("st.modo==='pos_secos'&&st.done.size===RECEITA.length"))
    p.locator('#secos-finalizar-btn').click()
    p.wait_for_function("uxTelaAtual()==='done'&&!st.criandoLote")
    lote=p.evaluate("LS.g('fdo_lotes',[])[0]")
    check('Balde registra 1.200 g no evento',lote['etapas']['porcionamento_secos']['aproveitamento']['usado_g']==1200)
    check('Balde registra padrão 3.000 g',lote['etapas']['porcionamento_secos']['aproveitamento']['padrao_g']==3000)
    vals=p.evaluate("l=>{const r=LS.g('fdo_lotes',[]).find(x=>x.id===l);return receitaValores(r.receitaSnapshot)}",lote['id'])
    check('Snapshot congela os pesos recalculados',vals['bag']==3870 and vals['ita']==4730 and vals['acucar']==970 and vals['agua']==3950 and vals['manteiga']==428 and vals['aprov']==1200)

    p.evaluate("ir('history');renderHist()")
    check('Histórico exibe massa reaproveitada executada','massa reaprov. 1,200 kg' in p.locator('#hist-list').inner_text())

    p.evaluate('(id)=>iniciarLiquidos(id)',lote['id'])
    check('Líquidos retomam água 3,950 kg do snapshot',p.evaluate("RECEITA.some(x=>x.nome==='Água com gelo'&&x.g===3950)"))
    check('Líquidos retomam massa laminada 1,200 kg do snapshot',p.evaluate("RECEITA.some(x=>x.nome==='Massa laminada'&&x.g===1200)"))
    check('Nenhum erro JavaScript não tratado',not errors)
    p.screenshot(path=str(OUT/'r2-1200-fluxo.png'),full_page=True)
    browser.close()
    (OUT/'resultado.json').write_text(json.dumps({'ok':True,'checks':checks},ensure_ascii=False,indent=2))
    print('USABILIDADE v26.8 OK:',len(checks),'verificações')
finally:
  server.shutdown()
