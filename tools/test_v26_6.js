const fs=require('fs'),vm=require('vm'),assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
for(const m of ["atualização v26.6","const POS_PRODUTOS=","fdo_partidas","fdo_formas","function salvarCorteLaminacao()","function posFreezerRapido","function posFreezerConservador","function posIniciarDescongelamento","function posModelagemDireta","function montarForma","function abrirEtiquetaPartida","FB.criarFormaAtomica","versao:'26.6'"])assert(html.includes(m),'marcador ausente: '+m);
assert(html.includes("{id:'croissant_115',nome:'Croissant · corte 11,5 cm',corteCm:11.5,sugQtd:36,forma:16"));
assert(html.includes("{id:'croissant_100',nome:'Croissant · corte 10 cm',corteCm:10,sugQtd:40,forma:16"));
assert(html.includes("{id:'croissant_090',nome:'Croissant · corte 9 cm',corteCm:9,sugQtd:44,forma:16"));
assert(html.includes("{id:'croissant_mini',nome:'Croissant Mini',corteCm:null,sugQtd:null,forma:35"));
assert(html.includes("{id:'pain_chocolat',nome:'Pain au Chocolat',corteCm:null,sugQtd:null,forma:16"));
assert(html.includes("{id:'new_york_roll',nome:'New York Roll',corteCm:null,sugQtd:null,forma:14"));
assert(html.includes("tempAlvo:-15"),'freezer conservador sem -15°C');
assert(html.includes("set('modelagem',!!o.perms.laminacao)"),'migração de permissão modelagem ausente');
assert(html.includes("if(posPartidasDaLam(id).length)"),'laminação com fatias ainda apagável');
assert(html.includes("fdo_v25/partidas")&&html.includes("fdo_v25/formas"));
const rules=JSON.parse(fs.readFileSync('database.rules.json','utf8')).rules.fdo_v25;assert(rules.partidas&&rules.formas,'rules sem novas coleções');
const sw=fs.readFileSync('sw.js','utf8');assert(sw.includes("const CACHE='fdo-v26-6'"));
// receitas permanecem idênticas: validador principal faz cálculo executando o bloco real.
console.log('TESTE v26.6 OK · fatias, frio, modelagem, etiquetas, sync e Rules presentes');
