const fs=require('fs');
const assert=require('assert');

const html=fs.readFileSync('index.html','utf8');

assert(
  html.includes("arr=arr.filter(l=>loteAtivo(l)&&!l.teste)"),
  'Receitas Teste não podem ser espelhadas para fdo_lotes legado'
);
assert(
  html.includes("if(k==='fdo_laminacoes')arr=arr.filter(l=>!l.testeId)"),
  'Laminações de teste não podem ser espelhadas para clientes legados'
);
assert(
  html.includes("document.getElementById('teste-fermento').value='';temp.value='';horas.value='';"),
  'R1–R3 não podem exibir o fermento estrutural 84 g como se fosse valor operacional do teste'
);
assert(
  html.includes("if(lote&&lote.receitaSnapshot&&Array.isArray(lote.receitaSnapshot.passos)) return lote.receitaSnapshot"),
  'Fluxos novos precisam priorizar o snapshot executado do teste'
);

console.log('TESTE COMPAT v25.3 OK · testes ficam só na estrutura canônica v25 · R1–R3 exigem fermento explícito');
