const fs=require('fs');
const assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const sw=fs.readFileSync('sw.js','utf8');

function has(src,needle,msg){assert(src.includes(needle),msg+' · ausente: '+needle)}
function notHas(src,needle,msg){assert(!src.includes(needle),msg+' · ainda presente: '+needle)}

has(html,'atualização v26.3','cabeçalho v26.3');
has(html,"const GEMINI_MODEL='gemini-3.6-flash'",'modelo Gemini estável definido em um ponto');
notHas(html,'gemini-2.0-flash','modelo Gemini desativado removido');
has(html,"if(!r.ok)throw new Error",'erro HTTP do Gemini tratado');
has(html,'Assistente indisponível agora. A produção continua normalmente.','falha de IA é explícita e não interrompe produção');
has(html,'function testarAssistenteConfig()','teste manual do Assistente disponível em Config');

for(const f of ['firebase-app-compat.js','firebase-auth-compat.js','firebase-database-compat.js']){
  has(html,'vendor/'+f,'Firebase SDK local referenciado: '+f);
  has(sw,'./vendor/'+f,'Firebase SDK entra no pré-cache: '+f);
}
notHas(html,'www.gstatic.com/firebasejs/10.13.2/','Firebase não pode depender do CDN no boot');

has(html,'function storageFalhou(err,chave)','falha de armazenamento tratada');
has(html,"id='storage-fatal-v263'",'falha de armazenamento cria bloqueio visível');
has(html,'function atualizarStorageInfo()','diagnóstico de armazenamento disponível');
has(html,"id=\"storage-info\"",'Config mostra saúde do armazenamento');
has(html,"throw e;}FB.push(k,v);return true",'LS.s não pode fingir sucesso após falha local');

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
has(html,"estoqueAcao:'estornar'",'cancelamento registra decisão de estoque');
has(html,"tipo:'estorno_cancelamento'",'movimento de estorno é auditável');
has(html,"tipo:'reaplicacao_restauro'",'movimento de restauração é auditável');

has(html,'Versão 26.3 · cache fdo-v26-3','diagnóstico exibe versão/cache');
has(sw,"const CACHE='fdo-v26-3'",'cache v26.3');

console.log('TESTE v26.3 OK · IA + armazenamento + offline + acesso + relógio + estoque');
