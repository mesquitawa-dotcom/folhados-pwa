from pathlib import Path

root=Path(__file__).resolve().parents[1]

# O re.sub do aplicador não deve transformar \n da confirmação em quebra física dentro da string JS.
p=root/'index.html'
s=p.read_text(encoding='utf-8')
ini=s.index('function salvarEdicaoReceita(){')
fim=s.index('async function aprovarTesteComoReceita',ini)
fn=r'''function salvarEdicaoReceita(){
  if(!OP.pode('receita_editar')||!receitaNuvemObrigatoria())return;const rid=st.receitaEditId,antes=st.receitaEditOriginal;if(!rid||!antes)return;const nome=String(document.getElementById('receita-edit-nome').value||'').trim();if(nome.length<2){alert('Informe o nome da receita.');return;}const motivo=String(document.getElementById('receita-edit-motivo').value||'').trim();if(motivo.length<8){alert('Escreva o motivo da alteração (mínimo de 8 caracteres).');document.getElementById('receita-edit-motivo').focus();return;}const v=receitaLerEditor();if(!v)return;const fixa=antes.fermentoFixo!=null,temp=fixa?v.temp:null,horas=fixa?v.horas:null,depois=receitaMontarEditada(antes,v,nome,temp,horas);depois.batimento=clonarReceita(v.batimento);const mudancas=receitaDiferencas(antes,depois);if(!mudancas.length){alert('Nenhuma alteração foi feita na receita.');return;}const resumo=mudancas.slice(0,16).join('\n')+(mudancas.length>16?'\n+'+(mudancas.length-16)+' alterações':'');if(!confirm('CONFIRMAR ALTERAÇÃO DE RECEITA\n\n'+resumo+'\n\nMotivo: '+motivo+'\n\nBaldes já existentes permanecerão com a receita anterior.'))return;
  const agora=new Date(),antReg=receitaDefRegistro(rid),reg={id:rid,numero:receitaNumero(rid,antes),ativo:true,origem:(antReg&&antReg.origem)||'receita_padrao',origemBaldeId:(antReg&&antReg.origemBaldeId)||null,origemTesteId:(antReg&&antReg.origemTesteId)||null,receita:clonarReceita(depois),criadoEm:(antReg&&antReg.criadoEm)||agora.toLocaleString('pt-BR'),criadoTs:(antReg&&antReg.criadoTs)||agora.getTime(),criadoPor:(antReg&&antReg.criadoPor)||getOp(),atualizadoEm:agora.toLocaleString('pt-BR'),atualizadoTs:agora.getTime(),atualizadoPor:getOp()};ESTOQUE_SYNC.localPush('receitas',reg);receitaRegistrarAudit('editada',rid,motivo,antes,depois,{mudancas});st.receitaEditId=null;st.receitaEditOriginal=null;alert('Receita alterada e registrada no histórico de alterações.');abrirReceitaCompleta(rid);
}
'''
s=s[:ini]+fn+s[fim:]
p.write_text(s,encoding='utf-8')

# Validador: v26.1 segue preservada, mas a versão corrente do backup é 26.2.
p=root/'tools/validate_fdo.py'
v=p.read_text(encoding='utf-8')
v=v.replace("'temposProgramados:clonarReceita','versao:'26.2''","'temposProgramados:clonarReceita',\"versao:'26.2'\"",1)
v=v.replace(',"versao:\'26.1\'"','',1)
p.write_text(v,encoding='utf-8')

# Teste de regressão do estoque deve provar a funcionalidade v26.0 preservada,
# sem exigir que a versão corrente continue sendo literalmente v26.1.
p=root/'tools/test_estoque_v26_0.js'
t=p.read_text(encoding='utf-8')
t=t.replace("ok(/atualização v26\\.1/.test(html),'cabeçalho v26.1 ausente');","ok(html.includes('NOVIDADES v26.1')&&html.includes('NOVIDADES v26.0'),'histórico funcional v26.0/v26.1 ausente');",1)
p.write_text(t,encoding='utf-8')

print('Arquivos gerados v26.2 corrigidos')
