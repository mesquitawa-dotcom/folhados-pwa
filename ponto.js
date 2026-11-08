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
function vigentes(versoes,dia){const ds=Object.keys(versoes||{}).filter(d=>d.slice(0,10)<=dia).sort();return ds.length?versoes[ds[ds.length-1]]:null}
function hashLeve(s){let h=2166136261;for(const c of s){h^=c.charCodeAt(0);h=Math.imul(h,16777619)}return(h>>>0).toString(16)}
function ultimo(a){return Object.keys(a||{}).sort().map(k=>a[k]).filter(Boolean).at(-1)||null}
const P={
 db:null,auth:null,uid:'',gerente:false,funcId:'',perfil:null,pares:{},colabs:{},regras:{},salarios:{},avisos:{},marcacoes:{},aprovacoes:{},ajustes:{},ocorrencias:{},solicitacoes:{},solucoes:{},conferencias:{},fechamentos:{},area:{...gpsBase},offset:null,fila:[],emEnvio:false,carregando:false,
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
   const caminhos=['fdo_ponto_colaboradores/'+this.funcId,'fdo_ponto_marcacoes/'+this.funcId,'fdo_ponto_aprovacoes/'+this.funcId,'fdo_ponto_conferencias/'+this.funcId,'fdo_ponto_regras/'+this.funcId,'fdo_ponto_avisos_gerais','fdo_ponto_avisos_individuais/'+this.funcId,'fdo_ponto_config/area','fdo_ponto_ajustes/'+this.funcId,'fdo_ponto_ocorrencias/'+this.funcId];
   const dados=await Promise.all(caminhos.map(p=>this.db.ref(p).once('value').then(s=>s.val()).catch(()=>null)));
   if(!dados[0]||dados[0].ativo!==true){this.funcId='';show('funcionario',false);show('ativacao');this.status('Cadastro do funcionário inativo ou indisponível.','err');return}
   this.perfil=dados[0];this.marcacoes=dados[1]||{};this.aprovacoes=dados[2]||{};this.conferencias=dados[3]||{};this.regras=dados[4]||{};
   this.avisos={gerais:dados[5]||{},individuais:dados[6]||{}};this.area=dados[7]||this.area;this.ajustes=dados[8]||{};this.ocorrencias=dados[9]||{};this.cacheSalvar();this.telaFuncionario();
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
   if(navigator.onLine){try{const a=await this.db.ref('fdo_ponto_config/area').once('value');if(a.val())this.area=a.val();const o=await this.db.ref('.info/serverTimeOffset').once('value');this.offset=Number(o.val())||0}catch(e){this.offset=null}}
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
   const aindaLocal=this.fila.some(x=>x.id===id),pendente=status!=='normal';
   const msg=aindaLocal?'Registro salvo no aparelho, aguardando sincronização e aprovação da gerência.':(geo.situacao==='fora'?'Você está fora da fábrica. Ponto registrado, PENDENTE DE APROVAÇÃO.':pendente?'Ponto registrado, PENDENTE DE APROVAÇÃO da gerência por GPS/relógio.':'Ponto registrado e confirmado.');
   txt('feedback',msg);
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
    }catch(e){console.warn('[PONTO] fila pendente',e);if(item.registro.avaliacao==='normal')item.registro.avaliacao='sem_internet';this.gravarFila();this.status('Há marcações aguardando sincronização. Não limpe os dados do aplicativo.','err');break}
   }
   if(this.funcId&&!this.gerente&&navigator.onLine)await this.atualizarFuncionario();
  }finally{this.emEnvio=false}
 },

 marcasDe(id){
  const v=this.gerente?(this.marcacoes[id]||{}):(id===this.funcId?this.eventosFuncionario():{});
  const a=this.gerente?(this.aprovacoes[id]||{}):this.aprovacoes;
  const registros=Object.entries(v).map(([key,e])=>{
   const decisoes=a[key]||{},last=ultimo(decisoes),aj=(this.gerente?(this.ajustes[id]||{}):this.ajustes)||{},corr=ultimo(aj[key]||{});
   const servidor=typeof e.servidorTs==='number'?e.servidorTs:null;const drift=e.origem==='celular'&&e.avaliacao==='normal'&&servidor&&Math.abs(e.clienteTs-servidor)>300000;
   const efetivo=corr?corr.clienteTs:(e.origem==='celular'&&servidor&&!drift?servidor:e.clienteTs);
   return {...e,id:key,originalTs:e.clienteTs,clienteTs:Number(efetivo)||0,corrigido:!!corr,avaliacao:drift?'relogio':e.avaliacao,decisao:last?last.decisao:null,justificativa:last?last.motivo:null};
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
  // Dias sem marcação não são classificados automaticamente como falta.
  const ocorr=this.gerente?(this.ocorrencias[id]||{}):(id===this.funcId?this.ocorrencias:{});
  for(const o of Object.values(ocorr||{})){
   if(!o||typeof o.data!=='string'||o.data.slice(0,7)!==mes)continue;
   const row=garantir(o.data);row.ocorrencia=o;
   if(o.tipo==='folga'||o.tipo==='feriado')row.abonado=true;
   if(o.tipo==='justificada')row.motivos.push('Ausência justificada: conferir impacto');
  }
  const regrasDia=this.gerente?(this.regras[id]||{}):(id===this.funcId?this.regras:{});
  const partes=mes.split('-').map(Number),numDias=new Date(Date.UTC(partes[0],partes[1],0)).getUTCDate();
  const hoje=dataBR(Date.now()),ate=mes<hoje.slice(0,7)?numDias:mes===hoje.slice(0,7)?Math.max(0,Number(hoje.slice(8))-1):0;
  for(let n=1;n<=ate;n++){
   const dia=mes+'-'+pad(n),reg=vigentes(regrasDia,dia),meta=reg&&reg.dias?reg.dias[diaSemana(dia)]:null;
   if(meta==null||Number(meta)<=0)continue;
   const row=garantir(dia);
   if(!row.marcas.length&&!row.abonado){row.provisorio=true;row.motivos.push('Sem marcação: conferir falta, feriado ou folga')}
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
   (d.provisorio?'Pendente':d.abonado?(d.ocorrencia.tipo==='folga'?'Folga':'Feriado'):'Confirmado')+(d.motivos.length?' · '+xhtml([...new Set(d.motivos)].join('; ')):'')+'</td></tr>').join('')+'</tbody></table>';
 },
 fingerprint(id,mes){
  const eventos=this.marcasDe(id).filter(e=>dataBR(e.clienteTs).slice(0,7)===mes);
  const dados=this.resumoMes(id,mes);
  return hashLeve(JSON.stringify(eventos.map(e=>[e.id,e.clienteTs,e.tipo,e.avaliacao,e.decisao,e.corrigido]))+
  JSON.stringify([dados.confirmados,dados.provisorios,dados.pendencias,dados.dias.map(d=>[d.data,d.motivos,d.abonado])]));
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

 async atualizarGerencia(){
  if(!this.gerente||!navigator.onLine)return this.status('Painel gerencial exige conexão.','err');
  const keys=['fdo_ponto_colaboradores','fdo_ponto_regras','fdo_ponto_financeiro','fdo_ponto_marcacoes','fdo_ponto_aprovacoes','fdo_ponto_solicitacoes','fdo_ponto_solucoes','fdo_ponto_conferencias','fdo_ponto_fechamentos','fdo_ponto_vinculos','fdo_ponto_config/area','fdo_ponto_ajustes','fdo_ponto_ocorrencias'];
  try{
   const results=await Promise.all(keys.map(k=>this.db.ref(k).once('value').then(s=>s.val())));
   [this.colabs,this.regras,this.salarios,this.marcacoes,this.aprovacoes,this.solicitacoes,this.solucoes,this.conferencias,this.fechamentos,this.pares]=results.slice(0,10).map(x=>x||{});this.ajustes=results[11]||{};this.ocorrencias=results[12]||{};
   this.area=results[10]||this.area;
   this.prepararSeletores();this.renderPendencias();this.renderRelatorio();this.preencherGPS();this.status('Gerência atualizada.','ok');
  }catch(e){console.error('[PONTO] gerência',e);this.status('Erro ao carregar a gerência. Verifique as Rules e sua autorização.','err')}
 },
 aba(a){for(const nome of ['resumo','cadastro','mes','avisos','gps'])show('aba-'+nome,nome===a)},
 prepararSeletores(){
  const itens=Object.entries(this.colabs).sort((a,b)=>String(a[1].nome).localeCompare(String(b[1].nome),'pt-BR'));
  const opts=itens.map(([id,p])=>'<option value="'+xhtml(id)+'">'+xhtml(p.nome)+'</option>').join('');
  for(const id of ['emp-selecionado','rel-emp','aviso-alvo']){
   const sel=$(id),old=sel.value;
   sel.innerHTML=(id==='emp-selecionado'?'<option value="">Novo funcionário</option>':id==='rel-emp'?'<option value="todos">Todos</option>':'<option value="todos">Todos os funcionários</option>')+opts;
   if([...sel.options].some(o=>o.value===old))sel.value=old;
  }
  this.preencherCadastro();
 },
 preencherCadastro(){
  const id=$('emp-selecionado').value,p=this.colabs[id]||{},reg=vigentes(this.regras[id],dataBR(Date.now())),fin=vigentes(this.salarios[id],dataBR(Date.now()));
  $('emp-nome').value=p.nome||'';$('emp-tipo').value=p.tipo||'mensalista';$('emp-ativo').checked=p.ativo!==false;
  for(let i=0;i<7;i++)$('jornada-'+i).value=reg&&reg.dias&&reg.dias[i]!=null?reg.dias[i]:'';
  $('emp-valor').value=fin&&Number.isFinite(Number(fin.centavos))?(Number(fin.centavos)/100).toFixed(2):'';
  this.renderVinculos(id);
 },
 renderVinculos(id){
  const p=Object.entries(this.pares).filter(([,v])=>v.funcionarioId===id);
  $('lista-vinculos').innerHTML=p.length?p.map(([uid,v])=>'<div class="list-row">'+xhtml(uid)+' · '+(v.ativo?'Ativo':'Revogado')+
   (v.ativo?' <button class="btn" onclick="P.revogar('+JSON.stringify(uid)+')">Revogar</button>':'')+'</div>').join(''):'Nenhum celular vinculado.';
 },
 async salvarFuncionario(){
  if(!this.gerente)return;
  const id=$('emp-selecionado').value||idNovo(),nome=$('emp-nome').value.trim(),tipo=$('emp-tipo').value,ativo=$('emp-ativo').checked;
  if(nome.length<2||nome.length>90||!['mensalista','horista'].includes(tipo))return alert('Confira nome e tipo.');
  const vig=$('emp-vigencia').value||dataBR(Date.now());
  if(!/^\d{4}-\d{2}-\d{2}$/.test(vig))return alert('Informe a vigência válida.');
  const dias={};
  for(let i=0;i<7;i++){const v=$('jornada-'+i).value;if(v!==''){if(!/^\d+$/.test(v)||Number(v)>1440)return alert('Jornada inválida.');dias[i]=Number(v)}}
  const s=$('emp-valor').value,centavos=s===''?null:Math.round(Number(s)*100);
  if(centavos!==null&&(!Number.isFinite(centavos)||centavos<0))return alert('Valor financeiro inválido.');
  try{
   await this.db.ref('fdo_ponto_colaboradores/'+id).set({nome,tipo,ativo});
   const rev=vig+'~'+this.db.ref('fdo_ponto_regras/'+id).push().key;
   await this.db.ref('fdo_ponto_regras/'+id+'/'+rev).set({dias,tipo,gerenteUid:this.uid,servidorTs:firebase.database.ServerValue.TIMESTAMP});
   if(centavos!==null){const rv=vig+'~'+this.db.ref('fdo_ponto_financeiro/'+id).push().key;await this.db.ref('fdo_ponto_financeiro/'+id+'/'+rv).set({centavos,tipo,gerenteUid:this.uid,servidorTs:firebase.database.ServerValue.TIMESTAMP})}
   await this.atualizarGerencia();$('emp-selecionado').value=id;this.preencherCadastro();alert('Cadastro salvo e versionado.');
  }catch(e){alert('Não foi possível salvar o cadastro. Verifique acesso/conexão.');console.warn(e)}
 },
 async vincular(){
  if(!this.gerente)return;const id=$('emp-selecionado').value,uid=$('emp-uid').value.trim();
  if(!this.colabs[id]||!this.colabs[id].ativo)return alert('Selecione um funcionário ativo.');
  if(!/^[a-zA-Z0-9]{18,128}$/.test(uid))return alert('Código UID inválido.');
  const antes=this.pares[uid];if(antes&&antes.funcionarioId!==id&&!confirm('Este aparelho já pertence a outro funcionário. Deseja transferi-lo?'))return;
  try{await this.db.ref('fdo_ponto_vinculos/'+uid).set({funcionarioId:id,ativo:true,gerenteUid:this.uid,atualizadoTs:firebase.database.ServerValue.TIMESTAMP});$('emp-uid').value='';await this.atualizarGerencia();alert('Celular autorizado. O funcionário já pode registrar o ponto.')}
  catch(e){alert('Erro ao autorizar celular.')}
 },
 async revogar(uid){
  if(!this.gerente||!this.pares[uid]||!confirm('Revogar o acesso deste celular?'))return;
  try{await this.db.ref('fdo_ponto_vinculos/'+uid).update({ativo:false,atualizadoTs:firebase.database.ServerValue.TIMESTAMP});await this.atualizarGerencia()}catch(e){alert('Erro ao revogar.')}
 },

 renderPendencias(){
  if(!this.gerente)return;
  const html=[];
  for(const [id,p] of Object.entries(this.colabs)){
   for(const e of this.marcasDe(id)){
    if(e.decisao||e.avaliacao==='normal'||e.avaliacao==='aprovado')continue;
    html.push('<div class="list-row"><strong>'+xhtml(p.nome)+'</strong> — '+xhtml(dataBR(e.clienteTs))+' '+xhtml(horaBR(e.clienteTs))+
     ' · '+xhtml(e.tipo)+'<div class="muted">Situação: '+xhtml(e.avaliacao)+' · GPS: '+xhtml(e.gps&&e.gps.situacao||'indisponível')+'</div>'+
     '<div class="actions"><button class="btn" onclick="P.decidir('+JSON.stringify(id)+','+JSON.stringify(e.id)+',\'aprovado\')">Aprovar</button>'+
     '<button class="btn" onclick="P.decidir('+JSON.stringify(id)+','+JSON.stringify(e.id)+',\'rejeitado\')">Rejeitar</button>'+
     '<button class="btn" onclick="P.ajustar('+JSON.stringify(id)+','+JSON.stringify(e.id)+')">Corrigir horário</button></div></div>');
   }
  }
  $('pendencias-ger').innerHTML=html.length?html.join(''):'<div class="status ok">Nenhuma marcação pendente.</div>';
  const sol=[];
  for(const [id,reqs] of Object.entries(this.solicitacoes)){
   for(const [reqId,r] of Object.entries(reqs||{})){
    if(Object.keys((this.solucoes[id]||{})[reqId]||{}).length)continue;
    sol.push('<div class="list-row"><strong>'+xhtml((this.colabs[id]||{}).nome||id)+'</strong> — '+xhtml(r.mes)+'<p>'+xhtml(r.texto)+'</p>'+
    '<button class="btn" onclick="P.resolverSolicitacao('+JSON.stringify(id)+','+JSON.stringify(reqId)+')">Marcar como analisada</button></div>');
   }
  }
  $('solicitacoes-ger').innerHTML=sol.length?sol.join(''):'<div class="status ok">Nenhuma solicitação pendente.</div>';
 },
 async decidir(emp,id,decisao){
  if(!this.gerente||!['aprovado','rejeitado'].includes(decisao))return;
  const motivo=prompt(decisao==='aprovado'?'Motivo da aprovação (opcional):':'Motivo da rejeição (obrigatório):')||'';
  if(decisao==='rejeitado'&&motivo.trim().length<5)return alert('Informe o motivo.');
  if(!confirm('Confirmar decisão? O registro original será preservado.'))return;
  try{await this.db.ref('fdo_ponto_aprovacoes/'+emp+'/'+id).push({decisao,motivo:motivo.trim().slice(0,250),gerenteUid:this.uid,servidorTs:firebase.database.ServerValue.TIMESTAMP});await this.atualizarGerencia()}
  catch(e){alert('Não foi possível registrar a decisão.')}
 },

 async ajustar(emp,id){
  if(!this.gerente)return;const e=(this.marcacoes[emp]||{})[id];if(!e)return;
  const original=new Date(e.clienteTs).toLocaleString('sv-SE',{timeZone:'America/Sao_Paulo'}).replace(' ','T').slice(0,16);
  const horario=prompt('Novo dia e horário da fábrica (AAAA-MM-DDTHH:MM):',original);
  if(!horario)return;
  const ts=Date.parse(horario+':00-03:00');
  if(!Number.isFinite(ts)||!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$/.test(horario))return alert('Horário inválido.');
  const motivo=prompt('Justificativa obrigatória para corrigir a marcação:')||'';
  if(motivo.trim().length<5)return alert('Informe o motivo.');
  if(!confirm('Preservar horário original e acrescentar correção?'))return;
  try{await this.db.ref('fdo_ponto_ajustes/'+emp+'/'+id).push({clienteTs:ts,motivo:motivo.trim().slice(0,250),gerenteUid:this.uid,servidorTs:firebase.database.ServerValue.TIMESTAMP});await this.atualizarGerencia()}
  catch(e){alert('Erro ao gravar correção.')}
 },
 async resolverSolicitacao(emp,id){
  const resposta=prompt('Como a solicitação foi tratada? Se necessário, inclua uma marcação supervisionada ou corrija o horário:')||'';
  if(resposta.trim().length<5)return;
  try{await this.db.ref('fdo_ponto_solucoes/'+emp+'/'+id).push({texto:resposta.trim().slice(0,500),gerenteUid:this.uid,servidorTs:firebase.database.ServerValue.TIMESTAMP});await this.atualizarGerencia()}
  catch(e){alert('Erro ao registrar resposta.')}
 },
 async marcarManual(){
  if(!this.gerente)return;
  const emp=$('emp-selecionado').value,tipo=$('manual-tipo').value,h=$('manual-hora').value,motivo=$('manual-motivo').value.trim();
  const ts=Date.parse(h+':00-03:00');
  if(!this.colabs[emp]||!tipos.includes(tipo)||!Number.isFinite(ts)||motivo.length<5)return alert('Selecione funcionário, horário, tipo e motivo válido.');
  if(!confirm('Incluir marcação supervisionada, com auditoria?'))return;
  try{
   await this.db.ref('fdo_ponto_marcacoes/'+emp).push({tipo,uid:this.uid,clienteTs:ts,servidorTs:firebase.database.ServerValue.TIMESTAMP,gps:{situacao:'supervisionado'},avaliacao:'aprovado',origem:'gerencia',motivo});
   $('manual-motivo').value='';await this.atualizarGerencia();
  }catch(e){alert('Erro ao registrar marcação supervisionada.')}
 },

 preencherGPS(){const a=this.area||gpsBase;$('gps-lat').value=a.lat;$('gps-lng').value=a.lng;$('gps-raio').value=a.raio},
 async salvarGPS(){
  if(!this.gerente)return;
  const lat=Number($('gps-lat').value),lng=Number($('gps-lng').value),raio=Number($('gps-raio').value);
  if(!Number.isFinite(lat)||!Number.isFinite(lng)||Math.abs(lat)>90||Math.abs(lng)>180||raio<20||raio>2000)return alert('Valores GPS inválidos.');
  try{await this.db.ref('fdo_ponto_config/area').set({lat,lng,raio});this.area={lat,lng,raio};this.status('Área de registro atualizada.','ok')}
  catch(e){this.status('Erro ao salvar a área de registro.','err')}
 },
 async copiarLink(acao){
  const url=new URL('./ponto.html',location.href);url.searchParams.set('acao',acao);
  try{await navigator.clipboard.writeText(url.href);this.status('Link copiado. Pode ser transformado em QR impresso.','ok')}
  catch{prompt('Copie o link:',url.href)}
 },
 async publicarAviso(){
  if(!this.gerente)return;
  const alvo=$('aviso-alvo').value,texto=$('aviso-texto').value.trim();
  if(texto.length<3)return alert('Escreva a mensagem do aviso.');
  const path=alvo==='todos'?'fdo_ponto_avisos_gerais':'fdo_ponto_avisos_individuais/'+alvo;
  try{await this.db.ref(path).push({texto,gerenteUid:this.uid,clienteTs:Date.now(),servidorTs:firebase.database.ServerValue.TIMESTAMP});
   $('aviso-texto').value='';this.status('Aviso publicado. Ele aparecerá no Ponto do funcionário.','ok')}
  catch(e){this.status('Falha ao publicar aviso.','err')}
 },

 idsRelatorio(){const id=$('rel-emp').value;return id==='todos'?Object.keys(this.colabs).sort((a,b)=>String(this.colabs[a].nome).localeCompare(String(this.colabs[b].nome),'pt-BR')):[id].filter(x=>this.colabs[x])},
 linhasRelatorio(){
  const mes=$('mes-ger').value||mesAtual();
  return this.idsRelatorio().map(id=>{
   const dados=this.resumoMes(id,mes),c=ultimo(((this.conferencias[id]||{})[mes])||{}),conferido=!!c&&c.resumo===this.fingerprint(id,mes);
   return{id,nome:this.colabs[id].nome,dados,conferido};
  });
 },
 renderRelatorio(){
  if(!this.gerente)return;
  const linhas=this.linhasRelatorio();
  $('resumo-ger').innerHTML='<table><thead><tr><th>Funcionário</th><th>Horas confirmadas</th><th>Provisórias</th><th>Conferência</th></tr></thead><tbody>'+
    linhas.map(r=>'<tr><td>'+xhtml(r.nome)+'</td><td>'+horas(r.dados.confirmados)+'</td><td>'+horas(r.dados.provisorios)+'</td><td>'+(r.conferido?'✓':'Pendente')+'</td></tr>').join('')+'</tbody></table>';
  $('financeiro-ger').innerHTML='<table><thead><tr><th>Funcionário</th><th>Modalidade</th><th>Valor cadastrado</th><th>Estimativa básica</th></tr></thead><tbody>'+
   linhas.map(r=>{
    const fin=vigentes(this.salarios[r.id],$('mes-ger').value+'-01'),tipo=fin&&fin.tipo||this.colabs[r.id].tipo;
    const bruto=fin?(tipo==='horista'?Math.round(r.dados.confirmados*Number(fin.centavos)/60):Number(fin.centavos)):null;
    return'<tr><td>'+xhtml(r.nome)+'</td><td>'+xhtml(tipo)+'</td><td>'+ (fin?dinheiro(fin.centavos)+(tipo==='horista'?'/h':'/mês'):'Não definido')+
    '</td><td>'+(bruto==null?'—':dinheiro(bruto)+(r.dados.pendencias?' (parcial)':''))+'</td></tr>';
   }).join('')+'</tbody></table><p class="tiny">Estimativa básica gerencial. Não é holerite: adicionais, faltas, encargos e alterações salariais durante o mês exigem conferência contábil.</p>';
  const fech=ultimo((this.fechamentos||{})[$('mes-ger').value]);txt('fechamento-status',fech?'Fechamento gerencial registrado. Correções posteriores exigem nova conferência.':'Mês ainda não encerrado pela gerência.');
 },
 htmlRelatorio(){
  const mes=$('mes-ger').value||mesAtual(),linhas=this.linhasRelatorio();
  return'<h1>Folhados d’Ouro — Espelho de ponto</h1><p>Período: '+xhtml(mes)+' · Gerado em '+xhtml(new Date().toLocaleString('pt-BR',{timeZone:'America/Sao_Paulo'}))+'</p>'+
   linhas.map((r,i)=>'<section '+(i?'class="page-break"':'')+'><h2>'+xhtml(r.nome)+'</h2><p>Horas confirmadas: <strong>'+horas(r.dados.confirmados)+'</strong> · Provisórias: '+horas(r.dados.provisorios)+' · Conferência: '+(r.conferido?'realizada':'pendente')+'</p>'+
   this.tabelaDias(r.dados)+'<p>Observações: '+(r.dados.pendencias?r.dados.pendencias+' dia(s) aguardando conferência.':'Sem marcações pendentes detectadas.')+'</p></section>').join('');
 },
 salvarPDF(){
  if(!this.gerente)return;
  $('ponto-impressao').innerHTML=this.htmlRelatorio();
  this.status('Na tela de impressão, selecione “Salvar como PDF”.','ok');
  window.print();
 },
 async salvarPNG(){
  if(!this.gerente)return;
  const mes=$('mes-ger').value||mesAtual(),linhas=this.linhasRelatorio();
  if(!linhas.length)return alert('Nenhum funcionário selecionado.');
  const width=1200,height=260+linhas.length*68;
  const cv=document.createElement('canvas');cv.width=width;cv.height=height;
  const c=cv.getContext('2d');c.fillStyle='#ffffff';c.fillRect(0,0,width,height);c.fillStyle='#151515';
  c.font='bold 38px Georgia';c.fillText('Folhados d’Ouro — Ponto',45,65);
  c.font='25px Georgia';c.fillText('Mês: '+mes+' · Resumo sem salários',45,110);
  c.fillStyle='#555';c.font='21px Georgia';c.fillText('Funcionário                         Confirmadas       Provisórias       Conferência',45,167);
  linhas.forEach((r,i)=>{
   const y=220+i*68;c.fillStyle=i%2?'#f5f3ef':'#eae7df';c.fillRect(30,y-34,1135,57);
   c.fillStyle='#151515';c.font='23px Georgia';c.fillText(r.nome.slice(0,27),45,y);
   c.fillText(horas(r.dados.confirmados),570,y);c.fillText(horas(r.dados.provisorios),775,y);
   c.fillText(r.conferido?'Conferido':'Pendente',990,y);
  });
  const blob=await new Promise(resolve=>cv.toBlob(resolve,'image/png'));
  if(!blob)return alert('Não foi possível gerar a imagem.');
  const name='fdo-ponto-'+mes+'.png',arquivo=new File([blob],name,{type:'image/png'});
  if(navigator.canShare&&navigator.canShare({files:[arquivo]})){
   try{await navigator.share({files:[arquivo],title:'Ponto Folhados d’Ouro'});return}catch(e){if(e.name==='AbortError')return}
  }
  const u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),3000);
 },

 async fecharMes(){
  if(!this.gerente)return;
  const mes=$('mes-ger').value||mesAtual();
  if(mes>=mesAtual())return alert('O mês só pode ser fechado após seu último dia.');
  const linhas=this.linhasRelatorio();
  const pend=linhas.filter(x=>x.dados.pendencias||!x.conferido);
  const motivo=$('motivo-fechar').value.trim();
  if(pend.length&&motivo.length<10)return alert('Existem pendências ou conferências faltantes. Informe justificativa de pelo menos 10 caracteres.');
  if(!confirm('Confirmar fechamento gerencial de '+mes+'? O histórico será preservado.'))return;
  const dados={};
  linhas.forEach(r=>{dados[r.id]={nome:r.nome,confirmados:r.dados.confirmados,provisorios:r.dados.provisorios,pendencias:r.dados.pendencias,conferido:r.conferido,resumo:this.fingerprint(r.id,mes)}});
  try{
   await this.db.ref('fdo_ponto_fechamentos/'+mes).push({gerenteUid:this.uid,mes,dados,motivo,clienteTs:Date.now(),servidorTs:firebase.database.ServerValue.TIMESTAMP});
   $('motivo-fechar').value='';await this.atualizarGerencia();this.status('Fechamento registrado com histórico de auditoria.','ok');
  }catch(e){this.status('Falha no fechamento. Nenhuma conclusão foi confirmada.','err')}
 },
 // METHODS
};
if(typeof module!=='undefined')module.exports={dataBR,horaBR,horas,vigentes,hashLeve,distM};
if(typeof window!=='undefined')window.P=P;
if(typeof document!=='undefined')window.addEventListener('DOMContentLoaded',()=>P.init());
