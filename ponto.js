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
 // METHODS
};
if(typeof module!=='undefined')module.exports={dataBR,horaBR,horas,vigentes,hashLeve,distM};
if(typeof document!=='undefined')window.addEventListener('DOMContentLoaded',()=>P.init());
