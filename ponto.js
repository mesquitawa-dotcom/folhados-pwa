'use strict';
// Folhados d'Ouro — Ponto piloto. Módulo isolado, sem alterações nas receitas.
const PONTO_FIREBASE_CFG={
  apiKey:"AIzaSyDN3uZEjtmKE678io-61aIhgFnkxG1PrnE",
  authDomain:"producaofolhadosdouro-b6fb5.firebaseapp.com",
  databaseURL:"https://producaofolhadosdouro-b6fb5-default-rtdb.firebaseio.com",
  projectId:"producaofolhadosdouro-b6fb5",
  storageBucket:"producaofolhadosdouro-b6fb5.firebasestorage.app",
  messagingSenderId:"904726497964",
  appId:"1:904726497964:web:03b4b9111ff0ff2580ed09"
};
const PONTO_APP_CHECK_KEY='6LcPFJ8tAAAAAFk2yg6aQ5Qi0NNMERW220URnH2A';
const $=id=>document.getElementById(id);
const xhtml=v=>String(v==null?'':v).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const txt=(id,v)=>{const el=$(id);if(el)el.textContent=String(v==null?'':v)};
const show=(id,yes=true)=>{const el=$(id);if(el)el.classList.toggle('off',!yes)};
const pad=n=>String(n).padStart(2,'0');
const mesAtual=()=>new Date().toLocaleDateString('sv-SE',{timeZone:'America/Sao_Paulo'}).slice(0,7);
const dataBR=ts=>new Date(ts).toLocaleDateString('sv-SE',{timeZone:'America/Sao_Paulo'});
const horaBR=ts=>new Date(ts).toLocaleTimeString('pt-BR',{timeZone:'America/Sao_Paulo',hour:'2-digit',minute:'2-digit'});
const horas=mins=>{const v=Math.max(0,Math.round(mins||0));return Math.floor(v/60)+'h'+pad(v%60)};
const diaSemana=date=>new Date(date+'T12:00:00-03:00').getUTCDay();
const dinheiro=cent=>((Number(cent)||0)/100).toLocaleString('pt-BR',{style:'currency',currency:'BRL'});
const idNovo=()=>Date.now().toString(36)+'-'+Math.random().toString(36).slice(2,12);
const tipos=['entrada','inicio_intervalo','fim_intervalo','saida'];
const gpsBase={lat:-20.5294456,lng:-47.3940625,raio:150};
function distM(a,b,c,d){const R=6371000;const v=(c-a)*Math.PI/180,w=(d-b)*Math.PI/180,t=a*Math.PI/180,u=c*Math.PI/180;const z=Math.sin(v/2)**2+Math.cos(t)*Math.cos(u)*Math.sin(w/2)**2;return Math.round(2*R*Math.atan2(Math.sqrt(z),Math.sqrt(1-z)))}
function vigentes(versoes,dia){const ds=Object.keys(versoes||{}).filter(d=>d<=dia).sort();return ds.length?versoes[ds[ds.length-1]]:null}
function hashLeve(s){let h=2166136261;for(const c of s){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return(h>>>0).toString(16)}
function ultimo(a){return Object.keys(a||{}).sort().map(k=>a[k]).filter(Boolean).at(-1)||null}
const P={
 db:null,auth:null,uid:'',gerente:false,funcId:'',perfil:null,pares:{},colabs:{},regras:{},salarios:{},avisos:{},marcacoes:{},aprovacoes:{},solicitacoes:{},solucoes:{},conferencias:{},fechamentos:{},area:{...gpsBase},offset:null,fila:[],emEnvio:false,carregando:false,
 status(msg,tipo=''){const e=$('mensagem');e.textContent=msg;e.className='status '+tipo},
 cache(){try{return JSON.parse(localStorage.getItem('fdo_ponto_sess_v1')||'null')}catch{return null}},
 cacheSalvar(){try{localStorage.setItem('fdo_ponto_sess_v1',JSON.stringify({uid:this.uid,funcId:this.funcId,perfil:this.perfil,area:this.area}))}catch(e){this.status('Armazenamento indisponível. Não registre ponto neste aparelho.','err')}},
 lerFila(){try{const v=JSON.parse(localStorage.getItem('fdo_ponto_fila_v1')||'[]');return Array.isArray(v)?v:[]}catch{return []}},
 gravarFila(){localStorage.setItem('fdo_ponto_fila_v1',JSON.stringify(this.fila))},
 async init(){
  $('mes-func').value=mesAtual();$('mes-ger').value=mesAtual();
  $('emp-vigencia').value=dataBR(Date.now());
  const nomes=['Dom','Seg','Ter','Qua','Qui','Sex','Sáb'];
  $('dias-cadastro').innerHTML=nomes.map((nome,i)=>'<label class="field"><span>'+nome+' (minutos)</span><input id="jornada-'+i+'" type="number" min="0" max="1440" placeholder="Não definida"></label>').join('');
  if(typeof firebase==='undefined'||!firebase.auth||!firebase.database){this.status('Firebase indisponível. Tente atualizar o aplicativo.','err');return}
  try{
   if(!firebase.apps.length)firebase.initializeApp(PONTO_FIREBASE_CFG);
   try{if(firebase.appCheck&&firebase.appCheck.ReCaptchaEnterpriseProvider)firebase.appCheck().activate(new firebase.appCheck.ReCaptchaEnterpriseProvider(PONTO_APP_CHECK_KEY),true)}catch(e){console.warn('[PONTO] App Check indisponível',e.message)}
   this.auth=firebase.auth();this.db=firebase.database();await this.auth.setPersistence(firebase.auth.Auth.Persistence.LOCAL);
   const user=await new Promise(resolve=>{const unsub=this.auth.onAuthStateChanged(u=>{unsub();resolve(u)})});
   const cred=user?{user}:await this.auth.signInAnonymously();this.uid=cred.user.uid;txt('uid',this.uid);
   this.fila=this.lerFila().filter(v=>v.uid===this.uid);
   const cache=this.cache();
   if(!navigator.onLine){
    if(cache&&cache.uid===this.uid&&cache.funcId){this.funcId=cache.funcId;this.perfil=cache.perfil;this.area=cache.area||this.area;this.marcacoes={};this.telaFuncionario();this.status('Sem internet: registros ficarão pendentes de sincronização.','err')}
    else this.status('Conecte-se à internet para confirmar o acesso.','err');
   }else await this.recarregar();
   window.addEventListener('online',()=>this.recarregar());
  }catch(e){console.error('[PONTO] início',e);this.status('Não foi possível iniciar. Confira a internet e a autorização do aparelho.','err')}
 },
 async recarregar(){
  if(!navigator.onLine){this.status('Sem internet: registros locais ficam pendentes.','err');return}
  try{
   const snap=await this.db.ref('fdo_ponto_gerentes/'+this.uid).once('value');
   this.gerente=!!(snap.val()&&snap.val().ativo===true);
   const off=await this.db.ref('.info/serverTimeOffset').once('value');this.offset=Number(off.val())||0;
   if(this.gerente){show('ativacao',false);show('funcionario',false);show('gerencia');await this.atualizarGerencia();this.aba('resumo')}
   else{
    const link=(await this.db.ref('fdo_ponto_vinculos/'+this.uid).once('value')).val();
    if(!link||link.ativo!==true){this.funcId='';show('ativacao');show('funcionario',false);show('gerencia',false);this.status('Celular ainda não autorizado pela gerência.');return}
    this.funcId=link.funcionarioId;await this.atualizarFuncionario();
   }
   await this.sincronizarFila();
  }catch(e){console.warn('[PONTO] acesso',e);this.status('Falha ao verificar autorização. Nenhuma permissão foi presumida.','err')}
 },
 async copiarUID(){try{await navigator.clipboard.writeText(this.uid);this.status('Código copiado.')}catch{this.status('Selecione o código na tela para copiar.')}},

 async atualizarFuncionario(){
  if(!this.funcId)return;
  try{
   const root=this.db.ref;
   const caminhos=['fdo_ponto_colaboradores/'+this.funcId,'fdo_ponto_marcacoes/'+this.funcId,'fdo_ponto_aprovacoes/'+this.funcId,'fdo_ponto_conferencias/'+this.funcId,'fdo_ponto_regras/'+this.funcId,'fdo_ponto_avisos_gerais','fdo_ponto_avisos_individuais/'+this.funcId,'fdo_ponto_config/area'];
   const dados=await Promise.all(caminhos.map(p=>this.db.ref(p).once('value').then(s=>s.val()).catch(()=>null)));
   if(!dados[0]||dados[0].ativo!==true){this.funcId='';show('funcionario',false);show('ativacao');this.status('Cadastro do funcionário inativo ou indisponível.','err');return}
   this.perfil=dados[0];this.marcacoes=dados[1]||{};this.aprovacoes=dados[2]||{};this.conferencias=dados[3]||{};this.regras=dados[4]||{};
   this.avisos={gerais:dados[5]||{},individuais:dados[6]||{}};this.area=dados[7]||this.area;this.cacheSalvar();this.telaFuncionario();
   this.status('Acesso autorizado. Registre sua entrada ou saída normalmente.','ok');
  }catch(e){this.status('Erro ao carregar seus registros. Tente novamente.','err');console.warn(e)}
 },
 telaFuncionario(){show('ativacao',false);show('gerencia',false);show('funcionario');this.renderFuncionario()},
 eventosFuncionario(){
  const obj={...this.marcacoes};
  this.fila.filter(v=>v.funcionarioId===this.funcId).forEach(v=>{obj[v.id]=v.registro});
  return obj;
 },
 ultimaMarcacao(){
  const a=Object.values(this.eventosFuncionario()).filter(e=>tipos.includes(e.tipo)).sort((u,v)=>u.clienteTs-v.clienteTs);
  return a.length?a[a.length-1]:null;
 },
 proximaAcao(){
  const anterior=this.ultimaMarcacao();
  if(!anterior||anterior.tipo==='saida')return'entrada';
  if(anterior.tipo==='inicio_intervalo')return'fim_intervalo';
  return'saida';
 },
 renderFuncionario(){
  if(!this.perfil)return;
  txt('nome-func',this.perfil.nome);txt('data-func',new Date().toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo',dateStyle:'full'}));
  const next=this.proximaAcao();
  txt('principal',({entrada:'REGISTRAR ENTRADA',saida:'REGISTRAR SAÍDA',fim_intervalo:'RETORNAR DO INTERVALO'})[next]);
  const pausa=next==='saida';show('intervalo',pausa);
  txt('estado-func',next==='entrada'?'Fora do expediente':next==='saida'?'Jornada iniciada': 'Em intervalo');
  const mes=$('mes-func').value||mesAtual(),dados=this.resumoMes(this.funcId,mes);
  txt('horas-func',horas(dados.confirmados));txt('pend-func',horas(dados.provisorios));
  $('dias-func').innerHTML=this.tabelaDias(dados);
  const conf=ultimo((this.conferencias||{})[mes]),finger=this.fingerprint(this.funcId,mes);
  txt('conf-func',conf?(conf.resumo===finger?'✓ Conferência registrada':'Relatório alterado: confira novamente'):'Conferência ainda não registrada');
  const all=Object.values(this.avisos.gerais||{}).concat(Object.values(this.avisos.individuais||{})).sort((a,b)=>(b.clienteTs||0)-(a.clienteTs||0)).slice(0,15);
  $('avisos-func').innerHTML=all.length?all.map(o=>'<div class="list-row">'+xhtml(o.texto)+'<div class="tiny">'+xhtml(dataBR(o.clienteTs))+'</div></div>').join(''):'<div class="muted">Sem avisos.</div>';
  const pediu=new URLSearchParams(location.search).get('acao');
  if(pediu&&pediu!==next&&tipos.includes(pediu))txt('feedback','O QR solicitou outra ação. Confira o botão exibido antes de registrar.');
 },
 async gpsAgora(){
  if(!navigator.geolocation)return{situacao:'indisponivel'};
  const p=await new Promise(resolve=>navigator.geolocation.getCurrentPosition(resolve,()=>resolve(null),{enableHighAccuracy:true,timeout:13000,maximumAge:0}));
  if(!p||!p.coords)return{situacao:'indisponivel'};
  const c=p.coords,g=this.area||gpsBase,d=distM(c.latitude,c.longitude,Number(g.lat),Number(g.lng)),prec=Math.round(c.accuracy||99999),raio=Number(g.raio)||gpsBase.raio;
  const situacao=prec>Math.min(100,raio/2)?'impreciso':(d+prec<=raio?'dentro':'fora');
  return{situacao,distancia:d,precisao:prec,...(situacao==='dentro'?{}:{lat:Number(c.latitude.toFixed(6)),lng:Number(c.longitude.toFixed(6))})};
 },
 async registrarPrincipal(){await this.registrar(this.proximaAcao())},
 async registrarIntervalo(){await this.registrar('inicio_intervalo')},
 async registrar(tipo){
  if(this.gerente||!this.funcId||!this.perfil||!tipos.includes(tipo)||this.registrando)return;
  if(tipo!==this.proximaAcao()&&!(tipo==='inicio_intervalo'&&this.proximaAcao()==='saida')){this.status('Sequência de ponto incompatível; confira a marcação anterior.','err');return}
  this.registrando=true;$('principal').disabled=true;show('intervalo',false);
  try{
   txt('feedback','Verificando a localização para registrar o horário...');
   const geo=await this.gpsAgora(),offline=!navigator.onLine,relogio=this.offset===null||Math.abs(this.offset)>300000;
   const status=offline?'sem_internet':relogio?'relogio':geo.situacao==='dentro'?'normal':'pendente';
   const registro={tipo,uid:this.uid,clienteTs:Date.now(),servidorTs:firebase.database.ServerValue.TIMESTAMP,gps:geo,avaliacao:status,origem:'celular'};
   const id=this.db.ref('fdo_ponto_marcacoes/'+this.funcId).push().key;
   const item={id,uid:this.uid,funcionarioId:this.funcId,registro};
   this.fila.push(item);
   try{this.gravarFila()}catch{this.fila.pop();throw new Error('Falha ao salvar marcação no aparelho. Nenhum ponto foi registrado.')}
   this.marcacoes[id]=registro;
   this.renderFuncionario();
   if(!offline)await this.sincronizarFila();
   const pendente=status!=='normal';
   txt('feedback',offline?'Registro salvo neste aparelho, aguardando sincronização e aprovação da gerência.':(pendente?'Ponto registrado, mas está fora da área autorizada ou sem GPS confiável: PENDENTE DE APROVAÇÃO.':'Ponto registrado. Confira a sincronização acima.'));
  }catch(e){this.status(e.message||'Não foi possível registrar o ponto.','err')}
  finally{this.registrando=false;$('principal').disabled=false;this.renderFuncionario()}
 },
 async sincronizarFila(){
  if(this.emEnvio||!navigator.onLine||!this.db)return;
  this.emEnvio=true;
  try{
   for(const item of [...this.fila]){
    if(item.uid!==this.uid)continue;
    try{
     await this.db.ref('fdo_ponto_marcacoes/'+item.funcionarioId+'/'+item.id).set(item.registro);
     this.fila=this.fila.filter(x=>x.id!==item.id);this.gravarFila();
    }catch(e){console.warn('[PONTO] fila pendente',e);this.status('Há marcações aguardando sincronização. Não limpe os dados do aplicativo.','err');break}
   }
   if(this.funcId&&!this.gerente&&navigator.onLine)await this.atualizarFuncionario();
  }finally{this.emEnvio=false}
 },

 marcasDe(id){
  const v=this.gerente?(this.marcacoes[id]||{}):(id===this.funcId?this.eventosFuncionario():{});
  const a=this.gerente?(this.aprovacoes[id]||{}):this.aprovacoes;
  const registros=Object.entries(v).map(([key,e])=>{
   const decisoes=a[key]||{},last=ultimo(decisoes);
   return {...e,id:key,clienteTs:Number(e.clienteTs)||0,decisao:last?last.decisao:null,justificativa:last?last.motivo:null};
  }).filter(e=>e.clienteTs>0&&tipos.includes(e.tipo));
  return registros.sort((a,b)=>a.clienteTs-b.clienteTs||a.id.localeCompare(b.id));
 },
 resumoMes(id,mes){
  const eventos=this.marcasDe(id);const sessoes=[];let sessao=null;const avulsos=[];
  const incluir=s=>{if(s&&dataBR(s.inicio).slice(0,7)===mes)sessoes.push(s)};
  for(const e of eventos){
   if(e.decisao==='rejeitado'){avulsos.push({...e,razao:'Rejeitado pela gerência'});continue}
   if(e.tipo==='entrada'){
    if(sessao){sessao.incompleta=true;incluir(sessao)}
    sessao={inicio:e.clienteTs,fim:null,ativa:e.clienteTs,min:0,eventos:[e],incompleta:false};continue;
   }
   if(!sessao){avulsos.push({...e,razao:'Marcação sem entrada'});continue}
   sessao.eventos.push(e);
   if(e.tipo==='inicio_intervalo'){
    if(sessao.ativa===null)sessao.incompleta=true;
    else{sessao.min+=(e.clienteTs-sessao.ativa)/60000;sessao.ativa=null}
   }
   if(e.tipo==='fim_intervalo'){
    if(sessao.ativa!==null)sessao.incompleta=true;
    sessao.ativa=e.clienteTs;
   }
   if(e.tipo==='saida'){
    if(sessao.ativa!==null)sessao.min+=(e.clienteTs-sessao.ativa)/60000;
    sessao.fim=e.clienteTs;
    if(e.clienteTs<sessao.inicio||e.clienteTs-sessao.inicio>20*3600000)sessao.incompleta=true;
    incluir(sessao);sessao=null;
   }
  }
  if(sessao){sessao.incompleta=true;incluir(sessao)}
  const porDia={};const garantir=d=>porDia[d]||(porDia[d]={data:d,marcas:[],min:0,provisorio:false,motivos:[]});
  for(const s of sessoes){
   const dia=dataBR(s.inicio),row=garantir(dia);
   row.min+=Math.max(0,Math.round(s.min));
   row.marcas.push(...s.eventos);
   if(s.incompleta){row.provisorio=true;row.motivos.push('Jornada incompleta')}
   for(const e of s.eventos)if(e.avaliacao!=='normal'&&e.avaliacao!=='aprovado'&&e.decisao!=='aprovado'){row.provisorio=true;row.motivos.push('Marcação pendente')}
  }
  for(const e of avulsos){
   const dia=dataBR(e.clienteTs);
   if(dia.slice(0,7)!==mes)continue;
   const row=garantir(dia);row.marcas.push(e);row.provisorio=true;row.motivos.push(e.razao);
  }
  const dias=Object.values(porDia).filter(d=>d.data.slice(0,7)===mes).sort((a,b)=>a.data.localeCompare(b.data));
  let confirmados=0,provisorios=0,previstos=0;
  const regras=this.gerente?(this.regras[id]||{}):(id===this.funcId?this.regras:{});
  for(const d of dias){
   const regra=vigentes(regras,d.data),semana=diaSemana(d.data),meta=regra&&regra.dias?regra.dias[semana]:null;
   d.previsto=meta==null?null:Number(meta);
   if(d.previsto!==null&&Number.isFinite(d.previsto))previstos+=d.previsto;
   if(d.provisorio)provisorios+=d.min;else confirmados+=d.min;
  }
  return{dias,confirmados,provisorios,previstos,pendencias:dias.filter(d=>d.provisorio).length};
 },
 tabelaDias(res){
  if(!res.dias.length)return'<p class="muted">Nenhuma marcação neste mês.</p>';
  return'<table><thead><tr><th>Data</th><th>Marcações</th><th>Trabalhado</th><th>Situação</th></tr></thead><tbody>'+
   res.dias.map(d=>'<tr><td>'+xhtml(d.data.slice(8)+'/'+d.data.slice(5,7))+'</td><td>'+
   d.marcas.map(e=>xhtml(horaBR(e.clienteTs))).join(' · ')+'</td><td>'+horas(d.min)+'</td><td>'+
   (d.provisorio?'Pendente':'Confirmado')+'</td></tr>').join('')+'</tbody></table>';
 },
 fingerprint(id,mes){
  const eventos=this.marcasDe(id).filter(e=>dataBR(e.clienteTs).slice(0,7)===mes);
  const dados=this.resumoMes(id,mes);
  return hashLeve(JSON.stringify(eventos.map(e=>[e.id,e.clienteTs,e.tipo,e.avaliacao,e.decisao]))+
  JSON.stringify([dados.confirmados,dados.provisorios,dados.pendencias]));
 },
 async confirmarConferencia(){
  if(!this.funcId||!navigator.onLine)return this.status('Conecte-se para confirmar sua conferência.','err');
  const mes=$('mes-func').value;
  if(mes>=mesAtual())return this.status('A confirmação mensal fica disponível após o último dia do mês.','err');
  const r=this.resumoMes(this.funcId,mes);
  if(r.pendencias)return this.status('Há dias pendentes. Solicite a conferência antes de confirmar.','err');
  if(!confirm('Você conferiu as marcações de '+mes+' e não encontrou divergências?'))return;
  const confirmacao={uid:this.uid,resumo:this.fingerprint(this.funcId,mes),clienteTs:Date.now(),servidorTs:firebase.database.ServerValue.TIMESTAMP};
  try{await this.db.ref('fdo_ponto_conferencias/'+this.funcId+'/'+mes).push(confirmacao);await this.atualizarFuncionario();this.status('Sua conferência mensal foi registrada.','ok')}
  catch(e){this.status('Não foi possível gravar a conferência. Tente novamente.','err')}
 },
 async pedirCorrecao(){
  if(!this.funcId)return;
  const mes=$('mes-func').value||mesAtual();
  const texto=prompt('Informe a data, o horário correto e o que aconteceu (solicitação será analisada pela gerência):');
  if(!texto||texto.trim().length<10)return;
  if(!navigator.onLine)return this.status('Conecte-se para solicitar a correção.','err');
  try{await this.db.ref('fdo_ponto_solicitacoes/'+this.funcId).push({uid:this.uid,mes,texto:texto.trim().slice(0,500),clienteTs:Date.now(),servidorTs:firebase.database.ServerValue.TIMESTAMP});
  this.status('Solicitação enviada à gerência. O ponto original será preservado.','ok')}
  catch(e){this.status('Não foi possível enviar a solicitação.','err')}
 },
 // METHODS
};
if(typeof module!=='undefined')module.exports={dataBR,horaBR,horas,vigentes,hashLeve,distM};
if(typeof document!=='undefined')window.addEventListener('DOMContentLoaded',()=>P.init());
