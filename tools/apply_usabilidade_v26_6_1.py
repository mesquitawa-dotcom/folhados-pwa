"""Bancada temporária: aplica o delta exato validado, somente na branch isolada.
Os hashes verificam a base, o transporte e cada arquivo final antes de gravar.
Este arquivo e o transporte são retirados do commit de entrega.
"""
from pathlib import Path
import base64
import hashlib
import json
import lzma
import os
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
BRANCH = 'agent/usabilidade-v26-6-1'
BASE = '04e3a34f6aba6436859a51b9c2c0e6216942492d'
PAYLOAD_SHA = 'a5d14ea44c006dad8780ff90ea1259ae768a8d003cf8246e826aa82aabbba9af'
ALLOWED = {
    '.github/workflows/validate-fdo.yml', 'Resumo_v26.6.1.md',
    'index.html', 'sw.js', 'tools/test_usabilidade_v26_6_1.py',
    'tools/test_v26_6.js', 'tools/validate_fdo.py',
}
TEMP = ['.github/workflows/usabilidade-workbench.yml',
        'tools/apply_usabilidade_v26_6_1.py',
        'tools/usabilidade_delta_1.txt', 'tools/usabilidade_delta_2.txt']

def run(*args):
    subprocess.run(args, check=True, cwd=ROOT)

def sha(data):
    return hashlib.sha256(data).hexdigest()

if os.environ.get('GITHUB_REF') != 'refs/heads/' + BRANCH:
    raise SystemExit('Aplicação permitida somente na branch isolada.')
remote_main = subprocess.check_output(
    ['git', 'ls-remote', 'origin', 'refs/heads/main'], text=True).split()[0]
if remote_main != BASE:
    raise SystemExit('main mudou: revisar a nova base antes de aplicar.')
raw = ''.join((ROOT / ('tools/usabilidade_delta_' + str(i) + '.txt')).read_text().strip()
              for i in (1, 2))
packed = base64.b64decode(raw, validate=True)
payload = lzma.decompress(packed)
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
    ops = e['ops']
    previous = 0
    for start, end, value in ops:
        if not (previous <= start <= end <= len(original)) or not isinstance(value, str):
            raise SystemExit('Intervalo inválido: ' + e['path'])
        previous = end
    changed = original
    for start, end, value in reversed(ops):
        changed = changed[:start] + value + changed[end:]
    result = changed.encode('utf-8')
    if sha(result) != e['after']:
        raise SystemExit('Resultado diferente: ' + e['path'])
    outputs[path] = result
for path, result in outputs.items():
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(result)
print('Sete arquivos conferidos e aplicados; main permanece intacto.', flush=True)
run('git', 'diff', '--check')
run(sys.executable, 'tools/validate_fdo.py')
for test in sorted((ROOT / 'tools').glob('test_*.js')):
    if 'database' not in test.name:
        run('node', str(test))
# CI completo (navegador real e Firebase Emulator) será exigido no PR.
run('git', 'config', 'user.name', 'github-actions[bot]')
run('git', 'config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
run('git', 'rm', '-f', *TEMP)
run('git', 'add', *sorted(ALLOWED))
run('git', 'commit', '-m', 'v26.6.1 — Usabilidade, retorno seguro e laminação em duas etapas')
run('git', 'push', 'origin', 'HEAD:refs/heads/' + BRANCH)
print('Código enviado à branch de trabalho. Não houve merge nem publicação no main.', flush=True)
