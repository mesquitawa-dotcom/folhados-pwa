const fs=require('fs');
const assert=require('assert');

const html=fs.readFileSync('index.html','utf8');
const ini=html.indexOf('const SYNC25={');
const fim=html.indexOf('\nFB.init=',ini);
if(ini<0||fim<0) throw new Error('Bloco SYNC25 não encontrado');
const bloco=html.slice(ini,fim)+"\nglobalThis.__SYNC25=SYNC25;";

const mem=new Map();
globalThis.localStorage={
  getItem:k=>mem.has(k)?mem.get(k):null,
  setItem:(k,v)=>mem.set(k,String(v)),
  removeItem:k=>mem.delete(k)
};
globalThis.LS={
  g:(k,d)=>{try{const v=localStorage.getItem(k);return v===null?d:JSON.parse(v)}catch{return d}},
  s:(k,v)=>localStorage.setItem(k,JSON.stringify(v))
};
Object.defineProperty(globalThis,'navigator',{value:{onLine:true},configurable:true});
globalThis.loteAtivo=l=>{if(!l)return false;const c=Number(l.cancelado&&l.cancelado.emTs)||0,r=Number(l.restaurado&&l.restaurado.emTs)||0;return !c||r>c};
globalThis.dataCurta=ts=>{const d=new Date(ts);return d.toLocaleDateString('pt-BR',{day:'2-digit',month:'2-digit'})};
globalThis.getOp=()=> 'TESTE';
globalThis.FB={applying:false,db:null,status(){},repaint(){}};
globalThis.DEVICE={aprovado:true};

eval(bloco);
const S=globalThis.__SYNC25;

function clone(v){return v==null?v:JSON.parse(JSON.stringify(v))}
const dbStore={};
function parts(path){return String(path||'').split('/').filter(Boolean)}
function getPath(path){let x=dbStore;for(const p of parts(path)){if(x==null||typeof x!=='object'||!(p in x))return null;x=x[p]}return clone(x)}
function setPath(path,val){const ps=parts(path);let x=dbStore;for(let i=0;i<ps.length-1;i++)x=x[ps[i]]||(x[ps[i]]={});if(!ps.length)throw new Error('root set não usado');x[ps.at(-1)]=clone(val)}
class Snap{
  constructor(v){this.v=clone(v)}
  val(){return clone(this.v)}
  child(k){return new Snap(this.v&&typeof this.v==='object'?this.v[k]:null)}
}
class Ref{
  constructor(path){this.path=path}
  async transaction(fn){const cur=getPath(this.path),next=fn(clone(cur));if(next===undefined)return {committed:false,snapshot:new Snap(cur)};setPath(this.path,next);return {committed:true,snapshot:new Snap(next)}}
  async set(v){setPath(this.path,v);return null}
  on(){return null}
}
FB.db={ref:path=>new Ref(path)};

// 1) Merge por etapa: atualizações independentes não podem se apagar.
{
  const a={id:'l1',criadoTs:1,etapas:{porcionamento_secos:{feito:true,emTs:10,temp:18},batimento:{feito:true,emTs:20,peso:100}}};
  const b={id:'l1',criadoTs:1,etapas:{porcionamento_secos:{feito:true,emTs:10,temp:18},fermentacao:{feito:true,emTs:30,tempMin:24}}};
  const m=S.merge('fdo_lotes',a,b);
  assert(m.etapas.batimento&&m.etapas.fermentacao,'merge perdeu etapa independente');
}

// 2) Outbox: ACK de envio antigo não pode apagar uma alteração mais nova feita durante o envio.
{
  mem.clear();
  const a={id:'l1',criadoTs:1,etapas:{batimento:{feito:true,emTs:10,peso:100}}};
  const b={id:'l1',criadoTs:1,etapas:{batimento:{feito:true,emTs:20,peso:110}}};
  S.queue('fdo_lotes',a);
  const enviado=clone(S.out().fdo_lotes.l1);
  S.queue('fdo_lotes',b);
  S.ack('fdo_lotes','l1',enviado);
  assert(S.out().fdo_lotes.l1.etapas.batimento.peso===110,'ACK antigo apagou alteração nova');
  const atual=clone(S.out().fdo_lotes.l1);
  S.ack('fdo_lotes','l1',atual);
  assert(!S.out().fdo_lotes.l1,'ACK atual não limpou outbox');
}

// 3) Tombstone: um registro antigo não pode ressuscitar uma laminação apagada.
{
  const old={id:'lam1',dataTs:100,composicao:[]};
  const tomb={id:'lam1',_deleted:true,deletedTs:200};
  assert(S.merge('fdo_laminacoes',old,tomb)._deleted===true,'tombstone não venceu dado antigo');
  assert(S.merge('fdo_laminacoes',tomb,old)._deleted===true,'tombstone dependeu da ordem do merge');
}

// 4) Laminação online: duas operações não podem consumir as mesmas partes.
(async()=>{
  dbStore.fdo_v25={laminacoes:{},meta:{lote_seq:10}};
  const cap={L1:4};
  const lam1={id:'lam_a',dataTs:100,composicao:[{loteId:'L1',loteNum:1,partes:4}]};
  const lam2={id:'lam_b',dataTs:101,composicao:[{loteId:'L1',loteNum:1,partes:1}]};
  const r1=await S.criarLaminacaoAtomica(lam1,cap);
  assert(r1.ok,'primeira reserva deveria passar');
  const r2=await S.criarLaminacaoAtomica(lam2,cap);
  assert(!r2.ok,'segunda reserva excedente deveria ser bloqueada');

  // Apagada a primeira laminação (tombstone), as partes podem ser usadas novamente.
  dbStore.fdo_v25.laminacoes.lam_a={id:'lam_a',_deleted:true,deletedTs:200};
  const r3=await S.criarLaminacaoAtomica(lam2,cap);
  assert(r3.ok,'tombstone deveria liberar as partes');

  // 5) Contador online: transações consecutivas têm números únicos.
  mem.set('fdo_lote_seq','10');
  dbStore.fdo_v25.meta.lote_seq=10;
  const n1=await S.proxLoteNum();
  const n2=await S.proxLoteNum();
  assert(n1.num===11&&n2.num===12,'contador transacional não foi sequencial');
  assert(n1.origem==='transacao'&&n2.origem==='transacao','contador online caiu para modo offline');

  console.log('TESTES SYNC v25.1 OK');
})().catch(e=>{console.error(e);process.exit(1)});
