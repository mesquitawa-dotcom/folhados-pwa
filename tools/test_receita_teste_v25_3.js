const fs=require('fs');
const assert=require('assert');

const html=fs.readFileSync('index.html','utf8');
const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');

const rIni=scripts.indexOf('const TEMP_FERMENTO');
const rFim=scripts.indexOf('const st=',rIni);
const tIni=scripts.indexOf('const TESTE_CAMPOS=',rFim);
const tFim=scripts.indexOf('// Escolhe qual receita rodar',tIni);
if(rIni<0||rFim<0||tIni<0||tFim<0) throw new Error('Blocos de receita/teste não encontrados');

const receita=scripts.slice(rIni,rFim);
const teste=scripts.slice(tIni,tFim);
const program=receita+`\nvar st={testeBase:'r3'};\n`+teste+String.raw`
const valores={
  bag:4113,feu:0,ita:5027,fermento:46,acucar:1030,sal:204,manteiga:714,
  agua:4110,leite:204,aprov:0,semLaminar:0
};
const alteracoes=testeAlteracoes('r3',valores,20,14);
assert.deepStrictEqual(alteracoes.map(x=>x.k),['bag','ita','acucar','sal','manteiga','agua','leite','aprov']);
assert(!alteracoes.some(x=>x.k==='fermento'),'46 g em 20°C/14 h não deveria ser marcado como alteração de fermento');

const r=montarReceita(
  {nome:'TESTE · R3',rotulo:'TESTE · R3',farinhas:'teste',fermentoFixo:46,fermentoHoras:14,teste:true,baseReceita:'r3'},
  valores.bag,valores.feu,valores.ita,
  {agua:valores.agua,acucar:valores.acucar,leite:valores.leite,sal:valores.sal,manteiga:valores.manteiga,aprov:valores.aprov,semLaminar:valores.semLaminar,fermento:valores.fermento}
);
const total=(r.passos||[]).reduce((s,p)=>s+(p.g||0),0);
assert.strictEqual(total,15448,'total da Receita Teste de referência');
assert.strictEqual((r.passos.find(p=>p.nome==='Fermento seco')||{}).g,46,'fermento executado');
assert.strictEqual((r.passos.find(p=>p.nome==='Massa laminada')||{}).g,0,'Aproveita precisa ficar 0 no snapshot completo');

r.passosLiquidos=r.passosLiquidos.filter(p=>!(p.nome==='Massa laminada'&&Number(p.g)===0));
assert(!r.passosLiquidos.some(p=>p.nome==='Massa laminada'),'Aproveita 0 não deve gerar passo inútil no porcionamento');

assert.deepStrictEqual(Object.keys(RECEITAS),['r1','r2','r3','r4','r5'],'Receita Teste não pode virar uma R6 fixa');
assert.strictEqual(RECEITAS.r3.nome,'Receita 3 - PADRÃO','R3 precisa continuar intacta');
console.log('TESTE RECEITA TESTE v25.3 OK · total 15448 g · 8 alterações registradas');
`;

new Function('assert',program)(assert);
