// ════════════════════════════════════════════════════════════
// v26.0 — RECEITA COMPLETA + CONTROLE DE ESTOQUE
// ════════════════════════════════════════════════════════════
const ESTOQUE_ITENS=[
  {id:'farinha_bagatelle',nome:'Farinha Bagatelle',passo:'Bagatelle',grupo:'insumo',unidade:'g'},
  {id:'farinha_feuilletage',nome:'Farinha Feuilletage',passo:'Feuilletage',grupo:'insumo',unidade:'g'},
  {id:'farinha_italiana00',nome:'Farinha Italiana 00',passo:'Italiana 00',grupo:'insumo',unidade:'g'},
  {id:'fermento_seco',nome:'Fermento seco',passo:'Fermento seco',grupo:'insumo',unidade:'g'},
  {id:'acucar',nome:'Açúcar',passo:'Açúcar',grupo:'insumo',unidade:'g'},
  {id:'sal_refinado',nome:'Sal refinado',passo:'Sal refinado',grupo:'insumo',unidade:'g'},
  {id:'manteiga',nome:'Manteiga',passo:'Manteiga',grupo:'insumo',unidade:'g'},
  {id:'leite_po',nome:'Leite em pó',passo:'Leite em pó',grupo:'insumo',unidade:'g'},
  {id:'caixa_grande',nome:'Caixas Grandes',grupo:'embalagem',unidade:'un'},
  {id:'caixa_aberta',nome:'Caixas Abertas',grupo:'embalagem',unidade:'un'},
  {id:'caixa_mini',nome:'Caixas de Mini',grupo:'embalagem',unidade:'un'}
];
const ESTOQUE_POR_PASSO={};ESTOQUE_ITENS.forEach(x=>{if(x.passo)ESTOQUE_POR_PASSO[x.passo]=x.id;});
function estoqueItem(id){return ESTOQUE_ITENS.find(x=>x.id===id)||null;}
function estoqueInsumos(){return ESTOQUE_ITENS.filter(x=>x.grupo==='insumo');}
function estoqueEmbalagens(){return ESTOQUE_ITENS.filter(x=>x.grupo==='embalagem');}
function estoqueNumero(v){
  const s=String(v==null?'':v).trim().replace(/\s/g,'').replace(',','.');
  if(!s)return null;const n=Number(s);return isFinite(n)?n:null;
}
function estoqueFmt(id,v){
  const it=estoqueItem(id),n=Number(v)||0;
  if(it&&it.unidade==='un')return Math.round(n)+' un';
  const kg=n/1000;
  return kg.toLocaleString('pt-BR',{minimumFractionDigits:kg%1?3:0,maximumFractionDigits:3})+' kg';
}
function estoqueCorDif(v){return Math.abs(Number(v)||0)<1?'var(--grn)':((Number(v)||0)<0?'var(--red)':'var(--gold)');}
function estoqueMovimentos(){return LS.g('fdo_estoque_movimentos',[]);}
function estoqueContagens(){return LS.g('fdo_estoque_contagens',[]);}
function receitaObservacoes(){return LS.g('fdo_receitas_observacoes',[]);}
function receitaObsRegistro(rid){return receitaObservacoes().find(x=>x.id===rid)||null;}
function estoqueTemMovimento(id){return estoqueMovimentos().some(x=>x&&x.id===id);}

const ESTOQUE_SYNC={
  defs:{
    movimentos:{local:'fdo_estoque_movimentos',path:'fdo_v25/estoque/movimentos'},
    contagens:{local:'fdo_estoque_contagens',path:'fdo_v25/estoque/contagens'},
    observacoes:{local:'fdo_receitas_observacoes',path:'fdo_v25/receitas_observacoes'}
  },
  OUT:'fdo_estoque_outbox_v26',iniciado:false,flushing:false,ready:{},inicioTs:0,refs:{},
  clone(v){return v==null?v:JSON.parse(JSON.stringify(v));},
  key(id){return String(id||'sem_id').replace(/[.#$\[\]\/]/g,'_');},
  ts(x){return Math.max(Number(x&&x.atualizadoTs)||0,Number(x&&x.emTs)||0,Number(x&&x.criadoTs)||0);},
  list(nome){const d=this.defs[nome];return d?LS.g(d.local,[]):[];},
  save(nome,arr){const d=this.defs[nome];if(!d)return;try{localStorage.setItem(d.local,JSON.stringify(arr))}catch{}},
  upsert(arr,reg){
    const out=Array.isArray(arr)?arr.slice():[],i=out.findIndex(x=>x&&x.id===reg.id);
    if(i<0)out.push(this.clone(reg));else if(this.ts(reg)>=this.ts(out[i]))out[i]={...this.clone(out[i]),...this.clone(reg)};
    return out.sort((a,b)=>this.ts(b)-this.ts(a));
  },
  out(){const base={movimentos:{},contagens:{},observacoes:{}};const x=LS.g(this.OUT,base)||base;Object.keys(base).forEach(k=>x[k]=x[k]||{});return x;},
  saveOut(x){try{localStorage.setItem(this.OUT,JSON.stringify(x))}catch{}},
  queue(nome,reg){const o=this.out(),id=this.key(reg.id),at=o[nome]&&o[nome][id];if(!at||this.ts(reg)>=this.ts(at))o[nome][id]=this.clone(reg);this.saveOut(o);},
  pending(){const o=this.out();return Object.values(o).some(m=>Object.keys(m||{}).length);},
  localPush(nome,reg){const arr=this.upsert(this.list(nome),reg);this.save(nome,arr);this.queue(nome,reg);FB.repaint();this.flush();},
  apply(nome,val){
    const rem=Object.values((val&&typeof val==='object')?val:{}).filter(x=>x&&x.id),loc=this.list(nome);let arr=rem.slice();
    loc.forEach(x=>{arr=this.upsert(arr,x);if(!rem.some(r=>r.id===x.id))this.queue(nome,x);});
    this.save(nome,arr);this.ready[nome]=true;FB.repaint();this.flush();
    if(nome==='movimentos')estoqueReconciliarSaidasLotes();
  },
  async flush(){
    if(this.flushing||!FB.db||!navigator.onLine)return;const o=this.out(),jobs=[];
    Object.keys(this.defs).forEach(nome=>Object.entries(o[nome]||{}).forEach(([id,reg])=>jobs.push([nome,id,reg])));
    if(!jobs.length)return;this.flushing=true;FB.status('pending','Estoque salvo · sincronizando…');let ok=true;
    for(const [nome,id,reg] of jobs){
      try{
        await FB.db.ref(this.defs[nome].path+'/'+id).transaction(cur=>!cur||this.ts(reg)>=this.ts(cur)?reg:cur,undefined,false);
        const agora=this.out(),cur=agora[nome]&&agora[nome][id];if(cur&&JSON.stringify(cur)===JSON.stringify(reg))delete agora[nome][id];this.saveOut(agora);
      }catch(e){ok=false;console.warn('[ESTOQUE] sync',nome,id,e);}
    }
    this.flushing=false;
    if(this.pending()&&navigator.onLine){setTimeout(()=>this.flush(),0);return;}
    FB.status(ok?'ok':'err',ok?'✓ Sincronizado':'⚠ Estoque salvo aqui · nuvem pendente');
  },
  async garantirInicio(){
    const local=Number(LS.g('fdo_estoque_inicio_ts_v26',0))||Date.now();
    if(!FB.db||!navigator.onLine){this.inicioTs=local;try{localStorage.setItem('fdo_estoque_inicio_ts_v26',JSON.stringify(local))}catch{};return;}
    try{
      const r=await FB.db.ref('fdo_v25/estoque/meta/inicioTs').transaction(cur=>Number(cur)||local,undefined,false);
      this.inicioTs=Number(r.snapshot.val())||local;try{localStorage.setItem('fdo_estoque_inicio_ts_v26',JSON.stringify(this.inicioTs))}catch{};
      estoqueReconciliarSaidasLotes();
    }catch(e){this.inicioTs=local;}
  },
  init(){
    if(this.iniciado||!FB.db)return;this.iniciado=true;
    Object.entries(this.defs).forEach(([nome,d])=>{
      const ref=FB.db.ref(d.path);this.refs[nome]=ref;
      ref.on('value',snap=>this.apply(nome,snap.val()),e=>{console.warn('[ESTOQUE] listen',nome,e);FB.status('err','⚠ Estoque salvo aqui · nuvem pendente');});
    });
    this.garantirInicio();this.flush();
  },
  online(){if(!this.iniciado)this.init();else{this.garantirInicio();this.flush();}}
};

function estoqueConsumoLote(lote){
  const r=receitaDoLote(lote);if(!r||!Array.isArray(r.passos))return null;
  const itens={};
  r.passos.forEach(p=>{
    const id=ESTOQUE_POR_PASSO[p.nome];if(!id)return;
    let g=Number(p.g)||0;if(p.cat==='FERMENTO'){const real=loteFermentoG(lote);if(real!=null)g=Number(real)||0;}
    if(g>0)itens[id]=(itens[id]||0)-g;
  });
  return Object.keys(itens).length?itens:null;
}
function registrarSaidaEstoqueLote(lote){
  if(!lote||!lote.id)return false;const id='saida_receita_'+lote.id;if(estoqueTemMovimento(id))return false;
  const itens=estoqueConsumoLote(lote);if(!itens)return false;
  const ts=Number(lote.criadoTs)||Date.now(),reg={id,tipo:'saida_receita',em:lote.criado||new Date(ts).toLocaleString('pt-BR'),emTs:ts,op:(porcInfo(lote).op||getOp()),loteId:lote.id,loteNum:lote.num,receita:lote.receita,receitaNome:lote.receitaNome||lote.rotulo||'',itens,dispositivo:(typeof DEVICE!=='undefined'?DEVICE.audit():null)};
  ESTOQUE_SYNC.localPush('movimentos',reg);return true;
}
function estoqueReconciliarSaidasLotes(){
  const inicio=Number(ESTOQUE_SYNC.inicioTs||LS.g('fdo_estoque_inicio_ts_v26',0))||0;if(!inicio)return;
  let n=0;LS.g('fdo_lotes',[]).forEach(l=>{if(l&&Number(l.criadoTs)>=inicio&&registrarSaidaEstoqueLote(l))n++;});return n;
}
function estoqueSaldos(){
  const s={};estoqueInsumos().forEach(x=>s[x.id]=0);
  estoqueMovimentos().forEach(m=>Object.entries((m&&m.itens)||{}).forEach(([id,v])=>{if(id in s)s[id]+=Number(v)||0;}));return s;
}
function estoqueUltimaContagem(){return estoqueContagens().slice().sort((a,b)=>(Number(b.emTs)||0)-(Number(a.emTs)||0))[0]||null;}
function estoqueDataCurta(ts){return ts?new Date(ts).toLocaleDateString('pt-BR'):'—';}
function entrarEstoque(){exigeP('estoque',()=>{renderEstoque();ir('estoque');});}
function renderEstoque(){
  estoqueReconciliarSaidasLotes();const saldos=estoqueSaldos(),cont=estoqueUltimaContagem(),fis=(cont&&cont.valores)||{};
  const info=document.getElementById('estoque-ultima');if(info)info.textContent=cont?('Última conferência: '+estoqueDataCurta(cont.emTs)+' · '+(cont.op||'—')):'Ainda não há conferência física semanal.';
  const ins=document.getElementById('estoque-insumos');if(ins)ins.innerHTML=estoqueInsumos().map(it=>{
    const tem=Object.prototype.hasOwnProperty.call(fis,it.id),f=tem?Number(fis[it.id])||0:null,d=tem?f-(Number(saldos[it.id])||0):null;
    return `<div class="est-item"><div class="est-item-top"><b>${_escHtml(it.nome)}</b><span class="est-sistema">Sistema ${estoqueFmt(it.id,saldos[it.id])}</span></div><div class="est-item-sub">${tem?('Conferido '+estoqueFmt(it.id,f)+' · diferença <span style="color:'+estoqueCorDif(d)+'">'+(d>0?'+':'')+estoqueFmt(it.id,d)+'</span>'):'Conferência física: não informada'}</div></div>`;
  }).join('');
  const emb=document.getElementById('estoque-embalagens');if(emb)emb.innerHTML=estoqueEmbalagens().map(it=>`<div class="est-item"><div class="est-item-top"><b>${_escHtml(it.nome)}</b><span class="est-sistema">${Object.prototype.hasOwnProperty.call(fis,it.id)?estoqueFmt(it.id,fis[it.id]):'Não conferido'}</span></div><div class="est-item-sub">Somente saldo físico semanal nesta etapa.</div></div>`).join('');
  const bE=document.getElementById('estoque-btn-entrada'),bC=document.getElementById('estoque-btn-contagem');if(bE)bE.style.display=OP.pode('estoque_entrada')?'':'none';if(bC)bC.style.display=OP.pode('estoque_contagem')?'':'none';
}
function abrirEstoqueEntrada(){
  if(!OP.pode('estoque_entrada')){alert('Você não tem permissão para registrar entradas de estoque.');return;}
  const sel=document.getElementById('estoque-entrada-item');sel.innerHTML=estoqueInsumos().map(x=>`<option value="${x.id}">${_escHtml(x.nome)}</option>`).join('');
  document.getElementById('estoque-entrada-qtd').value='';document.getElementById('estoque-entrada-obs').value='';ir('estoque-entrada');
}
function salvarEstoqueEntrada(){
  if(!OP.pode('estoque_entrada'))return;const id=document.getElementById('estoque-entrada-item').value,it=estoqueItem(id),kg=estoqueNumero(document.getElementById('estoque-entrada-qtd').value);
  if(!it||it.grupo!=='insumo'){alert('Selecione um insumo.');return;}if(kg==null||kg<=0){alert('Informe uma quantidade maior que zero, em kg.');document.getElementById('estoque-entrada-qtd').focus();return;}
  const g=Math.round(kg*1000),agora=new Date(),obs=String(document.getElementById('estoque-entrada-obs').value||'').trim().slice(0,160);
  const reg={id:FB.novoId('est_entrada'),tipo:'entrada',em:agora.toLocaleString('pt-BR'),emTs:agora.getTime(),op:getOp(),itens:{[id]:g},observacao:obs||null,dispositivo:(typeof DEVICE!=='undefined'?DEVICE.audit():null)};
  ESTOQUE_SYNC.localPush('movimentos',reg);alert('Entrada registrada: '+it.nome+' · '+estoqueFmt(id,g)+'.');renderEstoque();ir('estoque');
}
function abrirEstoqueContagem(){
  if(!OP.pode('estoque_contagem')){alert('Você não tem permissão para registrar a conferência semanal.');return;}
  const hoje=new Date(),d=document.getElementById('estoque-cont-data');d.value=hoje.toISOString().slice(0,10);
  const ultima=estoqueUltimaContagem(),ant=(ultima&&ultima.valores)||{};
  document.getElementById('estoque-cont-campos').innerHTML=ESTOQUE_ITENS.map(it=>{
    const ph=Object.prototype.hasOwnProperty.call(ant,it.id)?('Anterior: '+estoqueFmt(it.id,ant[it.id])):(it.unidade==='un'?'Quantidade':'Ex.: 12,5');
    return `<label class="est-cont-field"><span>${_escHtml(it.nome)}</span><input class="inp" data-est-id="${it.id}" type="text" inputmode="decimal" placeholder="${_escHtml(ph)}"><small>${it.unidade==='un'?'unidades':'kg'}</small></label>`;
  }).join('');
  estoqueAtualizarDiaContagem();ir('estoque-contagem');
}
function estoqueAtualizarDiaContagem(){
  const v=document.getElementById('estoque-cont-data').value,el=document.getElementById('estoque-cont-dia');if(!el)return;if(!v){el.textContent='';return;}
  const d=new Date(v+'T12:00:00'),seg=d.getDay()===1;el.textContent=seg?'Segunda-feira · conferência semanal':'Atenção: a data escolhida não é segunda-feira.';el.style.color=seg?'var(--grn)':'var(--gold)';
}
function salvarEstoqueContagem(){
  if(!OP.pode('estoque_contagem'))return;const data=document.getElementById('estoque-cont-data').value;if(!data){alert('Informe a data da conferência.');return;}
  const vals={};for(const inp of document.querySelectorAll('#estoque-cont-campos [data-est-id]')){const id=inp.dataset.estId,it=estoqueItem(id),n=estoqueNumero(inp.value);if(n==null||n<0){alert('Preencha '+(it?it.nome:id)+' com zero ou uma quantidade positiva.');inp.focus();return;}vals[id]=it.unidade==='un'?Math.round(n):Math.round(n*1000);}
  const d=new Date(data+'T12:00:00');if(d.getDay()!==1&&!confirm('A data escolhida não é segunda-feira. Deseja registrar mesmo assim?'))return;
  const agora=new Date(),reg={id:FB.novoId('est_contagem'),tipo:'contagem_semanal',data,em:agora.toLocaleString('pt-BR'),emTs:agora.getTime(),op:getOp(),valores:vals,dispositivo:(typeof DEVICE!=='undefined'?DEVICE.audit():null)};
  ESTOQUE_SYNC.localPush('contagens',reg);alert('Conferência semanal registrada sem alterar o saldo calculado.');renderEstoque();ir('estoque');
}
function renderEstoqueMovimentos(){
  const el=document.getElementById('estoque-mov-lista'),mov=estoqueMovimentos().slice().sort((a,b)=>(Number(b.emTs)||0)-(Number(a.emTs)||0));
  if(!mov.length){el.innerHTML='<div class="est-vazio">Nenhuma entrada ou saída registrada.</div>';return;}
  el.innerHTML=mov.map(m=>{
    const itens=Object.entries(m.itens||{}).map(([id,v])=>{const it=estoqueItem(id);return '<div><b>'+_escHtml(it?it.nome:id)+':</b> '+((Number(v)||0)>0?'+':'')+estoqueFmt(id,v)+'</div>';}).join('');
    const tit=m.tipo==='entrada'?'Entrada recebida':('Saída automática · Balde #'+(m.loteNum||'—'));
    return `<div class="est-mov"><div class="est-mov-title">${_escHtml(tit)}</div><div class="est-mov-meta">${_escHtml(m.em||'')} · ${_escHtml(m.op||'—')}${m.receitaNome?' · '+_escHtml(m.receitaNome):''}</div><div class="est-mov-itens">${itens}</div>${m.observacao?'<div class="est-mov-obs">'+_escHtml(m.observacao)+'</div>':''}</div>`;
  }).join('');
}
function abrirEstoqueMovimentos(){renderEstoqueMovimentos();ir('estoque-mov');}

function abrirReceitaCompleta(rid){if(!RECEITAS[rid])return;st.receitaVisual=rid;renderReceitaCompleta();ir('receita-completa');}
function renderReceitaCompleta(){
  const rid=st.receitaVisual||'r1',r=RECEITAS[rid];if(!r)return;document.getElementById('receita-full-title').textContent=r.nome;
  const ferm=(r.passos||[]).find(p=>p.cat==='FERMENTO'),dinamico=r.fermentoFixo==null,baseTotal=(r.passos||[]).reduce((s,p)=>s+(Number(p.g)||0),0),semFerm=baseTotal-(Number(ferm&&ferm.g)||0);
  document.getElementById('receita-full-total').textContent=dinamico?('Total final: '+formatPeso(semFerm)+' + fermento escolhido'):('Total: '+formatPeso(baseTotal));
  let html='',grupo='';(r.passos||[]).forEach(p=>{if(p.grupo!==grupo){grupo=p.grupo;html+='<div class="rec-full-grupo">'+_escHtml(grupo)+'</div>';}const q=(dinamico&&p.cat==='FERMENTO')?'conforme temperatura / horas':formatPeso(p.g);html+='<div class="rec-full-item"><span>'+_escHtml(p.nome)+'</span><b>'+_escHtml(q)+'</b></div>';});
  if(dinamico)html+='<div class="rec-full-fer"><b>Opções de fermento</b>'+OPCOES_FERMENTO.map(o=>'<span>'+o.temp+'°C · '+o.horas+' h = '+o.fermento+' g</span>').join('')+'</div>';
  document.getElementById('receita-full-lista').innerHTML=html;
  const obs=receitaObsRegistro(rid),ta=document.getElementById('receita-full-obs'),btn=document.getElementById('receita-full-salvar');ta.value=obs&&obs.texto||'';const pode=OP.pode('receita_obs');ta.readOnly=!pode;btn.style.display=pode?'':'none';document.getElementById('receita-full-obs-meta').textContent=obs?('Atualizado em '+(obs.em||'—')+' · '+(obs.op||'—')):(pode?'Nenhuma observação registrada.':'Nenhuma observação registrada pela gerência.');
}
function salvarObservacaoReceita(){
  if(!OP.pode('receita_obs')){alert('Somente a gerência pode alterar as observações das receitas.');return;}const rid=st.receitaVisual||'',r=RECEITAS[rid];if(!r)return;
  const texto=String(document.getElementById('receita-full-obs').value||'').trim().slice(0,1200),agora=new Date(),reg={id:rid,receitaNome:r.nome,texto,em:agora.toLocaleString('pt-BR'),atualizadoTs:agora.getTime(),op:getOp()};ESTOQUE_SYNC.localPush('observacoes',reg);renderReceitaCompleta();alert('Observações da receita salvas.');
}
function garantirPermissoesV260(){
  const arr=OP.lista();if(!arr.length)return;let mudou=false;
  arr.forEach(o=>{o.perms=o.perms||{};const n=String(o.nome||'').trim().toLowerCase();const set=(k,v)=>{if(!Object.prototype.hasOwnProperty.call(o.perms,k)){o.perms[k]=v;mudou=true;}};
    if(n==='wagner'){set('estoque',true);set('estoque_entrada',true);set('estoque_contagem',true);set('receita_obs',true);}
    else if(n==='maycon'){set('estoque',true);set('estoque_entrada',false);set('estoque_contagem',true);set('receita_obs',false);}
    else{set('estoque',false);set('estoque_entrada',false);set('estoque_contagem',false);set('receita_obs',false);}
  });
  if(mudou)OP.setLista(arr);
}
