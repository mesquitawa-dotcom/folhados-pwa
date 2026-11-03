const fs=require('fs'),assert=require('assert'),vm=require('vm');
const src=fs.readFileSync('index.html','utf8');
let n=0;
function ok(nome,fn){fn();console.log('OK '+(++n)+' '+nome);}
function plain(x){return JSON.parse(JSON.stringify(x));}

const ini=src.indexOf('const APROV_R2_PERFIL=');
const fim=src.indexOf('// Escolhe qual receita rodar',ini);
assert(ini>=0&&fim>ini,'bloco de cálculo do reaproveitamento não encontrado');
const bloco=src.slice(ini,fim)+'\nthis.__calc=aprovCalcularR2;this.__perfil=APROV_R2_PERFIL;';
const ctx={Math,Number,console};vm.createContext(ctx);vm.runInContext(bloco,ctx);
const calc=ctx.__calc,perfil=ctx.__perfil;

ok('perfil R2 usa padrão verificado de 3.000 g',()=>assert.equal(perfil.padrao_g,3000));
ok('3.000 g preserva os pesos vigentes da R2',()=>assert.deepStrictEqual(plain(calc(3000)),{
  bag:3500,feu:0,ita:4280,acucar:878,agua:3580,leite:174,manteiga:0,sal:174,aprov:3000
}));
ok('1.200 g reproduz o cenário operacional arredondado para balança de 2 g',()=>assert.deepStrictEqual(plain(calc(1200)),{
  bag:3870,feu:0,ita:4730,acucar:970,agua:3950,leite:194,manteiga:428,sal:194,aprov:1200
}));
ok('1.500 g produz uma execução intermediária coerente',()=>assert.deepStrictEqual(plain(calc(1500)),{
  bag:3806,feu:0,ita:4654,acucar:954,agua:3890,leite:194,manteiga:358,sal:194,aprov:1500
}));
ok('0 g reproduz a receita sem massa reaproveitada',()=>assert.deepStrictEqual(plain(calc(0)),{
  bag:4112,feu:0,ita:5028,acucar:1030,agua:4200,leite:204,manteiga:714,sal:204,aprov:0
}));
ok('cálculo recusa quantidade negativa',()=>assert.equal(calc(-2),null));
ok('cálculo recusa acima do padrão verificado',()=>assert.equal(calc(3002),null));

ok('entrada operacional exige passo de 2 g',()=>{
  assert(src.includes('id="aprov-qtd"'));
  assert(src.includes('step="2"'));
  assert(src.includes("g%2!==0"));
});
ok('fórmula automática fica limitada à R2 verificada',()=>{
  assert(src.includes("if(rid!=='r2'||!r)return null;"));
  assert(src.includes("campos.every(k=>Number(v[k])===Number(esperado[k]))"));
});
ok('receita definitiva não é alterada; execução usa cópia própria',()=>{
  assert(src.includes('st.aprovBaseReceita=clonarReceita(st.receitaExecucao)'));
  assert(src.includes('st.receitaExecucao=rec;'));
  assert(src.includes('rec.aproveitamentoExecucao='));
});
ok('snapshot e porcionamento registram reaproveitamento executado',()=>{
  assert(src.includes('lote.receitaSnapshot=clonarReceita(r)'));
  assert(src.includes('aproveitamento:r.aproveitamentoExecucao?clonarReceita(r.aproveitamentoExecucao):null'));
});
ok('histórico mostra massa reaproveitada e padrão',()=>{
  assert(src.includes("massa reaprov. '+formatPeso"));
  assert(src.includes("+' · padrão '+formatPeso"));
});
ok('vários baldes mostram total de massa reaproveitada necessária',()=>{
  assert(src.includes('id="baldes-aprov-total"'));
  assert(src.includes("Massa reaproveitada necessária: '+formatPeso(Number(ap.usado_g)*n)"));
});

ok('navegação possui trava contra pingue-pongue ao voltar',()=>{
  assert(src.includes('voltando:false'));
  assert(src.includes('if(UX_NAV.voltando){UX_NAV.voltando=false;return;}'));
  assert(src.includes('UX_NAV.voltando=true;ir(alvo);'));
});
ok('fluxo de porcionamento tem retornos semânticos definidos',()=>{
  assert(src.includes("if(atual==='aproveitamento')"));
  assert(src.includes("if(atual==='farinha-lotes')"));
  assert(src.includes("if(atual==='pre-temp')"));
  assert(src.includes("if(atual==='temp')"));
});
ok('telas preparatórias recebem saída para Início quando necessário',()=>{
  assert(src.includes("home.textContent='⌂ Início'"));
  assert(src.includes('uxPodeInicioRapido'));
});
ok('tela de reaproveitamento oferece Início explícito',()=>{
  const tela=src.slice(src.indexOf('id="s-aproveitamento"'),src.indexOf('<!-- ═══ RECEITA COMPLETA',src.indexOf('id="s-aproveitamento"')));
  assert(tela.includes("onclick=\"ir('start')\""));
});

console.log('TESTE v26.8 OK — '+n+' verificações');
