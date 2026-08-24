from pathlib import Path
p=Path(__file__).resolve().parents[1]/'index.html'
s=p.read_text(encoding='utf-8')
old="if(r.fermentoFixo!=null){temp.value=17;horas.value=r.fermentoHoras!=null?r.fermentoHoras:'';}else{temp.value='';horas.value='';}"
new="if(r.fermentoFixo!=null){temp.value=17;horas.value=r.fermentoHoras!=null?r.fermentoHoras:'';}else{document.getElementById('teste-fermento').value='';temp.value='';horas.value='';}"
if s.count(old)!=1:
    raise SystemExit(f'marcador fermento: esperado 1, encontrado {s.count(old)}')
s=s.replace(old,new,1)
p.write_text(s,encoding='utf-8')
print('FERMENTO_DINAMICO_TESTE_SEM_VALOR_FALSO_OK')
