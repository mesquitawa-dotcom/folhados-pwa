from pathlib import Path
import json, re, subprocess, tempfile

ROOT=Path(__file__).resolve().parents[1]
html=(ROOT/'index.html').read_text(encoding='utf-8')
manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
sw=(ROOT/'sw.js').read_text(encoding='utf-8')

errors=[]

def fail(msg): errors.append(msg)

# v25.3 — Receita Teste rastreável, sem alterar R1–R5
for marker in (
    'Receita Teste','id="s-teste-base"','id="s-teste-edit"',
    'receitaSnapshot=clonarReceita','function receitaDoLote(lote)',
    'function adicionarObsTeste(id)','function loteReceitaChave(l)',
    'function testeLinhasEtiqueta(lote,pi)','TESTE · BALDE #',
    "if(x.lote&&x.lote.teste)return"
):
    if marker not in html: fail('v25.3 sem marcador: '+marker)

# v25.2 — Firebase Authentication + autorização do aparelho + rules as code
for marker in ("firebase-auth-compat.js","const DEVICE={","fdo_dispositivos/","signInAnonymously","DEVICE.bootstrap(()=>GEO.bootstrap(bootApp))","dispositivo:(typeof DEVICE"):
    if marker not in html: fail('v25.2 sem marcador: '+marker)
for req in ('database.rules.json','firebase.json'):
    if not (ROOT/req).exists(): fail('Arquivo Firebase ausente: '+req)
try:
    rules=json.loads((ROOT/'database.rules.json').read_text(encoding='utf-8'))
    rr=rules.get('rules',{})
    if rr.get('.read') is not False or rr.get('.write') is not False: fail('Raiz do RTDB deve negar leitura/gravação por padrão')
    if 'fdo_dispositivos' not in rr or 'fdo_v25' not in rr: fail('Rules sem allowlist de aparelho/v25')
    if rr.get('fdo_acessos',{}).get('.read') is not False: fail('fdo_acessos não deve ser legível pelo cliente')
except Exception as e: fail('database.rules.json inválido: '+str(e))
try:
    fj=json.loads((ROOT/'firebase.json').read_text(encoding='utf-8'))
    if fj.get('database',{}).get('rules')!='database.rules.json': fail('firebase.json não aponta para database.rules.json')
except Exception as e: fail('firebase.json inválido: '+str(e))

# v25.1 — sincronização granular/transacional
for marker in ("fdo_v25/lotes","fdo_v25/laminacoes","fdo_sync_outbox_v25","async function proxLoteNum()","await proxLoteNum()","async function proxLamSeqDia(ts)","function lotePartesUsadas(l)","Aparelho antigo detectado · conciliando","criarLaminacaoAtomica","fdo_v25/meta/lote_seq_reset","ack(k,id,sent)"):
    if marker not in html: fail('v25.1 sem marcador: '+marker)
if "function proxLoteNum(){ const n=LS.g('fdo_lote_seq',0)+1" in html: fail('Numeração antiga ainda presente')
if "versao:'25.0'" in html: fail('Backup ainda declara versão 25.0')

# 1) JavaScript inline: sintaxe real via Node
scripts=re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>',html,re.S)
inline='\n'.join(x for x in scripts if x.strip())
with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8') as f:
    f.write(inline); jsfile=f.name
r=subprocess.run(['node','--check',jsfile],capture_output=True,text=True)
if r.returncode: fail('JavaScript inválido: '+(r.stderr.strip() or r.stdout.strip()))

# 2) onclick simples -> função declarada. Ignora chamadas a métodos (obj.fn).
handlers=set(re.findall(r'onclick="\s*([A-Za-z_$][\w$]*)\s*\(',html))
declared=set(re.findall(r'function\s+([A-Za-z_$][\w$]*)\s*\(',inline))
declared.update(re.findall(r'(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(',inline))
missing=sorted(h for h in handlers if h not in declared)
if missing: fail('Handlers onclick sem função declarada: '+', '.join(missing))

# 3) IDs referenciados por getElementById devem existir no HTML
html_ids=set(re.findall(r'\bid="([^"]+)"',html))
used_ids=set(re.findall(r'getElementById\([\'\"]([^\'\"]+)[\'\"]\)',inline))
missing_ids=sorted(used_ids-html_ids)
if missing_ids: fail('IDs usados no JS e ausentes no HTML: '+', '.join(missing_ids))

# 4) PWA: manifest e assets locais
for key in ('name','short_name','start_url','scope','display','icons'):
    if key not in manifest: fail('manifest.json sem '+key)
for icon in manifest.get('icons',[]):
    src=icon.get('src','')
    if src and not src.startswith(('http://','https://')) and not (ROOT/src).exists():
        fail('Ícone do manifest ausente: '+src)
assets_m=re.search(r'const ASSETS=\[(.*?)\];',sw,re.S)
if not assets_m: fail('ASSETS não encontrado em sw.js')
else:
    for asset in re.findall(r"['\"]([^'\"]+)['\"]",assets_m.group(1)):
        if asset in ('./',): continue
        rel=asset[2:] if asset.startswith('./') else asset
        if rel and not (ROOT/rel).exists(): fail('Asset do Service Worker ausente: '+asset)

# 5) Cache deve acompanhar a versão indicada no cabeçalho
vm=re.search(r"atualização v(\d+)\.(\d+)",html)
cm=re.search(r"const CACHE=['\"]([^'\"]+)['\"]",sw)
if vm and cm:
    expected_cache=f'fdo-v{vm.group(1)}-{vm.group(2)}'
    if cm.group(1)!=expected_cache: fail(f'Cache {cm.group(1)} não corresponde à versão {expected_cache}')
else: fail('Não foi possível identificar versão/cache')

# 6) Totais: avalia o próprio código da aplicação. As 5 receitas padrão são invariantes.
#    Também simula exatamente a Receita Teste fornecida para a v25.3.
start=inline.find('const TEMP_FERMENTO')
end=inline.find('const st=')
if start<0 or end<0 or end<=start:
    fail('Não foi possível isolar o bloco de receitas')
else:
    recipe_js=inline[start:end]+"""
const __padrao=Object.fromEntries(Object.entries(RECEITAS).map(([k,r])=>[k,(r.passos||[]).reduce((s,p)=>s+(p.g||0),0)]));
const __teste=montarReceita(
  {nome:'TESTE · R3',rotulo:'TESTE · R3',farinhas:'referência v25.3',fermentoFixo:46,fermentoHoras:14},
  4113,0,5027,
  {agua:4110,acucar:1030,leite:204,sal:204,manteiga:714,aprov:0,semLaminar:0,fermento:46}
);
const __testeTotal=(__teste.passos||[]).reduce((s,p)=>s+(p.g||0),0);
console.log(JSON.stringify({padrao:__padrao,teste:__testeTotal}));
"""
    with tempfile.NamedTemporaryFile('w',suffix='.js',delete=False,encoding='utf-8') as f:
        f.write(recipe_js); rfile=f.name
    rr=subprocess.run(['node',rfile],capture_output=True,text=True)
    if rr.returncode:
        fail('Falha ao calcular receitas: '+rr.stderr.strip())
    else:
        try: calc=json.loads(rr.stdout.strip().splitlines()[-1])
        except Exception: calc={}; fail('Saída inválida no cálculo das receitas')
        expected_totals={'r1':15464,'r2':15690,'r3':15544,'r4':15564,'r5':15714}
        if calc.get('padrao')!=expected_totals:
            fail(f"Totais das receitas padrão alterados: esperado {expected_totals}, obtido {calc.get('padrao')}")
        if calc.get('teste')!=15448:
            fail(f"Receita Teste de referência deveria totalizar 15448 g, obtido {calc.get('teste')}")

if errors:
    print('\n'.join('ERRO: '+e for e in errors))
    raise SystemExit(1)
print('VALIDAÇÃO FDO OK')
print('Receitas padrão: R1=15464 R2=15690 R3=15544 R4=15564 R5=15714 g')
print('Receita Teste de referência v25.3: 15448 g')
