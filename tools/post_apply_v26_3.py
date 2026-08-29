from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

# Service Worker
p=ROOT/'sw.js';s=p.read_text(encoding='utf-8')
old="const CACHE='fdo-v26-2';"
if s.count(old)!=1: raise SystemExit('cache v26.2 não encontrado exatamente uma vez')
s=s.replace(old,"const CACHE='fdo-v26-3';",1)
anchor="  './icon-512.png',\n"
if s.count(anchor)!=1: raise SystemExit('âncora ASSETS não encontrada')
s=s.replace(anchor,anchor+"  './vendor/firebase-app-compat.js',\n  './vendor/firebase-auth-compat.js',\n  './vendor/firebase-database-compat.js',\n",1)
p.write_text(s,encoding='utf-8')

# Validador principal
p=ROOT/'tools/validate_fdo.py';v=p.read_text(encoding='utf-8')
needle="# v26.2 — lembrete de estoque + batimento por receita\n"
if v.count(needle)!=1: raise SystemExit('âncora validador v26.2 não encontrada')
checks="""# v26.3 — confiabilidade, diagnóstico e offline real
for marker in (
    'atualização v26.3',\"const GEMINI_MODEL='gemini-3.6-flash'\",'function testarAssistenteConfig()',
    'vendor/firebase-app-compat.js','vendor/firebase-auth-compat.js','vendor/firebase-database-compat.js',
    'function storageFalhou(err,chave)','id=\"storage-info\"','fdo_operadores_inicializados',
    'Cadastro de operadores indisponível','pinFalhasV263','function verificarRelogioServidor()',
    'function registrarEstornoEstoqueLote(lote)','function registrarReaplicacaoEstoqueLote(lote)',
    \"tipo:'estorno_cancelamento'\",\"tipo:'reaplicacao_restauro'\",\"versao:'26.3'\"
):
    if marker not in html: fail('v26.3 sem marcador: '+marker)
if 'gemini-2.0-flash' in html: fail('Gemini 2.0 Flash desativado ainda presente')
if 'www.gstatic.com/firebasejs/10.13.2/' in html: fail('Firebase ainda depende do CDN no boot')
for req in ('vendor/firebase-app-compat.js','vendor/firebase-auth-compat.js','vendor/firebase-database-compat.js'):
    if not (ROOT/req).exists(): fail('Firebase local ausente: '+req)

"""
v=v.replace(needle,checks+needle,1)
v=v.replace("    'temposProgramados:clonarReceita',\"versao:'26.2'\"\n","    'temposProgramados:clonarReceita'\n",1)
v=v.replace("print('VALIDAÇÃO FDO v26.2 OK')","print('VALIDAÇÃO FDO v26.3 OK')",1)
p.write_text(v,encoding='utf-8')
print('POST PATCH v26.3 aplicado em sw.js + validate_fdo.py')
