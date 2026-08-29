const fs=require('fs');
const assert=require('assert');
const vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
const sw=fs.readFileSync('sw.js','utf8');

function has(src,needle,msg){assert(src.includes(needle),msg+' · ausente: '+needle)}
function notHas(src,needle,msg){assert(!src.includes(needle),msg+' · ainda presente: '+needle)}
function extractFunction(src,name){
  const start=src.indexOf('function '+name+'(');assert(start>=0,'função ausente: '+name);
  const brace=src.indexOf('{',start);let depth=0,quote='',esc=false;
  for(let i=brace;i<src.length;i++){
    const c=src[i];
    if(quote){if(esc)esc=false;else if(c==='\\')esc=true;else if(c===quote)quote='';continue;}
    if(c==='"'||c==="'"||c==='`'){quote=c;continue;}
    if(c==='{')depth++;else if(c==='}'&&--depth===0)return src.slice(start,i+1);
  }
  throw new Error('fim não encontrado: '+name);
}

has(html,'atualização v26.3','cabeçalho v26.3');
has(html,"const GEMINI_MODEL='gemini-3.6-flash'",'modelo Gemini estável definido em um ponto');
notHas(html,'gemini-2.0-flash','modelo Gemini desativado removido');
has(html,"if(!r.ok)throw new Error",'erro HTTP do Gemini tratado');
has(html,'Assistente indisponível agora. A produção continua normalmente.','falha de IA é explícita e não interrompe produção');
has(html,'function testarAssistenteConfig()','teste manual do Assistente disponível em Config');
has(html,"'x-goog-api-key':key",'chave Gemini enviada em header');
notHas(html,'generateContent?key=','chave Gemini não deve ficar na URL');

for(const f of ['firebase-app-compat.js','firebase-auth-compat.js','firebase-database-compat.js']){
  has(html,'vendor/'+f,'Firebase SDK local referenciado: '+f);
  has(sw,'./vendor/'+f,'Firebase SDK entra no pré-cache: '+f);
}
notHas(html,'www.gstatic.com/firebasejs/10.13.2/','Firebase não pode depender do CDN no boot');

has(html,'function storageFalhou(err,chave)','falha de armazenamento tratada');
has(html,"id='storage-fatal-v263'",'falha de armazenamento cria bloqueio visível');
has(html,'function atualizarStorageInfo()','diagnóstico de armazenamento disponível');
has(html,"id=\"storage-info\"",'Config mostra saúde do armazenamento');
has(html,"catch(e){storageFalhou(e,k);throw e}FB.push(k,v);return true",'LS.s não pode fingir sucesso após falha local');

has(html,"fdo_operadores_inicializados",'estado de implantação dos operadores preservado');
has(html,'Cadastro de operadores indisponível','lista vazia após implantação bloqueia produção');
has(html,'A produção foi bloqueada para evitar acesso sem login.','fail-closed explicado ao operador');

has(html,'pinFalhasV263','contador de tentativas de PIN');
has(html,'pinBloqAteV263','bloqueio temporário de PIN');
has(html,'Muitas tentativas. Aguarde 30 s.','mensagem de limite de tentativas');

has(html,'function verificarRelogioServidor()','checagem de relógio contra Firebase');
has(html,".ref('.info/serverTimeOffset')",'offset de horário do servidor consultado');
has(html,'Relógio do aparelho parece incorreto','alerta de relógio incorreto');

has(html,'function registrarEstornoEstoqueLote(lote)','estorno de baixa por cancelamento');
has(html,'function registrarReaplicacaoEstoqueLote(lote)','restauração reaplica a baixa quando necessário');
has(html,'function estoqueReconciliarAjustesCancelamento()','estorno/reaplicação são reconciliáveis');
has(html,"estoqueAcao='estornar'",'cancelamento registra decisão de estoque');
has(html,"tipo:'estorno_cancelamento'",'movimento de estorno é auditável');
has(html,"tipo:'reaplicacao_restauro'",'movimento de restauração é auditável');
has(html,"registrarEstornoEstoqueLote(lote);registrarReaplicacaoEstoqueLote(lote)",'restauro garante estorno antes de reaplicar baixa');

// Simulação contábil do novo fluxo de estoque, isolando as funções reais do app.
const stockFns=['estoqueMovimentoPorId','registrarEstornoEstoqueLote','registrarReaplicacaoEstoqueLote','estoqueReconciliarAjustesCancelamento']
  .map(n=>extractFunction(html,n)).join('\n');
const sandbox={
  movs:[],lotes:[],
  estoqueMovimentos(){return this.movs;},
  estoqueTemMovimento(id){return this.movs.some(m=>m&&m.id===id);},
  ESTOQUE_SYNC:{localPush(nome,reg){assert.strictEqual(nome,'movimentos');sandbox.movs.push(JSON.parse(JSON.stringify(reg)));}},
  DEVICE:{audit(){return {teste:true};}},getOp(){return 'Teste';},
  LS:{g(k,d){return k==='fdo_lotes'?sandbox.lotes:d;}},
  console
};
vm.createContext(sandbox);vm.runInContext(stockFns,sandbox);
function saldoTotal(movs){const out={};for(const m of movs)for(const [k,v] of Object.entries(m.itens||{}))out[k]=(out[k]||0)+(Number(v)||0);return out;}

const original={id:'saida_receita_L1',tipo:'saida_receita',itens:{farinha:-100,agua:-50}};
const lote={id:'L1',num:1,receita:'r1',receitaNome:'R1',cancelado:{emTs:1000,op:'Teste',estoqueAcao:'estornar'}};
sandbox.movs=[JSON.parse(JSON.stringify(original))];sandbox.lotes=[lote];
assert.strictEqual(sandbox.registrarEstornoEstoqueLote(lote),true,'cancelamento por engano deve criar estorno');
assert.deepStrictEqual(saldoTotal(sandbox.movs),{farinha:0,agua:0},'cancelamento estornado deve zerar efeito da saída');
assert.strictEqual(sandbox.registrarEstornoEstoqueLote(lote),false,'estorno deve ser idempotente');
lote.restaurado={emTs:2000,op:'Teste'};
sandbox.estoqueReconciliarAjustesCancelamento();
assert.deepStrictEqual(saldoTotal(sandbox.movs),{farinha:-100,agua:-50},'restauração deve reaplicar exatamente a baixa original');
assert.strictEqual(sandbox.movs.filter(m=>m.tipo==='reaplicacao_restauro').length,1,'reaplicação deve ser única');

// Cenário de recuperação: balde já restaurado, mas movimento de estorno desapareceu/não foi salvo.
const original2={id:'saida_receita_L2',tipo:'saida_receita',itens:{farinha:-80,agua:-20}};
const lote2={id:'L2',num:2,receita:'r1',receitaNome:'R1',cancelado:{emTs:3000,op:'Teste',estoqueAcao:'estornar'},restaurado:{emTs:4000,op:'Teste'}};
sandbox.movs=[JSON.parse(JSON.stringify(original2))];sandbox.lotes=[lote2];
sandbox.estoqueReconciliarAjustesCancelamento();
assert.strictEqual(sandbox.movs.filter(m=>m.tipo==='estorno_cancelamento').length,1,'reconciliação deve reconstruir estorno ausente');
assert.strictEqual(sandbox.movs.filter(m=>m.tipo==='reaplicacao_restauro').length,1,'reconciliação deve reconstruir reaplicação');
assert.deepStrictEqual(saldoTotal(sandbox.movs),{farinha:-80,agua:-20},'recuperação completa deve manter somente a baixa do balde ativo');

has(html,'Versão 26.3 · cache fdo-v26-3','diagnóstico exibe versão/cache');
has(sw,"const CACHE='fdo-v26-3'",'cache v26.3');

console.log('TESTE v26.3 OK · IA + armazenamento + offline + acesso + relógio + estoque reconciliável');
