// Extrai o núcleo real do index.html; não mantém uma segunda implementação.
const fs=require('fs'),vm=require('vm');
function load(){
 const src=fs.readFileSync('index.html','utf8'),clone=x=>x==null?x:JSON.parse(JSON.stringify(x));
 const core=src.slice(src.indexOf('const FLUXO267='),src.indexOf('function abrirFermentacaoLotes'));
 const sync=src.slice(src.indexOf('const SYNC25='),src.indexOf('\nFB.init=()=>DEVICE.bootstrap'));
 const ctx={console,Date,Number,Object,JSON,Set,Array,clonarReceita:clone};vm.createContext(ctx);
 vm.runInContext(core+'\n'+sync+'\nglobalThis.api={FLUXO267,fluxoAplicarPlano,fluxoEstadoForma,fluxoOcupacao,fluxoDuracao,fluxoMergeForma,SYNC25};',ctx);
 return ctx.api;
}
function form(id='f1'){return {id,nome:id,criadoTs:1000,totalUnidades:16,composicao:[{partidaId:'p1',unidades:16}]};}
function plan(etapa,ids,emTs=10000,extra={}){return {etapa,ids,emTs,operacaoId:etapa+'-'+emTs,op:'Teste',operadorId:'teste',dispositivo:{uid:'teste'},armario:1,...extra};}
module.exports={load,form,plan};
