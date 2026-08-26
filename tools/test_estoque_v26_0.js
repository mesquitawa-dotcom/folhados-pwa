const fs=require('fs');
const vm=require('vm');
const html=fs.readFileSync('index.html','utf8');
function ok(cond,msg){if(!cond){console.error('ERRO:',msg);process.exit(1)}}
function extractFunction(src,name){
  const start=src.indexOf('function '+name+'(');ok(start>=0,'função ausente: '+name);
  const brace=src.indexOf('{',start);let depth=0,quote='',esc=false;
  for(let i=brace;i<src.length;i++){
    const c=src[i];
    if(quote){if(esc)esc=false;else if(c==='\\')esc=true;else if(c===quote)quote='';continue;}
    if(c==='"'||c==="'"||c==='`'){quote=c;continue;}
    if(c==='{')depth++;else if(c==='}'&&--depth===0)return src.slice(start,i+1);
  }
  throw new Error('fim da função não encontrado: '+name);
}
ok(/atualização v26\.1/.test(html),'cabeçalho v26.1 ausente');
ok(html.includes('id="receitas-list"')&&html.includes('function renderReceitasPorcionamento()'),'lista dinâmica de receitas/consulta ausente');
ok(html.includes('id="receita-full-obs"')&&html.includes('salvarObservacaoReceita'),'observações da receita ausentes');
ok(html.includes('data-perm="estoque"')&&html.includes('Controle de Estoque'),'módulo Estoque ausente');
ok(html.includes("'fdo_v25/estoque/movimentos'")&&html.includes("'fdo_v25/estoque/contagens'"),'caminhos granulares do estoque ausentes');
ok(html.includes("'saida_receita_'+lote.id"),'saída automática não usa ID determinístico por balde');
ok(html.includes("n==='wagner'")&&html.includes("n==='maycon'"),'migração de permissões Wagner/Maycon ausente');
ok(html.includes('let estoqueReconciliando=false'),'proteção contra reentrada da reconciliação ausente');
ok(html.includes('ok?150:5000'),'retentativa do estoque sem intervalo de segurança');
ok(html.includes('function estoqueHojeISO()'),'data local da conferência semanal ausente');
ok(html.includes("else if(typeof ESTOQUE_SYNC!=='undefined')"),'início offline do estoque ausente');
ok(html.includes('grid-template-columns:minmax(0,1fr) 5.6rem'),'layout móvel da conferência não protegido');
ok(html.includes("estoqueDataISO(cont.data)||estoqueDataCurta(cont.emTs)"),'data selecionada da conferência não é exibida');
ok(html.includes('Math.min(atual,local)'),'marco de início não preserva o primeiro aparelho atualizado');
ok(html.includes("gerencia=OP.pode('estoque_entrada')"),'visão gerencial do estoque não está separada');
ok(html.includes('id="estoque-btn-mov"'),'botão de movimentações sem controle de visibilidade');
ok(html.includes('A comparação e as movimentações ficam disponíveis somente para a gerência.'),'acesso direto às movimentações não está protegido');
const am=html.match(/const ESTOQUE_ITENS=(\[.*?\]);\nconst ESTOQUE_POR_PASSO/s);ok(am,'catálogo de estoque não encontrado');
const itens=vm.runInNewContext(am[1]);
ok(itens.filter(x=>x.grupo==='insumo').length===8,'esperados 8 insumos controlados');
ok(itens.filter(x=>x.grupo==='embalagem').length===3,'esperadas 3 embalagens de conferência');
const mapa={};itens.forEach(x=>{if(x.passo)mapa[x.passo]=x.id});
const fn=extractFunction(html,'estoqueConsumoLote');
const sandbox={ESTOQUE_POR_PASSO:mapa,receitaDoLote:()=>({passos:[
  {nome:'Bagatelle',cat:'FARINHA',g:4113},{nome:'Feuilletage',cat:'FARINHA',g:0},{nome:'Italiana 00',cat:'FARINHA',g:5027},
  {nome:'Fermento seco',cat:'FERMENTO',g:84},{nome:'Açúcar',cat:'SECO',g:1030},{nome:'Sal refinado',cat:'SECO',g:204},
  {nome:'Manteiga',cat:'GORDURA',g:714},{nome:'Água com gelo',cat:'LÍQUIDO',g:4110},{nome:'Leite em pó',cat:'LÍQUIDO',g:204},
  {nome:'Massa laminada',cat:'MASSA',g:0},{nome:'Massa sem laminar',cat:'MASSA',g:0}
]}),loteFermentoG:()=>46,result:null};
vm.createContext(sandbox);vm.runInContext(fn+';result=estoqueConsumoLote({id:"teste"});',sandbox);
const esperado={farinha_bagatelle:-4113,farinha_italiana00:-5027,fermento_seco:-46,acucar:-1030,sal_refinado:-204,manteiga:-714,leite_po:-204};
ok(JSON.stringify(sandbox.result)===JSON.stringify(esperado),'consumo automático não corresponde à receita executada: '+JSON.stringify(sandbox.result));
ok(!('caixa_grande' in sandbox.result),'caixas não podem ter saída automática');
ok(!('agua' in sandbox.result),'água/gelo não deve entrar no estoque de compras');
console.log('TESTE ESTOQUE v26.0 OK · 8 insumos · 3 caixas · baixa única por balde');
