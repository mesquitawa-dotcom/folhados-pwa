// Executar exclusivamente no Firebase Emulator; dados sintéticos, sem produção real.
const fs=require('fs'),assert=require('assert');
const {initializeTestEnvironment,assertFails}=require('@firebase/rules-unit-testing');
const {ref,set,get,onValue,runTransaction}=require('firebase/database');
const {load,form,plan}=require('./fluxo_v26_7_test_helper');
const A=load();let count=0;
function ok(label,cond){assert(cond,label);console.log('OK '+(++count)+' '+label);}
// Escrita confirmada em A não significa que o listener de B já recebeu o evento.
// Aguarda o estado observável da interface, sem sleep fixo e sem repetir gravações.
function esperarEstado(r,condicao,descricao){
 return new Promise((resolve,reject)=>{
  let stop=null,terminou=false;
  const timer=setTimeout(()=>fim(new Error('Não propagou: '+descricao)),15000);
  function fim(erro,snapshot){if(terminou)return;terminou=true;clearTimeout(timer);if(stop)stop();if(erro)reject(erro);else resolve(snapshot);}
  stop=onValue(r,s=>{try{if(condicao(s.val()||{}))fim(null,s);}catch(e){fim(e);}},e=>fim(e));
  if(terminou)stop(); // O SDK pode entregar imediatamente o valor já em cache.
 });
}
(async()=>{
 const stops=[];
 const env=await initializeTestEnvironment({projectId:'demo-fdo-rules',database:{rules:fs.readFileSync('database.rules.json','utf8')}});
 try{
  await env.clearDatabase();
  let base=Object.fromEntries(Array.from({length:21},(_,i)=>{const f=form('f'+i);return [f.id,f];}));
  base=A.fluxoAplicarPlano(base,plan('entradaArmario',Object.keys(base).slice(0,19),10000));
  await env.withSecurityRulesDisabled(async c=>{
   const db=c.database();
   await set(ref(db,'fdo_dispositivos/teste-a'),{ativo:true,nome:'A teste'});
   await set(ref(db,'fdo_dispositivos/teste-b'),{ativo:true,nome:'B teste'});
   await set(ref(db,'fdo_v25/formas'),JSON.parse(JSON.stringify(base)));
   await set(ref(db,'fdo_v25/lotes/balde-antigo'),{id:'balde-antigo',etapas:{fermentacao:{feito:true,emTs:999}}});
  });
  const db1=env.authenticatedContext('teste-a').database(),db2=env.authenticatedContext('teste-b').database();
  const r1=ref(db1,'fdo_v25/formas'),r2=ref(db2,'fdo_v25/formas');
  // Espelha SYNC25.init: cada aparelho mantém o listener da coleção ativo.
  // get() sozinho não conserva o cache usado pela primeira chamada da transação.
  function watch(r){return new Promise((resolve,reject)=>{let first=true;stops.push(onValue(r,s=>{if(first){first=false;resolve(s);}},reject));});}
  await Promise.all([watch(r1),watch(r2)]);
  function tx(r,p){return runTransaction(r,cur=>{try{return JSON.parse(JSON.stringify(A.fluxoAplicarPlano(cur,p)));}catch(e){console.log('Transação não aplicada:',e.message);return undefined;}},{applyLocally:false});}
  const races=await Promise.all([tx(r1,plan('entradaArmario',['f19'],11000,{operacaoId:'a-ultima-vaga'})),tx(r2,plan('entradaArmario',['f20'],11000,{operacaoId:'b-ultima-vaga'}))]);
  ok('somente um aparelho obtém a última vaga',races.filter(x=>x.committed).length===1);
  await Promise.all([r1,r2].map(r=>esperarEstado(r,m=>A.fluxoOcupacao(1,Object.values(m))===20,'última vaga em ambos os aparelhos')));
  let current=(await get(r1)).val();ok('capacidade final nunca excede 20',A.fluxoOcupacao(1,Object.values(current))===20);
  const loser=A.fluxoEstadoForma(current.f19)==='pronta_fermentar'?'f19':'f20';
  const second=await tx(r2,plan('entradaArmario',[loser],12000));ok('outro aparelho vê armário cheio e não grava',!second.committed);
  const leave=await tx(r1,plan('saidaArmario',['f0','f1'],20000));ok('saída real parcial libera duas vagas',leave.committed&&A.fluxoOcupacao(1,Object.values(leave.snapshot.val()))===18);
  await esperarEstado(r2,m=>m.f0&&m.f1&&A.fluxoEstadoForma(m.f0)==='aguardando_assamento'&&A.fluxoEstadoForma(m.f1)==='aguardando_assamento'&&A.fluxoOcupacao(1,Object.values(m))===18,'retirada parcial no segundo aparelho');
  const enter=await tx(r2,plan('entradaArmario',[loser],21000));ok('vaga liberada pode ser ocupada no segundo aparelho',enter.committed&&A.fluxoOcupacao(1,Object.values(enter.snapshot.val()))===19);
  const bad=await tx(r1,plan('assamentoInicio',['f0','f2'],22000));ok('grupo com etapa divergente não avança parcialmente',!bad.committed&&!((await get(r1)).val().f0.eventos||{}).assamentoInicio);
  const bp=plan('assamentoInicio',['f0','f1'],23000),bake=await tx(r1,bp);ok('assamento inicia com as formas retiradas',bake.committed);
  await esperarEstado(r2,m=>m.f0&&m.f1&&A.fluxoEstadoForma(m.f0)==='assando'&&A.fluxoEstadoForma(m.f1)==='assando','início do assamento no segundo aparelho');
  const repeat=await tx(r2,bp);ok('retry de outra conexão é idempotente',repeat.committed&&repeat.snapshot.val().f0.eventos.assamentoInicio.emTs===23000);
  const end=await tx(r2,plan('assamentoFim',['f0','f1'],24000));ok('assamento finalizado nos mesmos IDs',end.committed&&A.fluxoEstadoForma(end.snapshot.val().f0)==='assada');
  await esperarEstado(r1,m=>m.f0&&m.f1&&A.fluxoEstadoForma(m.f0)==='assada'&&A.fluxoEstadoForma(m.f1)==='assada','conclusão do assamento no primeiro aparelho');
  // Uma fila antiga com timestamp maior precisa preservar as etapas confirmadas.
  const stale={...form('f0'),atualizadoTs:99000};
  await runTransaction(ref(db1,'fdo_v25/formas/f0'),cur=>JSON.parse(JSON.stringify(A.SYNC25.merge('fdo_formas',cur,stale))),{applyLocally:false});
  ok('sincronização de cópia antiga não apaga assamento',A.fluxoEstadoForma((await get(ref(db2,'fdo_v25/formas/f0'))).val())==='assada');
  ok('registro legado no balde não é modificado',(await get(ref(db1,'fdo_v25/lotes/balde-antigo/etapas/fermentacao/emTs'))).val()===999);
  await assertFails(set(ref(env.unauthenticatedContext().database(),'fdo_v25/formas/f0'),form('f0')));ok('Rules continuam negando gravação sem autorização',true);
  console.log('TESTE EMULATOR FLUXO v26.7 OK — '+count+' verificações');
 }finally{stops.forEach(stop=>stop());await env.cleanup();}
})().catch(e=>{console.error(e);process.exit(1);});
