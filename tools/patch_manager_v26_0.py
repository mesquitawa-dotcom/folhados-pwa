from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML = ROOT / 'index.html'
TEST = ROOT / 'tools' / 'test_estoque_v26_0.js'
SELF = ROOT / 'tools' / 'patch_manager_v26_0.py'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: esperado 1 marcador, encontrado {count}')
    return text.replace(old, new, 1)


html = HTML.read_text(encoding='utf-8')

html = replace_once(
    html,
    '<div class="est-note"><b>Saldo calculado</b> = entradas recebidas − insumos das receitas. A conferência física semanal fica separada e nunca altera esse cálculo.</div>',
    '<div class="est-note" id="estoque-nota"><b>Saldo calculado</b> = entradas recebidas − insumos das receitas. A conferência física semanal fica separada e nunca altera esse cálculo.</div>',
    'identificação da nota de estoque',
)
html = replace_once(
    html,
    '<button class="btn-sec" onclick="abrirEstoqueMovimentos()">📋 Movimentações</button>',
    '<button class="btn-sec" id="estoque-btn-mov" onclick="abrirEstoqueMovimentos()">📋 Movimentações</button>',
    'identificação do botão de movimentações',
)

old_transaction = """      const r=await FB.db.ref('fdo_v25/estoque/meta/inicioTs').transaction(cur=>Number(cur)||local,undefined,false);
      this.inicioTs=Number(r.snapshot.val())||local;try{localStorage.setItem('fdo_estoque_inicio_ts_v26',JSON.stringify(this.inicioTs))}catch{};"""
new_transaction = """      const r=await FB.db.ref('fdo_v25/estoque/meta/inicioTs').transaction(cur=>{
        const atual=Number(cur)||0;return atual>0?Math.min(atual,local):local;
      },undefined,false);
      this.inicioTs=Number(r.snapshot.val())||local;try{localStorage.setItem('fdo_estoque_inicio_ts_v26',JSON.stringify(this.inicioTs))}catch{};"""
html = replace_once(html, old_transaction, new_transaction, 'menor marco de início entre aparelhos')

old_render = """function renderEstoque(){
  estoqueReconciliarSaidasLotes();const saldos=estoqueSaldos(),cont=estoqueUltimaContagem(),fis=(cont&&cont.valores)||{};
  const info=document.getElementById('estoque-ultima');if(info)info.textContent=cont?('Conferência de '+(estoqueDataISO(cont.data)||estoqueDataCurta(cont.emTs))+' · '+(cont.op||'—')):'Ainda não há conferência física semanal.';
  const ins=document.getElementById('estoque-insumos');if(ins)ins.innerHTML=estoqueInsumos().map(it=>{
    const tem=Object.prototype.hasOwnProperty.call(fis,it.id),f=tem?Number(fis[it.id])||0:null,d=tem?f-(Number(saldos[it.id])||0):null;
    return `<div class="est-item"><div class="est-item-top"><b>${_escHtml(it.nome)}</b><span class="est-sistema">Sistema ${estoqueFmt(it.id,saldos[it.id])}</span></div><div class="est-item-sub">${tem?('Conferido '+estoqueFmt(it.id,f)+' · diferença <span style="color:'+estoqueCorDif(d)+'">'+(d>0?'+':'')+estoqueFmt(it.id,d)+'</span>'):'Conferência física: não informada'}</div></div>`;
  }).join('');
  const emb=document.getElementById('estoque-embalagens');if(emb)emb.innerHTML=estoqueEmbalagens().map(it=>`<div class="est-item"><div class="est-item-top"><b>${_escHtml(it.nome)}</b><span class="est-sistema">${Object.prototype.hasOwnProperty.call(fis,it.id)?estoqueFmt(it.id,fis[it.id]):'Não conferido'}</span></div><div class="est-item-sub">Somente saldo físico semanal nesta etapa.</div></div>`).join('');
  const bE=document.getElementById('estoque-btn-entrada'),bC=document.getElementById('estoque-btn-contagem');if(bE)bE.style.display=OP.pode('estoque_entrada')?'':'none';if(bC)bC.style.display=OP.pode('estoque_contagem')?'':'none';
}"""
new_render = """function renderEstoque(){
  estoqueReconciliarSaidasLotes();const saldos=estoqueSaldos(),cont=estoqueUltimaContagem(),fis=(cont&&cont.valores)||{},gerencia=OP.pode('estoque_entrada');
  const nota=document.getElementById('estoque-nota');if(nota)nota.innerHTML=gerencia?'<b>Saldo calculado</b> = entradas recebidas − insumos das receitas. A conferência física semanal fica separada e nunca altera esse cálculo.':'<b>Conferência semanal</b> · informe as quantidades físicas encontradas. A comparação com o saldo calculado fica reservada à gerência.';
  const info=document.getElementById('estoque-ultima');if(info)info.textContent=cont?('Conferência de '+(estoqueDataISO(cont.data)||estoqueDataCurta(cont.emTs))+' · '+(cont.op||'—')):'Ainda não há conferência física semanal.';
  const ins=document.getElementById('estoque-insumos');if(ins)ins.innerHTML=estoqueInsumos().map(it=>{
    const tem=Object.prototype.hasOwnProperty.call(fis,it.id),f=tem?Number(fis[it.id])||0:null,d=tem?f-(Number(saldos[it.id])||0):null;
    if(!gerencia)return `<div class="est-item"><div class="est-item-top"><b>${_escHtml(it.nome)}</b><span class="est-sistema">${tem?estoqueFmt(it.id,f):'Não conferido'}</span></div><div class="est-item-sub">Última quantidade física registrada.</div></div>`;
    return `<div class="est-item"><div class="est-item-top"><b>${_escHtml(it.nome)}</b><span class="est-sistema">Sistema ${estoqueFmt(it.id,saldos[it.id])}</span></div><div class="est-item-sub">${tem?('Conferido '+estoqueFmt(it.id,f)+' · diferença <span style="color:'+estoqueCorDif(d)+'">'+(d>0?'+':'')+estoqueFmt(it.id,d)+'</span>'):'Conferência física: não informada'}</div></div>`;
  }).join('');
  const emb=document.getElementById('estoque-embalagens');if(emb)emb.innerHTML=estoqueEmbalagens().map(it=>`<div class="est-item"><div class="est-item-top"><b>${_escHtml(it.nome)}</b><span class="est-sistema">${Object.prototype.hasOwnProperty.call(fis,it.id)?estoqueFmt(it.id,fis[it.id]):'Não conferido'}</span></div><div class="est-item-sub">Somente saldo físico semanal nesta etapa.</div></div>`).join('');
  const bE=document.getElementById('estoque-btn-entrada'),bC=document.getElementById('estoque-btn-contagem'),bM=document.getElementById('estoque-btn-mov');if(bE)bE.style.display=gerencia?'':'none';if(bC)bC.style.display=OP.pode('estoque_contagem')?'':'none';if(bM)bM.style.display=gerencia?'':'none';
}"""
html = replace_once(html, old_render, new_render, 'visão gerencial separada da conferência')

html = replace_once(
    html,
    "function abrirEstoqueMovimentos(){renderEstoqueMovimentos();ir('estoque-mov');}",
    "function abrirEstoqueMovimentos(){if(!OP.pode('estoque_entrada')){alert('A comparação e as movimentações ficam disponíveis somente para a gerência.');return;}renderEstoqueMovimentos();ir('estoque-mov');}",
    'proteção da tela de movimentações',
)

HTML.write_text(html, encoding='utf-8')

test = TEST.read_text(encoding='utf-8')
anchor = "ok(html.includes(\"estoqueDataISO(cont.data)||estoqueDataCurta(cont.emTs)\"),'data selecionada da conferência não é exibida');\n"
checks = """ok(html.includes('Math.min(atual,local)'),'marco de início não preserva o primeiro aparelho atualizado');
ok(html.includes("gerencia=OP.pode('estoque_entrada')"),'visão gerencial do estoque não está separada');
ok(html.includes('id="estoque-btn-mov"'),'botão de movimentações sem controle de visibilidade');
ok(html.includes('A comparação e as movimentações ficam disponíveis somente para a gerência.'),'acesso direto às movimentações não está protegido');
"""
test = replace_once(test, anchor, anchor + checks, 'testes de gerência e marco inicial')
TEST.write_text(test, encoding='utf-8')

try:
    SELF.unlink()
except FileNotFoundError:
    pass

print('SEPARAÇÃO DA VISÃO GERENCIAL v26.0 APLICADA')
