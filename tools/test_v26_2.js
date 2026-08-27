const fs=require('fs');
const assert=require('assert');
const vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
function has(x,msg){assert(html.includes(x),msg)}
has('atualização v26.2','cabeçalho v26.2');
has('id="inp-est-cont-op"','responsável da contagem configurável');
has('id="inp-est-cont-dia"','dia da contagem configurável');
has('id="estoque-lembrete-bg"','pop-up da contagem');
has("configuracoes:{local:'fdo_estoque_configuracoes',path:'fdo_v25/estoque/configuracoes'}",'configuração sincronizada');
has('function estoqueChecarLembreteContagem()','checagem do lembrete');
has('id="receita-edit-batimento"','batimento no editor da receita');
has('id="teste-bt1"','batimento na Receita Teste');
has('function migrarBatimentoReceitasV262()','migração dos tempos antigos');
has('function congelarBatimentoBaldesPendentesV262()','congelamento dos baldes pendentes');
has('temposProgramados:clonarReceita','histórico guarda tempos programados');
has('tempos:clonarReceita(batTemposRun','retomada guarda tempos');
assert(!html.includes('id="inp-bt1"'),'batimento não pode continuar como configuração global visível');
assert(!html.includes('id="inp-bt2"'),'bt2 global removido');
assert(!html.includes('id="inp-bt3"'),'bt3 global removido');
assert(!html.includes('id="inp-bt4"'),'bt4 global removido');

const scripts=[...html.matchAll(/<script(?:\s[^>]*)?>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function extractFunction(src,name){
  const start=src.indexOf('function '+name+'(');assert(start>=0,'função ausente: '+name);
  const brace=src.indexOf('{',start);let depth=0,quote='',esc=false;
  for(let i=brace;i<src.length;i++){
    const c=src[i];if(quote){if(esc)esc=false;else if(c==='\\')esc=true;else if(c===quote)quote='';continue;}
    if(c==='"'||c==="'"||c==='`'){quote=c;continue;}if(c==='{')depth++;else if(c==='}'&&--depth===0)return src.slice(start,i+1);
  }throw new Error('fim não encontrado '+name);
}
const decl=scripts.match(/const BATIMENTO_CAMPOS=\[[\s\S]*?\];/)[0];
const funcs=['batTemposNormalizar','batTemposBaseLegado','batAgenda'].map(n=>extractFunction(scripts,n)).join('\n');
const sandbox={result:null,batTemposRun:{t1:4,t2:5,t3:2,t4:1},getBatT1:()=>4,getBatT2:()=>6,getBatT3:()=>3,getBatT4:()=>2};
vm.createContext(sandbox);vm.runInContext(decl+'\n'+funcs+'\nresult=batAgenda().map(x=>x.min);',sandbox);
assert.deepStrictEqual(Array.from(sandbox.result),[4,9,11,12],'agenda precisa somar os quatro intervalos da receita');
console.log('TESTE v26.2 OK · lembrete configurável + batimento por receita + snapshots');
