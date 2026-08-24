from pathlib import Path
p=Path(__file__).resolve().parents[1]/'index.html'
s=p.read_text(encoding='utf-8')
old="if(k==='fdo_lotes'&&typeof loteAtivo==='function')arr=arr.filter(l=>loteAtivo(l));return arr"
new="if(k==='fdo_lotes'&&typeof loteAtivo==='function')arr=arr.filter(l=>loteAtivo(l)&&!l.teste);if(k==='fdo_laminacoes')arr=arr.filter(l=>!l.testeId);return arr"
if s.count(old)!=1:
    raise SystemExit(f'marcador bridge: esperado 1, encontrado {s.count(old)}')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('BRIDGE_LEGADO_TESTES_PROTEGIDO_OK')
