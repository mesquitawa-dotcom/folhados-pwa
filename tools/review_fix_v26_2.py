from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'index.html'
s=p.read_text(encoding='utf-8')

def troca(old,new,label,expected=None):
    global s
    n=s.count(old)
    if expected is not None and n!=expected:
        raise SystemExit(f'{label}: esperado {expected}, encontrado {n}')
    if n<1:
        raise SystemExit(f'{label}: marcador não encontrado')
    s=s.replace(old,new)

# Revisão manual detectou que os IDs foram criados como bt1..bt4,
# mas a leitura usava b1..b4. Corrige sem tocar em nenhum valor de receita.
troca("document.getElementById('receita-edit-b'+c.k.slice(1))","document.getElementById('receita-edit-b'+c.k)",'IDs do editor',1)
troca("document.getElementById('teste-b'+c.k.slice(1))","document.getElementById('teste-b'+c.k)",'IDs da Receita Teste',2)

# Normalização robusta: campo ausente usa a base, nunca vira 0 por Number(null).
old="""function batTemposNormalizar(v,base){
  const b=base||{t1:getBatT1(),t2:getBatT2(),t3:getBatT3(),t4:getBatT4()},o={};
  BATIMENTO_CAMPOS.forEach(c=>{const n=Number(v&&v[c.k]);o[c.k]=(isFinite(n)&&n>=0)?n:Number(b[c.k]);});return o;
}"""
new="""function batTemposNormalizar(v,base){
  const b=base||{t1:getBatT1(),t2:getBatT2(),t3:getBatT3(),t4:getBatT4()},o={};
  BATIMENTO_CAMPOS.forEach(c=>{const tem=!!(v&&Object.prototype.hasOwnProperty.call(v,c.k)),n=tem?Number(v[c.k]):NaN;o[c.k]=(isFinite(n)&&n>=0)?n:Number(b[c.k]);});return o;
}"""
if s.count(old)!=1: raise SystemExit('normalizador de batimento não encontrado')
s=s.replace(old,new,1)

# Comentário técnico precisa refletir a arquitetura atual: tempos estão nas receitas sincronizadas.
s=s.replace("//   tempos do batimento, tara, qtd de etiquetas) NÃO sobem para a nuvem.","//   tara e qtd de etiquetas) NÃO sobem para a nuvem. Os tempos do batimento v26.2\n//   pertencem às receitas e sincronizam pela estrutura de receitas definitivas.",1)

p.write_text(s,encoding='utf-8')

# Fortalece o teste: valida o vínculo real entre t1..t4 e os IDs bt1..bt4,
# o fallback de valores ausentes e a preservação ao aprovar um teste.
p=ROOT/'tools/test_v26_2.js'
t=p.read_text(encoding='utf-8')
insert="""has("document.getElementById('receita-edit-b'+c.k)",'editor lê bt1..bt4 pelo ID correto');
has("document.getElementById('teste-b'+c.k)",'Receita Teste lê bt1..bt4 pelo ID correto');
assert(!html.includes("document.getElementById('receita-edit-b'+c.k.slice(1))"),'editor não pode procurar b1..b4');
assert(!html.includes("document.getElementById('teste-b'+c.k.slice(1))"),'Receita Teste não pode procurar b1..b4');
has("rec.batimento=clonarReceita((l.receitaSnapshot&&l.receitaSnapshot.batimento)",'teste aprovado preserva o batimento executado');
has("op.id!==cfg.operadorId",'lembrete precisa ser exclusivo do operador designado');
has("estoqueContagemFeitaNaData(hoje)",'lembrete não deve aparecer após contagem do dia');
has("sessionStorage.getItem(estoqueLembreteChave",'Mais tarde adia somente na sessão');
"""
marker="has('tempos:clonarReceita(batTemposRun','retomada guarda tempos');\n"
if marker not in t: raise SystemExit('marcador do teste v26.2 ausente')
t=t.replace(marker,marker+insert,1)

old="""vm.createContext(sandbox);vm.runInContext(decl+'\\n'+funcs+'\\nresult=batAgenda().map(x=>x.min);',sandbox);
assert.deepStrictEqual(Array.from(sandbox.result),[4,9,11,12],'agenda precisa somar os quatro intervalos da receita');"""
new="""vm.createContext(sandbox);vm.runInContext(decl+'\\n'+funcs+'\\nresult={agenda:batAgenda().map(x=>x.min),fallback:batTemposNormalizar({}, {t1:7,t2:8,t3:9,t4:10})};',sandbox);
assert.deepStrictEqual(Array.from(sandbox.result.agenda),[4,9,11,12],'agenda precisa somar os quatro intervalos da receita');
assert.deepStrictEqual(JSON.parse(JSON.stringify(sandbox.result.fallback)),{t1:7,t2:8,t3:9,t4:10},'campo ausente precisa usar a base, nunca virar zero');"""
if old not in t: raise SystemExit('simulação v26.2 não encontrada')
t=t.replace(old,new,1)
p.write_text(t,encoding='utf-8')

print('Revisão v26.2 aplicada')
