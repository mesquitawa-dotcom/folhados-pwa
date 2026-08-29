from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def one(s,old,new,label):
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: esperado 1 ocorrência, obtido {n}')
    return s.replace(old,new,1)

# index.html
p=ROOT/'index.html';s=p.read_text(encoding='utf-8')
s=one(s,"       FOLHADOS D'OURO — atualização v26.3\n       NOVIDADES v26.3:","       FOLHADOS D'OURO — atualização v26.4\n       NOVIDADES v26.4:\n       • Segurança Firebase: trilhas históricas passam a ser append-only nas Rules.\n       • Auditoria de receitas e movimentos de estoque reconhecem retry idempotente sem regravar o remoto.\n       • Mesmo ID histórico com conteúdo diferente vira conflito e nunca sobrescreve o registro já gravado.\n       • A allowlist de fdo_v25 fecha caminhos não previstos, preservando somente estruturas usadas pelo app.\n       • Nenhuma receita, peso, fermento, tempo, snapshot ou fluxo produtivo foi alterado.\n       NOVIDADES v26.3:",'cabeçalho v26.4')
s=one(s,'Versão 26.3 · cache fdo-v26-3 · Firebase SDK local','Versão 26.4 · cache fdo-v26-4 · Firebase SDK local','versão em Config')
s=one(s,"versao:'26.3'","versao:'26.4'",'versão do backup')

old_methods="""  ts(x){return Math.max(Number(x&&x.atualizadoTs)||0,Number(x&&x.emTs)||0,Number(x&&x.criadoTs)||0);},
  list(nome){const d=this.defs[nome];return d?LS.g(d.local,[]):[];},"""
new_methods="""  ts(x){return Math.max(Number(x&&x.atualizadoTs)||0,Number(x&&x.emTs)||0,Number(x&&x.criadoTs)||0);},
  imutavel(nome){return nome==='movimentos'||nome==='auditoria';},
  canon(v){if(Array.isArray(v))return v.map(x=>this.canon(x));if(v&&typeof v==='object'){const o={};Object.keys(v).sort().forEach(k=>o[k]=this.canon(v[k]));return o;}return v;},
  igual(a,b){return JSON.stringify(this.canon(a))===JSON.stringify(this.canon(b));},
  list(nome){const d=this.defs[nome];return d?LS.g(d.local,[]):[];},"""
s=one(s,old_methods,new_methods,'métodos de sincronização imutável')

old_flush="""  async flush(){
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
    if(this.pending()&&navigator.onLine){
      if(!ok)FB.status('err','⚠ Estoque salvo aqui · nuvem pendente');
      setTimeout(()=>this.flush(),ok?150:5000);return;
    }
    FB.status(ok?'ok':'err',ok?'✓ Sincronizado':'⚠ Estoque salvo aqui · nuvem pendente');
  },"""
new_flush="""  async flush(){
    if(this.flushing||!FB.db||!navigator.onLine)return;const o=this.out(),jobs=[];
    Object.keys(this.defs).forEach(nome=>Object.entries(o[nome]||{}).forEach(([id,reg])=>jobs.push([nome,id,reg])));
    if(!jobs.length)return;this.flushing=true;FB.status('pending','Estoque salvo · sincronizando…');let ok=true,conflitoHistorico=false;
    for(const [nome,id,reg] of jobs){
      try{
        const ref=FB.db.ref(this.defs[nome].path+'/'+id);
        if(this.imutavel(nome)){
          const r=await ref.transaction(cur=>cur==null?reg:undefined,undefined,false),remoto=r.snapshot.val();
          if(!this.igual(remoto,reg)){
            ok=false;conflitoHistorico=true;
            console.error('[HISTÓRICO] conflito imutável preservado na nuvem',nome,id,{local:reg,remoto});
            continue;
          }
        }else{
          await ref.transaction(cur=>!cur||this.ts(reg)>=this.ts(cur)?reg:cur,undefined,false);
        }
        const agora=this.out(),cur=agora[nome]&&agora[nome][id];if(cur&&this.igual(cur,reg))delete agora[nome][id];this.saveOut(agora);
      }catch(e){ok=false;console.warn('[ESTOQUE] sync',nome,id,e);}
    }
    this.flushing=false;
    if(conflitoHistorico){FB.status('err','⚠ Conflito histórico · registro da nuvem preservado');return;}
    if(this.pending()&&navigator.onLine){
      if(!ok)FB.status('err','⚠ Estoque salvo aqui · nuvem pendente');
      setTimeout(()=>this.flush(),ok?150:5000);return;
    }
    FB.status(ok?'ok':'err',ok?'✓ Sincronizado':'⚠ Estoque salvo aqui · nuvem pendente');
  },"""
s=one(s,old_flush,new_flush,'flush de ESTOQUE_SYNC')
p.write_text(s,encoding='utf-8')

# sw.js
p=ROOT/'sw.js';sw=p.read_text(encoding='utf-8')
sw=one(sw,"const CACHE='fdo-v26-3';","const CACHE='fdo-v26-4';",'cache do Service Worker')
p.write_text(sw,encoding='utf-8')

# test_v26_3.js: passa a verificar preservação histórica, não a versão corrente
p=ROOT/'tools/test_v26_3.js';t=p.read_text(encoding='utf-8')
t=one(t,"has(html,'atualização v26.3','cabeçalho v26.3');","has(html,'NOVIDADES v26.3:','histórico v26.3 preservado');",'marcador histórico test_v26_3')
t=one(t,"has(html,'Versão 26.3 · cache fdo-v26-3','diagnóstico exibe versão/cache');\nhas(sw,\"const CACHE='fdo-v26-3'\",'cache v26.3');\n\n",'', 'asserts de versão corrente v26.3')
p.write_text(t,encoding='utf-8')

# validator
p=ROOT/'tools/validate_fdo.py';v=p.read_text(encoding='utf-8')
v=one(v,"# v26.3 — confiabilidade, diagnóstico e offline real\nfor marker in (\n    'atualização v26.3',","# v26.4 — segurança Firebase e históricos append-only\nfor marker in (\n    'atualização v26.4','NOVIDADES v26.4:',\"imutavel(nome){return nome==='movimentos'||nome==='auditoria';}\",\n    'conflitoHistorico=false',\"cur=>cur==null?reg:undefined\",'Conflito histórico · registro da nuvem preservado',\n    \"versao:'26.4'\"\n):\n    if marker not in html: fail('v26.4 sem marcador: '+marker)\n\n# v26.3 — confiabilidade, diagnóstico e offline real preservada\nfor marker in (\n    'NOVIDADES v26.3:',",'bloco v26.4 no validador')
v=one(v,",\"tipo:'estorno_cancelamento'\",\"tipo:'reaplicacao_restauro'\",\"versao:'26.3'\"\n):",",\"tipo:'estorno_cancelamento'\",\"tipo:'reaplicacao_restauro'\"\n):",'versão antiga no bloco v26.3')
v=one(v,"print('VALIDAÇÃO FDO v26.3 OK')","print('VALIDAÇÃO FDO v26.4 OK')",'saída do validador')
p.write_text(v,encoding='utf-8')

# Novo teste da versão v26.4
(ROOT/'tools/test_v26_4.js').write_text(r'''const fs=require('fs');
const assert=require('assert');
const html=fs.readFileSync('index.html','utf8');
const sw=fs.readFileSync('sw.js','utf8');
const rules=JSON.parse(fs.readFileSync('database.rules.json','utf8')).rules;
function has(src,x,msg){assert(src.includes(x),msg+' · ausente: '+x)}
has(html,'atualização v26.4','cabeçalho v26.4');
has(html,'NOVIDADES v26.4:','notas v26.4');
has(html,"imutavel(nome){return nome==='movimentos'||nome==='auditoria';}",'coleções históricas identificadas');
has(html,"cur=>cur==null?reg:undefined",'registro histórico só nasce quando ausente');
has(html,'this.igual(remoto,reg)','retry compara conteúdo remoto sem regravar');
has(html,'conflitoHistorico=true','conteúdo divergente vira conflito');
has(html,'Conflito histórico · registro da nuvem preservado','conflito fica visível e preserva nuvem');
has(html,"versao:'26.4'",'backup identifica v26.4');
has(html,'Versão 26.4 · cache fdo-v26-4','Config identifica v26.4');
has(sw,"const CACHE='fdo-v26-4'",'cache v26.4');
assert.strictEqual(rules['.read'],false,'raiz deve negar leitura');
assert.strictEqual(rules['.write'],false,'raiz deve negar gravação');
assert(!Object.prototype.hasOwnProperty.call(rules.fdo_v25,'.write'),'fdo_v25 não pode ter write amplo');
for(const path of [
  rules.fdo_acessos.$id,
  rules.fdo_v25.estoque.movimentos.$id,
  rules.fdo_v25.receitas_auditoria.$id
]){
  assert(path['.write'].includes('!data.exists() && newData.exists()'),'trilha histórica deve permitir somente criação');
}
assert(rules.fdo_v25.lotes['.write'],'lotes continuam graváveis');
assert(rules.fdo_v25.laminacoes['.write'],'laminações continuam graváveis');
assert(rules.fdo_v25.receitas_definitivas['.write'],'receitas definitivas continuam versionáveis');
assert(rules.fdo_v25.estoque.contagens['.write'],'contagens continuam graváveis');
console.log('TESTE v26.4 OK · sync histórico idempotente + Rules append-only + allowlist explícita');
''',encoding='utf-8')

# Smoke atual reaproveita a prova de boot da v26.3 com nome/saída v26.4
old=(ROOT/'tools/smoke_v26_3.py').read_text(encoding='utf-8')
new=old.replace('_smoke_v26_3.html','_smoke_v26_4.html').replace('SMOKE v26.3 OK','SMOKE v26.4 OK')
(ROOT/'tools/smoke_v26_4.py').write_text(new,encoding='utf-8')

# Workflow permanente: current version + Rules v26.4
p=ROOT/'.github/workflows/validate-fdo.yml';w=p.read_text(encoding='utf-8')
w=one(w,"      - name: Smoke de boot offline em navegador v26.3\n        run: python3 tools/smoke_v26_3.py\n","      - name: Testar segurança Firebase v26.4\n        run: node tools/test_v26_4.js\n      - name: Smoke de boot offline em navegador v26.4\n        run: python3 tools/smoke_v26_4.py\n",'workflow v26.4')
w=w.replace('tools/test_database_rules_v26_3.js','tools/test_database_rules_v26_4.js')
p.write_text(w,encoding='utf-8')

# O teste experimental v26.3 das Rules nunca foi publicado; remove para não deixar duplicidade.
(ROOT/'tools/test_database_rules_v26_3.js').unlink(missing_ok=True)

print('PATCH v26.4 aplicado: cliente + cache + testes + workflow')
