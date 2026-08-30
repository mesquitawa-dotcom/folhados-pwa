from pathlib import Path
import http.server
import os
import shutil
import subprocess
import threading
import time

ROOT=Path(__file__).resolve().parents[1]
src=(ROOT/'index.html').read_text(encoding='utf-8')
smoke=ROOT/'_smoke_v26_6.html'

prelude="""<script>
try{
  Object.defineProperty(Navigator.prototype,'onLine',{get:function(){return false;},configurable:true});
  localStorage.setItem('fdo_key',JSON.stringify('smoke-key'));
  localStorage.setItem('fdo_geo_ativo',JSON.stringify(false));
  localStorage.setItem('fdo_device_uid_v25',JSON.stringify('smoke-device'));
  localStorage.setItem('fdo_device_auth_v25',JSON.stringify({uid:'smoke-device',aprovado:true,nome:'Smoke'}));
}catch(e){}
</script>"""
probe="""<script>
setTimeout(function(){
  var v=document.querySelector('.scr:not(.off)');
  document.body.setAttribute('data-smoke-screen',v?v.id:'nenhuma');
  document.body.setAttribute('data-smoke-destino',typeof destinoBoot==='function'?'ok':'ausente');
  document.body.setAttribute('data-smoke-receita',typeof iniciarReceita==='function'?'ok':'ausente');
  document.body.setAttribute('data-smoke-pos',typeof renderModelagem==='function'&&typeof abrirCorteLaminacao==='function'?'ok':'ausente');
},2200);
</script>"""

if '<body>' not in src or '</body>' not in src:
    raise SystemExit('HTML sem body para smoke')
smoke.write_text(src.replace('<body>','<body>'+prelude,1).replace('</body>',probe+'</body>',1),encoding='utf-8')

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args):
        pass

os.chdir(ROOT)
server=http.server.ThreadingHTTPServer(('127.0.0.1',8765),Quiet)
th=threading.Thread(target=server.serve_forever,daemon=True)
th.start()

chrome=next((p for p in [shutil.which('google-chrome'),shutil.which('chromium'),shutil.which('chromium-browser')] if p),None)
if not chrome:
    server.shutdown(); smoke.unlink(missing_ok=True)
    raise SystemExit('Chrome/Chromium não encontrado no runner')

try:
    cmd=[chrome,'--headless=new','--no-sandbox','--disable-gpu','--disable-background-networking','--virtual-time-budget=5000','--dump-dom','http://127.0.0.1:8765/_smoke_v26_6.html']
    r=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
    if r.returncode!=0:
        raise SystemExit('Chrome falhou no smoke: '+(r.stderr[-2000:] or str(r.returncode)))
    dom=r.stdout
    if 'data-smoke-screen="s-start"' not in dom:
        raise SystemExit('Boot não chegou à tela inicial. Marcador: '+next((x for x in dom.split() if 'data-smoke-screen=' in x),'ausente'))
    if 'data-smoke-destino="ok"' not in dom or 'data-smoke-receita="ok"' not in dom or 'data-smoke-pos="ok"' not in dom:
        raise SystemExit('Funções críticas não ficaram disponíveis após o boot')
    print('SMOKE v26.6 OK · boot offline autorizado chegou à tela inicial')
finally:
    server.shutdown()
    smoke.unlink(missing_ok=True)
