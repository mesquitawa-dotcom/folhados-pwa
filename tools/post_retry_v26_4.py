from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

p=ROOT/'tools/validate_fdo.py';s=p.read_text(encoding='utf-8')
old='\"cur=>cur==null?reg:undefined\"'
new='\"await ref.once(\'value\')\",\"await ref.set(reg)\"'
if old in s:s=s.replace(old,new,1)
# também cobre a forma já materializada sem escapes Python
old2='"cur=>cur==null?reg:undefined"'
new2='"await ref.once(\'value\')","await ref.set(reg)"'
if old2 in s:s=s.replace(old2,new2,1)
if 'cur=>cur==null?reg:undefined' in s:raise SystemExit('marcador antigo de transaction ainda presente no validador')
if "await ref.once('value')" not in s or 'await ref.set(reg)' not in s:raise SystemExit('marcadores novos ausentes no validador')
p.write_text(s,encoding='utf-8')

p=ROOT/'tools/test_v26_4.js';t=p.read_text(encoding='utf-8')
if 'cur=>cur==null?reg:undefined' in t:
    t=t.replace("has(html,\"cur=>cur==null?reg:undefined\",'registro histórico só nasce quando ausente');","has(html,\"let remoto=(await ref.once('value')).val()\",'retry histórico começa lendo o remoto');\nhas(html,\"try{await ref.set(reg);remoto=reg;}\",'registro histórico só tenta criar quando ausente');",1)
if 'cur=>cur==null?reg:undefined' in t:raise SystemExit('marcador antigo ainda presente no teste v26.4')
p.write_text(t,encoding='utf-8')
print('Validador/teste v26.4 alinhados ao retry por leitura')
