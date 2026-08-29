from pathlib import Path
p=Path(__file__).with_name('apply_v26_4.py')
s=p.read_text(encoding='utf-8')
old="v=one(v,\",\\\"tipo:'estorno_cancelamento'\\\",\\\"tipo:'reaplicacao_restauro'\\\",\\\"versao:'26.3'\\\"\\n):\",\",\\\"tipo:'estorno_cancelamento'\\\",\\\"tipo:'reaplicacao_restauro'\\\"\\n):\",'versão antiga no bloco v26.3')"
new="v=one(v,\"\\\"versao:'26.3'\\\"\",\"\",'versão antiga no bloco v26.3')"
if s.count(old)!=1:
    raise SystemExit('âncora de reparo não encontrada exatamente uma vez')
p.write_text(s.replace(old,new,1),encoding='utf-8')
print('Âncora do validador v26.4 corrigida')
