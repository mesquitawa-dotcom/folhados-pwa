const fs = require('fs');
const assert = require('assert');
const {
  initializeTestEnvironment,
  assertSucceeds,
  assertFails,
} = require('@firebase/rules-unit-testing');
const { ref, set, get, update, remove } = require('firebase/database');

const PROJECT_ID = 'demo-fdo-rules';
const RULES = fs.readFileSync('database.rules.json', 'utf8');

async function ok(label, promise) {
  const result = await assertSucceeds(promise);
  console.log('OK   ' + label);
  return result;
}
async function no(label, promise) {
  await assertFails(promise);
  console.log('DENY ' + label);
}
function canon(v){
  if(Array.isArray(v))return v.map(canon);
  if(v&&typeof v==='object'){
    const out={};Object.keys(v).sort().forEach(k=>out[k]=canon(v[k]));return out;
  }
  return v;
}
function iguais(a,b){return JSON.stringify(canon(a))===JSON.stringify(canon(b));}
async function syncImutavel(db,path,reg){
  const r=ref(db,path);
  let remoto=(await get(r)).val();
  if(remoto==null){
    try{await set(r,reg);remoto=reg;}
    catch(e){remoto=(await get(r)).val();if(!iguais(remoto,reg))throw e;}
  }
  return {igual:iguais(remoto,reg),remoto};
}

(async () => {
  const env = await initializeTestEnvironment({projectId:PROJECT_ID,database:{rules:RULES}});
  try {
    await env.withSecurityRulesDisabled(async (ctx) => {
      const db=ctx.database();
      await set(ref(db,'fdo_dispositivos/device-ok'),{ativo:true,nome:'Teste autorizado'});
      await set(ref(db,'fdo_dispositivos/device-off'),{ativo:false,nome:'Teste não autorizado'});
    });
    const anon=env.unauthenticatedContext().database();
    const off=env.authenticatedContext('device-off').database();
    const app=env.authenticatedContext('device-ok').database();

    await no('anônimo não lê produção',get(ref(anon,'fdo_v25/lotes')));
    await no('anônimo não grava produção',set(ref(anon,'fdo_v25/lotes/lote_anon'),{id:'lote_anon'}));
    await no('aparelho não autorizado não lê produção',get(ref(off,'fdo_v25/lotes')));
    await no('aparelho não autorizado não grava produção',set(ref(off,'fdo_v25/lotes/lote_off'),{id:'lote_off'}));

    await ok('aparelho lê o próprio cadastro',get(ref(app,'fdo_dispositivos/device-ok')));
    await no('aparelho não lê cadastro de outro UID',get(ref(app,'fdo_dispositivos/device-off')));
    await no('aparelho não altera autorização do próprio UID',update(ref(app,'fdo_dispositivos/device-ok'),{ativo:false}));

    await ok('balde canônico continua gravável',set(ref(app,'fdo_v25/lotes/lote_1'),{id:'lote_1',num:1}));
    await ok('laminação canônica continua gravável',set(ref(app,'fdo_v25/laminacoes/lam_1'),{id:'lam_1'}));
    await ok('metadados transacionais continuam graváveis',set(ref(app,'fdo_v25/meta/lote_seq'),12));
    await ok('sequência de receita continua gravável',set(ref(app,'fdo_v25/receitas_meta/seq'),6));
    await no('caminho canônico desconhecido fica fechado',set(ref(app,'fdo_v25/caminho_nao_previsto'),true));

    await ok('ponte legada de baldes continua gravável',set(ref(app,'fdo_lotes'),[{id:'legado_1',num:1}]));
    await ok('operadores continuam sincronizáveis',set(ref(app,'fdo_operadores'),[{id:'op_1',nome:'Teste',ativo:true}]));
    await ok('lotes atuais de farinha continuam sincronizáveis',set(ref(app,'fdo_farinha_lotes_atuais'),{bagatelle:'A'}));

    await ok('receita definitiva pode nascer',set(ref(app,'fdo_v25/receitas_definitivas/r6'),{id:'r6',versao:1}));
    await ok('receita definitiva pode ser versionada',update(ref(app,'fdo_v25/receitas_definitivas/r6'),{versao:2}));
    await ok('observações de receita continuam graváveis',set(ref(app,'fdo_v25/receitas_observacoes/r6'),{id:'r6',texto:'Teste'}));
    await ok('configuração de estoque continua gravável',set(ref(app,'fdo_v25/estoque/configuracoes/geral'),{dia:1}));
    await ok('contagem de estoque continua gravável',set(ref(app,'fdo_v25/estoque/contagens/cont_1'),{id:'cont_1',emTs:1}));
    await ok('meta de estoque continua gravável',set(ref(app,'fdo_v25/estoque/meta/inicioTs'),1));

    const audit={id:'aud_1',tipo:'editada',emTs:100,motivo:'teste regras'};
    const auditPath='fdo_v25/receitas_auditoria/aud_1';
    await ok('auditoria de receita pode ser criada',set(ref(app,auditPath),audit));
    await no('set repetido da auditoria não regrava histórico',set(ref(app,auditPath),audit));
    const auditRetry=await syncImutavel(app,auditPath,audit);
    assert.strictEqual(auditRetry.igual,true,'retry deve reconhecer remoto igual sem escrever');
    console.log('OK   retry idempotente da auditoria é reconhecido por leitura');
    const auditConflito=await syncImutavel(app,auditPath,{...audit,motivo:'conteúdo diferente'});
    assert.strictEqual(auditConflito.igual,false,'mesmo ID divergente deve ser conflito');
    console.log('OK   mesmo ID com conteúdo diferente vira conflito, não sobrescrita');
    await no('auditoria de receita não pode ser alterada',update(ref(app,auditPath),{motivo:'adulterado'}));
    await no('auditoria de receita não pode ser apagada',remove(ref(app,auditPath)));

    const auditNovo={id:'aud_2',tipo:'criada',emTs:200,motivo:'novo'};
    const auditNovoSync=await syncImutavel(app,'fdo_v25/receitas_auditoria/aud_2',auditNovo);
    assert.strictEqual(auditNovoSync.igual,true);
    assert(iguais((await get(ref(app,'fdo_v25/receitas_auditoria/aud_2'))).val(),auditNovo));
    console.log('OK   cliente cria histórico ausente sob Rule append-only');

    const mov={id:'mov_1',tipo:'entrada',emTs:100,itens:{farinha:10}};
    const movPath='fdo_v25/estoque/movimentos/mov_1';
    await ok('movimento de estoque pode ser criado',set(ref(app,movPath),mov));
    await no('set repetido do movimento não regrava histórico',set(ref(app,movPath),mov));
    const movRetry=await syncImutavel(app,movPath,mov);
    assert.strictEqual(movRetry.igual,true);
    console.log('OK   retry idempotente do movimento é reconhecido por leitura');
    await no('movimento de estoque não pode ser alterado',update(ref(app,movPath),{tipo:'adulterado'}));
    await no('movimento de estoque não pode ser apagado',remove(ref(app,movPath)));

    const acesso={ts:100,status:'ok',operador:'Teste'};
    const acessoPath='fdo_acessos/acesso_1';
    await ok('log de acesso pode ser criado',set(ref(app,acessoPath),acesso));
    await no('log de acesso não pode ser regravado',set(ref(app,acessoPath),acesso));
    await no('log de acesso não pode ser alterado',update(ref(app,acessoPath),{status:'fora'}));
    await no('log de acesso não pode ser apagado',remove(ref(app,acessoPath)));
    await no('log de acesso continua sem leitura pelo cliente',get(ref(app,acessoPath)));

    console.log('FIREBASE RULES v26.4 OK · aparelho autorizado preservado · trilhas históricas append-only');
  } finally {await env.cleanup();}
})().catch(err=>{console.error(err);process.exit(1);});
