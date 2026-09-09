const assert=require('assert'),{load,form,plan}=require('./fluxo_v26_7_test_helper');
const A=load(),clone=x=>JSON.parse(JSON.stringify(x));let n=0;
function ok(label,fn){fn();console.log('OK '+(++n)+' '+label);}
function map(...fs){return Object.fromEntries(fs.map(f=>[A.SYNC25.key(f.id),f]));}
function no(m,p,regex){const before=JSON.stringify(m);assert.throws(()=>A.fluxoAplicarPlano(m,p),regex);assert.equal(JSON.stringify(m),before);}
let m=map(...Array.from({length:21},(_,i)=>form('f'+i)));
ok('formadas aguardam; abrir tela não registra estágio',()=>assert.equal(A.fluxoEstadoForma(m.f0),'pronta_fermentar'));
ok('21 formas recusadas sem gravação parcial',()=>no(m,plan('entradaArmario',Object.keys(m)),/20 formas/));
let t=A.fluxoAplicarPlano(m,plan('entradaArmario',Object.keys(m).slice(0,20)));
ok('20 formas aceitas e originais preservadas',()=>{assert.equal(A.fluxoOcupacao(1,Object.values(t)),20);assert(!m.f0.eventos);assert.equal(A.fluxoEstadoForma(t.f0),'fermentando');});
ok('armário cheio rejeita até uma forma',()=>no(t,plan('entradaArmario',['f20']),/20 formas/));
ok('armários independentes',()=>assert.equal(A.fluxoOcupacao(2,Object.values(A.fluxoAplicarPlano(t,plan('entradaArmario',['f20'],11000,{armario:2})))),1));
ok('retry idempotente preserva horários e dados',()=>assert.deepStrictEqual(clone(A.fluxoAplicarPlano(t,plan('entradaArmario',Object.keys(m).slice(0,20)))),clone(t)));
ok('operação diferente não duplica entrada',()=>no(t,plan('entradaArmario',['f0'],12000),/mudou de etapa/));
ok('entrada no forno sem saída é recusada',()=>no(t,plan('assamentoInicio',['f0'],12000),/mudou de etapa/));
let out=A.fluxoAplicarPlano(t,plan('saidaArmario',['f0','f1'],3700000));
ok('saída parcial libera apenas duas vagas',()=>{assert.equal(A.fluxoOcupacao(1,Object.values(out)),18);assert.equal(A.fluxoEstadoForma(out.f0),'aguardando_assamento');assert.equal(A.fluxoEstadoForma(out.f2),'fermentando');});
ok('temperaturas opcionais não ganham valores fictícios',()=>assert(!('tempMin' in out.f0.eventos.saidaArmario)));
ok('temperatura zero legítima preservada',()=>assert.equal(A.fluxoAplicarPlano(t,plan('saidaArmario',['f0'],12000,{tempMin:0,tempMax:0})).f0.eventos.saidaArmario.tempMin,0));
for(const [label,x] of [['max menor', {tempMin:25,tempMax:23}],['NaN',{tempMin:NaN}],['infinita',{tempMax:Infinity}]])ok('recusa temperatura '+label,()=>no(t,plan('saidaArmario',['f0'],12000,x),/Temperatura|máxima/));
let bake=A.fluxoAplicarPlano(out,plan('assamentoInicio',['f0','f1'],3800000)),done=A.fluxoAplicarPlano(bake,plan('assamentoFim',['f0','f1'],4700000));
ok('assamento exige início e fim separados',()=>{assert.equal(A.fluxoEstadoForma(bake.f0),'assando');assert.equal(A.fluxoEstadoForma(done.f0),'assada');assert.equal(A.fluxoEstadoForma(done.f2),'fermentando');});
ok('duração real persiste após serialização',()=>assert.equal(A.fluxoDuracao(clone(done).f0.eventos.entradaArmario.emTs,clone(done).f0.eventos.saidaArmario.emTs),'1h 01min'));
ok('duração de assamento é medida, não prescrição',()=>assert.equal(A.fluxoDuracao(done.f0.eventos.assamentoInicio.emTs,done.f0.eventos.assamentoFim.emTs),'0h 15min'));
for(const [label,p] of [['vazia',plan('entradaArmario',[])],['ids repetidos',plan('entradaArmario',['f0','f0'])],['etapa inválida',plan('x',['f0'])],['sem id operação',plan('entradaArmario',['f0'],1,{operacaoId:''})],['hora inválida',plan('entradaArmario',['f0'],NaN)],['forma ausente',plan('entradaArmario',['f999'])]])ok('rejeita '+label,()=>no(m,p));
for(const armario of [0,-1,1.5,'x',Infinity,'1'])ok('armário inválido '+armario,()=>no(m,plan('entradaArmario',['f0'],10000,{armario})));
ok('horário não pode voltar em etapa seguinte',()=>no(t,plan('saidaArmario',['f0'],9000),/relógio/));
ok('lote balde nunca pode ser forma fermentada',()=>no({b1:{id:'b1',num:1,etapas:{batimento:{feito:true}}}},plan('entradaArmario',['b1']),/quantidade|composição/));
for(const [label,change] of [['apagada',{_deleted:true}],['zero unidades',{totalUnidades:0}],['composição ausente',{composicao:[]}],['saldo incompatível',{totalUnidades:15}],['origem ausente',{composicao:[{unidades:16}]}],['unidades negativas',{composicao:[{partidaId:'p',unidades:-1},{partidaId:'p',unidades:17}]}]])ok('recusa forma '+label,()=>no(map({...form(),...change}),plan('entradaArmario',['f1'])));
ok('grupo com item inválido não movimenta os válidos',()=>no({...m,f20:{...m.f20,_deleted:true}},plan('entradaArmario',['f0','f20'])));
const stale={...clone(m.f0),atualizadoTs:9000000};
ok('sync forma antiga mais recente não apaga etapas',()=>assert.equal(A.fluxoEstadoForma(A.SYNC25.merge('fdo_formas',done.f0,stale)),'assada'));
ok('merge comuta e preserva quatro eventos',()=>{const x=A.SYNC25.merge('fdo_formas',stale,done.f0),y=A.SYNC25.merge('fdo_formas',done.f0,stale);assert.deepStrictEqual(clone(x),clone(y));assert.equal(Object.keys(x.eventos).length,4);});
ok('mesclagem de fatias não passa pelo fluxo de formas',()=>assert.equal(A.SYNC25.merge('fdo_partidas',{id:'p',atualizadoTs:1,qtd:1},{id:'p',atualizadoTs:2,qtd:2}).qtd,2));
ok('registros antigos de balde preservados na sincronização',()=>{const b={id:'b',etapas:{fermentacao:{feito:true,emTs:30,tempMin:24}}};assert.deepStrictEqual(clone(A.SYNC25.merge('fdo_lotes',b,{id:'b',atualizadoTs:40})).etapas,b.etapas);});
ok('estado inconsistente é sinalizado, não avançado',()=>{assert.equal(A.fluxoEstadoForma({...form(),eventos:{assamentoFim:{emTs:4}}}),'conferir');assert.equal(A.fluxoEstadoForma({...form(),eventos:{entradaArmario:{emTs:4,armario:1},saidaArmario:{emTs:3}}}),'conferir');});
console.log('TESTE FLUXO v26.7 OK — '+n+' verificações');
