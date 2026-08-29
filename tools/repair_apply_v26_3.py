from pathlib import Path
p=Path(__file__).with_name('apply_v26_3.py')
s=p.read_text(encoding='utf-8')
old="one(old_del,new_del,'cancelamento com estoque')"
new="between('function apagarLote(id){','function restaurarLote(id){',new_del+'\\n','cancelamento com estoque')"
if s.count(old)!=1:
    raise SystemExit('âncora da chamada de cancelamento não encontrada exatamente uma vez')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('Âncora de cancelamento convertida para substituição estrutural')
