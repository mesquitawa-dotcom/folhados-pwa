"""Aplica somente o delta exato validado na branch isolada.
A configuração do workflow é entregue separadamente pela conexão autorizada.
"""
from pathlib import Path
import base64, hashlib, json, lzma, os, subprocess, sys
ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
BRANCH = 'agent/usabilidade-v26-6-1'
BASE = '04e3a34f6aba6436859a51b9c2c0e6216942492d'
PAYLOAD_SHA = 'a5d14ea44c006dad8780ff90ea1259ae768a8d003cf8246e826aa82aabbba9af'
WORKFLOW = '.github/workflows/validate-fdo.yml'
ALLOWED = {WORKFLOW, 'Resumo_v26.6.1.md', 'index.html', 'sw.js',
           'tools/test_usabilidade_v26_6_1.py', 'tools/test_v26_6.js', 'tools/validate_fdo.py'}
TEMP = ['tools/apply_usabilidade_v26_6_1.py',
        'tools/usabilidade_delta_1.txt', 'tools/usabilidade_delta_2.txt']
def run(*args):
    subprocess.run(args, check=True, cwd=ROOT)
def sha(data):
    return hashlib.sha256(data).hexdigest()
if os.environ.get('GITHUB_REF') != 'refs/heads/' + BRANCH:
    raise SystemExit('Aplicação permitida somente na branch isolada.')
remote_main = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], text=True).split()[0]
if remote_main != BASE:
    raise SystemExit('main mudou: revisar a nova base antes de aplicar.')
raw = ''.join((ROOT / ('tools/usabilidade_delta_' + str(i) + '.txt')).read_text().strip() for i in (1, 2))
payload = lzma.decompress(base64.b64decode(raw, validate=True))
if sha(payload) != PAYLOAD_SHA:
    raise SystemExit('Hash do transporte não confere; nenhum arquivo foi alterado.')
entries = json.loads(payload)
if {e['path'] for e in entries} != ALLOWED or len(entries) != len(ALLOWED):
    raise SystemExit('Lista de arquivos inesperada.')
outputs = {}
for e in entries:
    path = ROOT / e['path']
    before = path.read_bytes() if path.exists() else b''
    if sha(before) != e['before']:
        raise SystemExit('Base diferente: ' + e['path'])
    original = before.decode('utf-8')
    previous = 0
    for start, end, value in e['ops']:
        if not (previous <= start <= end <= len(original)) or not isinstance(value, str):
            raise SystemExit('Intervalo inválido: ' + e['path'])
        previous = end
    changed = original
    for start, end, value in reversed(e['ops']):
        changed = changed[:start] + value + changed[end:]
    result = changed.encode('utf-8')
    if sha(result) != e['after']:
        raise SystemExit('Resultado diferente: ' + e['path'])
    outputs[path] = result
for path, result in outputs.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(result)
print('Sete arquivos conferidos; main permanece intacto.', flush=True)
run('git', 'diff', '--check')
run(sys.executable, 'tools/validate_fdo.py')
for test in sorted((ROOT / 'tools').glob('test_*.js')):
    if 'database' not in test.name:
        run('node', str(test))
# O token do runner não tem permissão de workflows. Não a ampliar:
# conservar os workflows atuais e entregar essa alteração pelo conector autorizado.
run('git', 'restore', '--source=HEAD', '--', WORKFLOW)
run('git', 'config', 'user.name', 'github-actions[bot]')
run('git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
run('git', 'rm', '-f', *TEMP)
run('git', 'add', *sorted(ALLOWED - {WORKFLOW}))
run('git', 'commit', '-m', 'v26.6.1 — Usabilidade, retorno seguro e laminação em duas etapas')
run('git', 'push', 'origin', 'HEAD:refs/heads/' + BRANCH)
print('Código enviado à branch de trabalho; sem merge no main.', flush=True)
