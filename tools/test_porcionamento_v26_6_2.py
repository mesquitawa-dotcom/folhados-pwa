"""Regressão do botão de avanço do clima: geometria, clique e conclusão real do fluxo.
Dados sintéticos, sem acesso à nuvem. CI usa origem local/localStorage reais.
FDO_MEMORY_DOM=1 usa DOM/armazenamento isolados, sem equivaler a instalação PWA.
"""
from pathlib import Path
import argparse, http.server, json, os, re, shutil, threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get('FDO_TEST_ARTIFACT_DIR', '/tmp/fdo-porcionamento-tests'))
OUT.mkdir(parents=True, exist_ok=True)
MEMORY = os.environ.get('FDO_MEMORY_DOM') == '1'
parser = argparse.ArgumentParser()
parser.add_argument('--baseline')
args = parser.parse_args()
SOURCE = (ROOT / 'index.html').read_text()
SEED = {
    'fdo_key': 'TESTE_SEM_ACESSO_REAL', 'fdo_geo_ativo': False,
    'fdo_device_uid_v25': 'teste-aparelho',
    'fdo_device_auth_v25': {'uid': 'teste-aparelho', 'aprovado': True, 'nome': 'Teste'},
    'fdo_migr_v248': True, 'fdo_pin_ativo': False,
    'fdo_farinha_lotes_atuais': {'bagatelle': 'TESTE-BAG', 'italiana00': 'TESTE-00'},
    'fdo_operadores': [{'id': 'teste-op', 'nome': 'Operador de teste', 'ativo': True,
        'pin': '8877', 'perms': {k: True for k in ['porcionamento', 'historico', 'calculadora']}}],
    'fdo_op_atual': 'teste-op'
}
INIT = "Object.defineProperty(Navigator.prototype,'onLine',{get:()=>false,configurable:true});"
class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw): super().__init__(*a, directory=str(ROOT), **kw)
    def log_message(self, *a): pass
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Quiet)
threading.Thread(target=server.serve_forever, daemon=True).start()
URL = f'http://127.0.0.1:{server.server_port}/'
checks, geometry, errors = [], [], []

def check(name, value):
    assert value, name
    checks.append(name)
    print('OK', name, flush=True)

def load(browser, source=SOURCE, size=(360, 660), font=22):
    ctx = browser.new_context(viewport={'width': size[0], 'height': size[1]},
        locale='pt-BR', timezone_id='America/Sao_Paulo', service_workers='block')
    ctx.route('**/*', lambda r: r.continue_() if r.request.url.startswith(URL) else r.abort())
    p = ctx.new_page()
    p.set_default_timeout(4000)
    p.on('pageerror', lambda e: errors.append(str(e)))
    p.on('dialog', lambda d: d.accept('') if d.type == 'prompt' else d.accept())
    if MEMORY:
        stored = {k: json.dumps(v, ensure_ascii=False) for k, v in SEED.items()}
        pre = INIT + """
        function storage(d){return {getItem:k=>Object.hasOwn(d,k)?d[k]:null,
        setItem:(k,v)=>{d[k]=String(v)},removeItem:k=>{delete d[k]},clear:()=>{
        Object.keys(d).forEach(k=>delete d[k])},key:i=>Object.keys(d)[i]||null,
        get length(){return Object.keys(d).length}};}
        Object.defineProperty(window,'localStorage',{value:storage(STORED)});
        Object.defineProperty(window,'sessionStorage',{value:storage({})});
        """.replace('STORED', json.dumps(stored, ensure_ascii=False))
        def vendor(m): return '<script>' + (ROOT / m.group(1)).read_text().replace('</script', r'<\/script') + '</script>'
        html = source.replace('<body>', '<body><script>' + pre + '</script>', 1)
        html = re.sub(r'<script src="(vendor/[^"<>]+)"[^>]*></script>', vendor, html)
        p.set_content(html, wait_until='domcontentloaded')
    else:
        ctx.add_init_script(INIT + 'const seed=' + json.dumps(SEED) + ';Object.entries(seed).forEach(([k,v])=>localStorage.setItem(k,JSON.stringify(v)));')
        # O código sob teste permanece intacto; a resposta local seleciona a versão.
        ctx.route(URL + 'index.html', lambda r: r.fulfill(status=200, content_type='text/html', body=source))
        p.goto(URL + 'index.html', wait_until='domcontentloaded')
    try:
        p.wait_for_function("DEVICE.bootLiberado===true && document.querySelector('.scr:not(.off)').id==='s-start'", timeout=15000)
    except Exception:
        print("BOOT DEBUG", errors, p.locator("body").inner_text()[:900], flush=True)
        raise
    p.evaluate("FB.db=null;falar=()=>{};falarForcado=()=>{};iniciarVoz=()=>{};pararVoz=()=>{};pedirWakeLock=()=>{};")
    p.evaluate('(px)=>document.documentElement.style.fontSize=px+"px"', font)
    return ctx, p

def forecast(p, mode):
    p.evaluate("""mode=>{window.fetch=async()=>{
        if(mode==='pendente')return new Promise(()=>{});
        if(mode==='erro')throw new Error('Sem conexão (teste)');
        const d=new Date();d.setDate(d.getDate()+1);const day=d.toISOString().split('T')[0];
        return {ok:true,json:async()=>({hourly:{time:Array.from({length:7},(_,i)=>day+'T0'+i+':00'),temperature_2m:Array(7).fill(18.7)}})};
    }}""", mode)

def enter(p, rid='r4', mode='sucesso'):
    forecast(p, mode)
    p.locator('#s-start [data-perm="porcionamento"]').click()
    p.locator('#s-porc-menu [onclick="ir(\'receitas\')"]').click()
    p.locator('#receitas-list [onclick="iniciarReceita(\'' + rid + '\')"]').click()
    p.locator('#far-lotes-confirm-btn').click()
    p.wait_for_function("document.querySelector('.scr:not(.off)').id==='s-pre-temp'")
    expected = {'sucesso': 'Previsão carregada com sucesso.', 'erro': 'Não foi possível ler os dados.', 'pendente': 'Consultando satélite...'}[mode]
    p.wait_for_function('(txt)=>document.getElementById("pre-temp-status").textContent===txt', arg=expected)

def visible_action(p, selector):
    return p.eval_on_selector(selector, """b=>{const r=b.getBoundingClientRect();
    const x=r.x+r.width/2,y=r.y+r.height/2,hit=document.elementFromPoint(x,y);
    return {ok:!b.disabled && r.height>=44 && r.top>=0 && r.bottom<=innerHeight && r.left>=0 && r.right<=innerWidth && (hit===b||b.contains(hit)),
    top:r.top,bottom:r.bottom,height:r.height,viewport:innerHeight};}""")

try:
    with sync_playwright() as pw:
        exe = shutil.which('google-chrome') or shutil.which('chromium') or shutil.which('chromium-browser')
        browser = pw.chromium.launch(executable_path=exe, headless=True, args=['--no-sandbox', '--disable-dev-shm-usage'])
        if args.baseline:
            old = Path(args.baseline).read_text()
            scripts = lambda s: '\n'.join(x for x in re.findall(r'<script[^>]*>(.*?)</script>', s, re.S) if x.strip())
            check('JavaScript de produção idêntico à v26.6.1, exceto versão do backup', scripts(old) == scripts(SOURCE).replace("versao:'26.6.2'", "versao:'26.6.1'"))
            ctx, p = load(browser, old)
            enter(p)
            prior = visible_action(p, '#s-pre-temp button[onclick="escolherTemp()"]')
            check('Reproduz botão cortado na v26.6.1 em 360x660', not prior['ok'])
            geometry.append({'baseline': prior})
            p.screenshot(path=str(OUT / 'antes-360x660.png'))
            cfg = p.evaluate('JSON.stringify({receitas:RECEITAS,fermento:TEMP_FERMENTO,opcoes:OPCOES_FERMENTO,produtos:POS_PRODUTOS})')
            ctx.close()
        layouts = [(320,480,22), (360,660,22), (390,700,22), (412,780,22), (768,1024,22), (1280,800,22), (740,360,22), (360,660,27.5), (320,568,33)]
        for w,h,font in layouts:
            ctx,p = load(browser,size=(w,h),font=font)
            enter(p)
            result = visible_action(p,'#pre-temp-continuar')
            check(f'Avanço inteiro e tocável sem rolar em {w}x{h}, fonte {font}',result['ok'])
            check(f'Voltar acessível em {w}x{h}, fonte {font}',visible_action(p,'#s-pre-temp [data-ux-voltar]')['ok'])
            geometry.append({'width':w,'height':h,'font':font,'action':result})
            p.screenshot(path=str(OUT / f'depois-{w}x{h}-{font}.png'))
            # A previsão longa deve rolar sem carregar o botão junto.
            p.evaluate("document.getElementById('pre-temp-status').textContent='Mensagem sintética longa. '.repeat(80)")
            check('Previsão excedente tem rolagem própria',p.eval_on_selector('.pre-temp-container',"e=>getComputedStyle(e).overflowY==='auto'&&e.scrollHeight>e.clientHeight"))
            p.eval_on_selector('.pre-temp-container','e=>e.scrollTop=e.scrollHeight')
            check('Avanço permanece fixo após rolar previsão',visible_action(p,'#pre-temp-continuar')['ok'])
            p.locator('#s-pre-temp [data-ux-voltar]').click()
            check('Voltar recupera lotes sem perder preenchimento',p.evaluate("uxTelaAtual()==='farinha-lotes' && document.getElementById('far-lote-bag').value==='TESTE-BAG' && document.getElementById('far-lote-ita').value==='TESTE-00'"))
            ctx.close()
        for rid in ('r1','r2','r3','r4','r5'):
            for mode in ('sucesso','erro','pendente'):
                ctx,p = load(browser)
                if args.baseline:
                    check('Receitas/fermentos/tempos/produtos preservados '+rid+'/'+mode,cfg==p.evaluate('JSON.stringify({receitas:RECEITAS,fermento:TEMP_FERMENTO,opcoes:OPCOES_FERMENTO,produtos:POS_PRODUTOS})'))
                enter(p,rid,mode)
                check('Botão disponível com previsão '+mode+'/'+rid,visible_action(p,'#pre-temp-continuar')['ok'])
                p.locator('#pre-temp-continuar').click()
                fixed=p.evaluate('receitaAtualObj().fermentoFixo!=null')
                if not fixed:
                    check('Receita variável pede escolha existente '+rid,p.evaluate("uxTelaAtual()==='temp'"))
                    p.locator('#temp-grid .temp-btn').first.click()
                check('Clima → porcionamento '+rid+'/'+mode,p.evaluate("uxTelaAtual()==='active' && st.step===0"))
                params=p.evaluate('({fermento:st.fermento,temp:st.temp,horas:st.fermentoHoras,total:totalReceitaFull(st.receita)})')
                steps=p.evaluate('RECEITA.length')
                for _ in range(steps):
                    if p.evaluate("st.modo==='pos_secos'"):break
                    p.locator('#nav-normal .next').click()
                check('Ingredientes concluídos, respeitando salto de manteiga zero '+rid+'/'+mode,p.evaluate("st.modo==='pos_secos' && st.done.size===RECEITA.length"))
                p.locator('#secos-finalizar-btn').click()
                p.wait_for_function("uxTelaAtual()==='done' && !st.criandoLote")
                records=p.evaluate("LS.g('fdo_lotes',[])")
                check('Fluxo completo gera um único balde '+rid+'/'+mode,len(records)==1)
                info=records[0]['etapas']['porcionamento_secos']
                check('Parâmetros e rastreabilidade preservados '+rid+'/'+mode,info['feito'] and info['fermento_g']==params['fermento'] and info['temp']==params['temp'] and info['fermento_horas']==params['horas'] and info['total_g']==params['total'] and info['farinhas_lotes']['bagatelle']['principal']=='TESTE-BAG')
                check('Baixa única no estoque '+rid+'/'+mode,p.evaluate("LS.g('fdo_estoque_movimentos',[]).filter(x=>x.tipo==='saida_receita').length") ==1)
                p.locator('#done-etq-btn').click()
                check('Etiqueta do balde acessível '+rid+'/'+mode,p.evaluate("uxTelaAtual()==='etiqueta' && !!document.getElementById('etq-img').src"))
                check('Abrir etiqueta não duplica balde '+rid+'/'+mode,p.evaluate("LS.g('fdo_lotes',[]).length") ==1)
                ctx.close()
        check('Nenhum erro JavaScript no fluxo',not errors)
        browser.close()
    (OUT/'resultado.json').write_text(json.dumps({'ok':True,'checks':checks,'geometry':geometry,'memory_dom':MEMORY},ensure_ascii=False,indent=2))
    print('PORCIONAMENTO v26.6.2 OK:',len(checks),'verificações')
finally:
    server.shutdown()
