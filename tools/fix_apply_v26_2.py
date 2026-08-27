from pathlib import Path

p=Path(__file__).with_name('apply_v26_2.py')
s=p.read_text(encoding='utf-8')

# 1) O apply da v26.1 reaplica receitas antes de marcar ready.
ini=s.index('rep("    this.save(nome,arr);this.ready[nome]=true')
fim=s.index(",'apply sync v262')",ini)+len(",'apply sync v262')")
novo='''rep("    this.save(nome,arr);if(nome==='receitas')aplicarReceitasDefinitivas();this.ready[nome]=true;FB.repaint();this.flush();\\n    if(nome==='movimentos')estoqueReconciliarSaidasLotes();","""    this.save(nome,arr);if(nome==='receitas')aplicarReceitasDefinitivas();this.ready[nome]=true;FB.repaint();this.flush();
    if(nome==='movimentos')estoqueReconciliarSaidasLotes();
    if(nome==='receitas')setTimeout(()=>{try{migrarBatimentoReceitasV262();}catch(e){console.warn('[RECEITAS] migração batimento',e)}},0);
    if(nome==='configuracoes')setTimeout(()=>{try{const vis=document.querySelector('.scr:not(.off)');if(vis&&vis.id==='s-start')estoqueChecarLembreteContagem();}catch(e){}},0);""",'apply sync v262')'''
s=s[:ini]+novo+s[fim:]

# 2) A nova coleção precisa existir também na estrutura da outbox.
mar="rep(\"    contagens:{local:'fdo_estoque_contagens',path:'fdo_v25/estoque/contagens'},\",\"    contagens:{local:'fdo_estoque_contagens',path:'fdo_v25/estoque/contagens'},\\n    configuracoes:{local:'fdo_estoque_configuracoes',path:'fdo_v25/estoque/configuracoes'},\",'sync config estoque')"
if mar not in s: raise SystemExit('marcador sync config estoque ausente')
s=s.replace(mar,mar+"\nrep(\"  out(){const base={movimentos:{},contagens:{},observacoes:{},receitas:{},auditoria:{}};\",\"  out(){const base={movimentos:{},contagens:{},configuracoes:{},observacoes:{},receitas:{},auditoria:{}};\",'outbox config estoque')",1)

# 3) Receita criada de um teste antigo recebe a configuração efetiva daquele balde.
mar2="# ── configuração do lembrete de estoque ──────────────────────────────"
if mar2 not in s: raise SystemExit('marcador antes do lembrete ausente')
extra="""# ── aprovação de teste antigo preserva batimento efetivo ──────────────
rep("const rid=FB.novoId('rec'),rec=clonarReceita(l.receitaSnapshot);rec.nome=","const rid=FB.novoId('rec'),rec=clonarReceita(l.receitaSnapshot);rec.batimento=clonarReceita((l.receitaSnapshot&&l.receitaSnapshot.batimento)||l.batimentoConfig||(l.etapas&&l.etapas.batimento&&l.etapas.batimento.temposProgramados)||batTemposBaseLegado());rec.nome=",'aprovação herda batimento')

"""
s=s.replace(mar2,extra+mar2,1)

p.write_text(s,encoding='utf-8')
print('Aplicador v26.2 corrigido')
