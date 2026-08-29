const fs=require('fs');
const assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const sw=fs.readFileSync('sw.js','utf8');
const rules=JSON.parse(fs.readFileSync('database.rules.json','utf8')).rules;
function has(src,x,msg){assert(src.includes(x),msg+' · ausente: '+x)}
has(html,'NOVIDADES v26.4:','histórico v26.4 preservado');
has(html,'NOVIDADES v26.4:','notas v26.4');
has(html,"imutavel(nome){return nome==='movimentos'||nome==='auditoria';}",'coleções históricas identificadas');
has(html,"let remoto=(await ref.once('value')).val()",'retry histórico começa lendo o remoto');
has(html,"try{await ref.set(reg);remoto=reg;}",'registro histórico só tenta criar quando ausente');
has(html,'this.igual(remoto,reg)','retry compara conteúdo remoto sem regravar');
has(html,'conflitoHistorico=true','conteúdo divergente vira conflito');
has(html,'Conflito histórico · registro da nuvem preservado','conflito fica visível e preserva nuvem');
assert.strictEqual(rules['.read'],false,'raiz deve negar leitura');
assert.strictEqual(rules['.write'],false,'raiz deve negar gravação');
assert(!Object.prototype.hasOwnProperty.call(rules.fdo_v25,'.write'),'fdo_v25 não pode ter write amplo');
for(const path of [
  rules.fdo_acessos.$id,
  rules.fdo_v25.estoque.movimentos.$id,
  rules.fdo_v25.receitas_auditoria.$id
]){
  assert(path['.write'].includes('!data.exists() && newData.exists()'),'trilha histórica deve permitir somente criação');
}
assert(rules.fdo_v25.lotes['.write'],'lotes continuam graváveis');
assert(rules.fdo_v25.laminacoes['.write'],'laminações continuam graváveis');
assert(rules.fdo_v25.receitas_definitivas['.write'],'receitas definitivas continuam versionáveis');
assert(rules.fdo_v25.estoque.contagens['.write'],'contagens continuam graváveis');
console.log('TESTE v26.4 OK · sync histórico idempotente + Rules append-only + allowlist explícita');
