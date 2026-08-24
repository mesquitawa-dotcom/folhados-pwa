from pathlib import Path

p=Path(__file__).with_name('apply_receita_teste_v25_3b.py')
src=p.read_text(encoding='utf-8')
old="#s-receitas .modulo-desc{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:.68rem}\n    /* ════ v24.10 — LOTES DAS FARINHAS ════ */"
new="#s-receitas .modulo-desc{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:.68rem}\n\n    /* ════ v24.10 — LOTES DAS FARINHAS ════ */"
if src.count(old)!=1:
    raise SystemExit(f'marcador CSS no aplicador: esperado 1, encontrado {src.count(old)}')
src=src.replace(old,new,1)
exec(compile(src,str(p),'exec'))
