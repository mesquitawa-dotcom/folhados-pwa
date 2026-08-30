const fs=require('fs');
const assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const sw=fs.readFileSync('sw.js','utf8');
const appcheck=fs.readFileSync('vendor/firebase-app-check-compat.js','utf8');
function has(src,x,msg){assert(src.includes(x),msg+' · ausente: '+x)}
// Regressão v26.5: verifica que o App Check continua preservado em versões posteriores.
// A versão/cache/backup correntes pertencem ao teste da versão atual, não a esta regressão.
has(html,'NOVIDADES v26.5:','notas v26.5 preservadas');
has(html,'vendor/firebase-app-check-compat.js','SDK App Check local');
has(html,"const APP_CHECK_SITE_KEY='6LcPFJ8tAAAAAFk2yg6aQ5Qi0NNMERW220URnH2A'",'site key Enterprise registrada');
has(html,'new firebase.appCheck.ReCaptchaEnterpriseProvider(APP_CHECK_SITE_KEY)','provider Enterprise');
has(html,'ac.activate(new firebase.appCheck.ReCaptchaEnterpriseProvider(APP_CHECK_SITE_KEY),true)','auto-refresh App Check');
has(html,'id="appcheck-info"','diagnóstico App Check');
has(html,"APP_CHECK.init();FB.db=firebase.database()",'App Check antes do Database');
has(sw,"'./vendor/firebase-app-check-compat.js'",'App Check pré-cacheado');
has(appcheck,'ReCaptchaEnterpriseProvider','bundle App Check contém provider Enterprise');
has(appcheck,'@firebase/app-check-compat','bundle App Check compat válido');
const order=['vendor/firebase-app-compat.js','vendor/firebase-app-check-compat.js','vendor/firebase-auth-compat.js','vendor/firebase-database-compat.js'].map(x=>html.indexOf(x));
assert(order.every(x=>x>=0)&&order.every((x,i)=>i===0||x>order[i-1]),'ordem dos SDKs Firebase deve ser App → App Check → Auth → Database');
console.log('TESTE v26.5 OK · App Check Enterprise preservado em versão posterior + SDK local + diagnóstico');
