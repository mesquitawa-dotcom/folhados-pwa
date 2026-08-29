from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SITE_KEY='6LcPFJ8tAAAAAFk2yg6aQ5Qi0NNMERW220URnH2A'

def one(s,old,new,label):
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: esperado 1 ocorrência, obtido {n}')
    return s.replace(old,new,1)

# index.html
p=ROOT/'index.html'
s=p.read_text(encoding='utf-8')
s=one(s,
"       FOLHADOS D'OURO — atualização v26.4\n       NOVIDADES v26.4:",
"       FOLHADOS D'OURO — atualização v26.5\n       NOVIDADES v26.5:\n       • Firebase App Check com reCAPTCHA Enterprise integrado ao cliente, sem enforcement nesta versão.\n       • Tokens App Check são renovados automaticamente quando o aparelho está online.\n       • Configurações passa a mostrar diagnóstico do token App Check para validação antes do enforcement.\n       • SDK App Check compat 10.13.2 é servido localmente e pré-cacheado, preservando o boot offline.\n       • Nenhuma receita, peso, fermento, tempo, snapshot ou fluxo produtivo foi alterado.\n       NOVIDADES v26.4:",
'cabeçalho v26.5')

s=one(s,
'  <script src="vendor/firebase-app-compat.js"></script>\n  <script src="vendor/firebase-auth-compat.js"></script>',
'  <script src="vendor/firebase-app-compat.js"></script>\n  <script src="vendor/firebase-app-check-compat.js"></script>\n  <script src="vendor/firebase-auth-compat.js"></script>',
'SDK App Check local')

s=one(s,
'  <div class="cfg-s" style="font-size:.68rem;line-height:1.45">Versão 26.4 · cache fdo-v26-4 · Firebase SDK local</div>\n  <div class="cfg-s" id="storage-info"',
'  <div class="cfg-s" style="font-size:.68rem;line-height:1.45">Versão 26.5 · cache fdo-v26-5 · Firebase SDK local · App Check</div>\n  <div class="cfg-s" id="appcheck-info" style="font-size:.68rem;line-height:1.45">App Check: verificando…</div>\n  <div class="cfg-s" id="storage-info"',
'diagnóstico App Check em Config')

anchor='''  appId:"1:904726497964:web:03b4b9111ff0ff2580ed09"\n};\n// ===== Autorização do aparelho via Firebase Authentication (v25.2) ========'''
block=f'''  appId:"1:904726497964:web:03b4b9111ff0ff2580ed09"\n}};\n\n// ===== Firebase App Check — v26.5 ==========================================\n// reCAPTCHA Enterprise score-based. A site key é pública por definição.\n// Nesta versão o cliente só envia tokens; enforcement continua DESATIVADO no console.\nconst APP_CHECK_SITE_KEY='{SITE_KEY}';\nconst APP_CHECK={{\n  iniciado:false,ok:false,erro:'',\n  init(){{\n    if(this.iniciado)return this.ok;\n    this.iniciado=true;\n    if(typeof firebase==='undefined'||!firebase.appCheck||!firebase.appCheck.ReCaptchaEnterpriseProvider){{\n      this.erro='SDK App Check não carregou';console.warn('[APP CHECK]',this.erro);return false;\n    }}\n    try{{\n      const ac=firebase.appCheck();\n      ac.activate(new firebase.appCheck.ReCaptchaEnterpriseProvider(APP_CHECK_SITE_KEY),true);\n      this.ok=true;this.erro='';return true;\n    }}catch(e){{this.erro=(e&&e.message)||String(e);console.warn('[APP CHECK] init',e);return false}}\n  }},\n  async diagnostico(){{\n    const el=document.getElementById('appcheck-info');if(!el)return;\n    if(!navigator.onLine){{el.textContent='App Check: offline · será validado ao conectar';return}}\n    if(!this.iniciado&&typeof firebase!=='undefined'&&firebase.apps&&firebase.apps.length)this.init();\n    if(!this.ok){{el.textContent='App Check: ⚠ SDK não inicializado';return}}\n    try{{\n      const r=await firebase.appCheck().getToken(false);\n      el.textContent=(r&&r.token)?'App Check: ✓ token válido · reCAPTCHA Enterprise':'App Check: ⚠ sem token';\n    }}catch(e){{el.textContent='App Check: ⚠ token não obtido';console.warn('[APP CHECK] token',e)}}\n  }}\n}};\n\n// ===== Autorização do aparelho via Firebase Authentication (v25.2) ========'''
s=one(s,anchor,block,'bloco APP_CHECK')

s=one(s,
'if(!firebase.apps.length)firebase.initializeApp(FB_CFG);FB.db=firebase.database();this.auth=firebase.auth();verificarRelogioServidor();',
'if(!firebase.apps.length)firebase.initializeApp(FB_CFG);APP_CHECK.init();FB.db=firebase.database();this.auth=firebase.auth();verificarRelogioServidor();',
'App Check antes de Database/Auth no DEVICE')

s=one(s,
'if(!firebase.apps.length) firebase.initializeApp(FB_CFG);\n      this.db=firebase.database();',
'if(!firebase.apps.length) firebase.initializeApp(FB_CFG);\n      APP_CHECK.init();\n      this.db=firebase.database();',
'App Check antes do FB legado')

s=one(s,
"try{if(!firebase.apps.length)firebase.initializeApp(FB_CFG);FB.db=firebase.database();FB.status",
"try{if(!firebase.apps.length)firebase.initializeApp(FB_CFG);APP_CHECK.init();FB.db=firebase.database();FB.status",
'App Check antes do SYNC25')

s=one(s,
'function carregarConfig(){\n  atualizarStorageInfo();',
'function carregarConfig(){\n  atualizarStorageInfo();\n  if(typeof APP_CHECK!==\'undefined\')APP_CHECK.diagnostico();',
'diagnóstico no carregarConfig')

s=one(s,"versao:'26.4'","versao:'26.5'",'versão do backup')
p.write_text(s,encoding='utf-8')

# Service Worker
p=ROOT/'sw.js';sw=p.read_text(encoding='utf-8')
sw=one(sw,"const CACHE='fdo-v26-4';","const CACHE='fdo-v26-5';",'cache v26.5')
sw=one(sw,
"  './vendor/firebase-app-compat.js',\n  './vendor/firebase-auth-compat.js',",
"  './vendor/firebase-app-compat.js',\n  './vendor/firebase-app-check-compat.js',\n  './vendor/firebase-auth-compat.js',",
'asset App Check')
p.write_text(sw,encoding='utf-8')

# README vendor
p=ROOT/'vendor/README.md';vr=p.read_text(encoding='utf-8')
vr="Firebase JavaScript SDK compat 10.13.2, copiado do CDN oficial gstatic para permitir boot offline previsível. Componentes locais usados pelo PWA: App, App Check, Authentication e Realtime Database. Fontes: https://www.gstatic.com/firebasejs/10.13.2/ . O código do aplicativo continua usando a API compat existente.\n"
p.write_text(vr,encoding='utf-8')

# test_v26_4 vira teste histórico, não prende a versão corrente
p=ROOT/'tools/test_v26_4.js';t=p.read_text(encoding='utf-8')
t=one(t,"has(html,'atualização v26.4','cabeçalho v26.4');","has(html,'NOVIDADES v26.4:','histórico v26.4 preservado');",'histórico test_v26_4')
for old in [
"has(html,\"versao:'26.4'\",'backup identifica v26.4');\n",
"has(html,'Versão 26.4 · cache fdo-v26-4','Config identifica v26.4');\n",
"has(sw,\"const CACHE='fdo-v26-4'\",'cache v26.4');\n"
]:
    if old not in t: raise SystemExit('assert corrente v26.4 ausente: '+old.strip())
    t=t.replace(old,'',1)
p.write_text(t,encoding='utf-8')

# Validador geral
p=ROOT/'tools/validate_fdo.py';v=p.read_text(encoding='utf-8')
old='''# v26.4 — segurança Firebase e históricos append-only\nfor marker in (\n    'atualização v26.4','NOVIDADES v26.4:',"imutavel(nome){return nome==='movimentos'||nome==='auditoria';}",\n    'conflitoHistorico=false',"await ref.once('value')","await ref.set(reg)",'Conflito histórico · registro da nuvem preservado',\n    "versao:'26.4'"\n):\n    if marker not in html: fail('v26.4 sem marcador: '+marker)\n'''
new=f'''# v26.5 — App Check com reCAPTCHA Enterprise, sem enforcement\nfor marker in (\n    'atualização v26.5','NOVIDADES v26.5:','vendor/firebase-app-check-compat.js',\n    "const APP_CHECK_SITE_KEY='{SITE_KEY}'",'const APP_CHECK={{',\n    'new firebase.appCheck.ReCaptchaEnterpriseProvider(APP_CHECK_SITE_KEY)',\n    "APP_CHECK.init();FB.db=firebase.database()",'id="appcheck-info"',\n    "versao:'26.5'"\n):\n    if marker not in html: fail('v26.5 sem marcador: '+marker)\nif not (ROOT/'vendor/firebase-app-check-compat.js').exists(): fail('Firebase App Check local ausente')\n\n# v26.4 — segurança Firebase e históricos append-only preservada\nfor marker in (\n    'NOVIDADES v26.4:',"imutavel(nome){{return nome==='movimentos'||nome==='auditoria';}}",\n    'conflitoHistorico=false',"await ref.once('value')","await ref.set(reg)",'Conflito histórico · registro da nuvem preservado'\n):\n    if marker not in html: fail('v26.4 sem marcador: '+marker)\n'''
v=one(v,old,new,'bloco v26.5/v26.4 no validador')
v=one(v,"print('VALIDAÇÃO FDO v26.4 OK')","print('VALIDAÇÃO FDO v26.5 OK')",'saída do validador')
p.write_text(v,encoding='utf-8')

# Teste específico v26.5
(ROOT/'tools/test_v26_5.js').write_text(f'''const fs=require('fs');\nconst assert=require('assert');\nconst html=fs.readFileSync('index.html','utf8');\nconst sw=fs.readFileSync('sw.js','utf8');\nconst appcheck=fs.readFileSync('vendor/firebase-app-check-compat.js','utf8');\nfunction has(src,x,msg){{assert(src.includes(x),msg+' · ausente: '+x)}}\nhas(html,'atualização v26.5','cabeçalho v26.5');\nhas(html,'NOVIDADES v26.5:','notas v26.5');\nhas(html,'vendor/firebase-app-check-compat.js','SDK App Check local');\nhas(html,"const APP_CHECK_SITE_KEY='{SITE_KEY}'",'site key Enterprise registrada');\nhas(html,'new firebase.appCheck.ReCaptchaEnterpriseProvider(APP_CHECK_SITE_KEY)','provider Enterprise');\nhas(html,'ac.activate(new firebase.appCheck.ReCaptchaEnterpriseProvider(APP_CHECK_SITE_KEY),true)','auto-refresh App Check');\nhas(html,'id="appcheck-info"','diagnóstico App Check');\nhas(html,"APP_CHECK.init();FB.db=firebase.database()",'App Check antes do Database');\nhas(html,"versao:'26.5'",'backup v26.5');\nhas(html,'Versão 26.5 · cache fdo-v26-5 · Firebase SDK local · App Check','Config v26.5');\nhas(sw,"const CACHE='fdo-v26-5'",'cache v26.5');\nhas(sw,"'./vendor/firebase-app-check-compat.js'",'App Check pré-cacheado');\nhas(appcheck,'ReCaptchaEnterpriseProvider','bundle App Check contém provider Enterprise');\nhas(appcheck,'@firebase/app-check-compat','bundle App Check compat válido');\nconst order=['vendor/firebase-app-compat.js','vendor/firebase-app-check-compat.js','vendor/firebase-auth-compat.js','vendor/firebase-database-compat.js'].map(x=>html.indexOf(x));\nassert(order.every(x=>x>=0)&&order.every((x,i)=>i===0||x>order[i-1]),'ordem dos SDKs Firebase deve ser App → App Check → Auth → Database');\nconsole.log('TESTE v26.5 OK · App Check Enterprise integrado sem enforcement + SDK local + diagnóstico');\n''',encoding='utf-8')

# Smoke v26.5 herda a prova real de boot offline
oldsm=(ROOT/'tools/smoke_v26_4.py').read_text(encoding='utf-8')
newsm=oldsm.replace('_smoke_v26_4.html','_smoke_v26_5.html').replace('SMOKE v26.4 OK','SMOKE v26.5 OK')
(ROOT/'tools/smoke_v26_5.py').write_text(newsm,encoding='utf-8')

print('PATCH v26.5 aplicado: App Check + SDK local + diagnóstico + testes')
