# Folhados d'Ouro — Resumo v26.6.1

## 1. IDENTIFICAÇÃO
- Revisão: **v26.6.1 — Usabilidade e retorno seguro**, sem iniciar Fermentação Final/Forno v26.7.
- Repositório: `mesquitawa-dotcom/folhados-pwa`.
- Pull Request de entrega: **#13**. O status de merge/publicação deve ser confirmado no GitHub.
- Base conferida: v26.6, `04e3a34f6aba6436859a51b9c2c0e6216942492d`.
- Cache: `fdo-v26-6-1` (anterior `fdo-v26-6`).
- Branch: `agent/usabilidade-v26-6-1`.
- Restauração: `backup/pre-v26-6-1-usabilidade-2026-09-08`.
- Fonte de verdade: código vigente no `main`; confirmar o HEAD antes de novas alterações.

## 2. PRESERVADO
Arquitetura vanilla em `index.html`, tema escuro/dourado, Georgia, dados/snapshots, histórico, Firebase SDK local, App Check, autorização dos aparelhos, operadores, PINs, impressão Bluetooth e funcionamento offline-first.
Manifest, ícones, Rules, vendor e parâmetros de receitas/fermentos/tempos/produtos/capacidade de formas permanecem inalterados nesta revisão.
Não foi desenvolvido Fermentação Final nem Forno; módulo de Fermentação anterior preservado.

## 3. PORCIONAMENTO
“Mesmos lotes” no alto, com números visíveis para conferência e edição recolhida. Cabeçalho operacional compacto.
Voltar da confirmação final retorna ao último ingrediente sem perder o preenchimento. Após gerar os baldes, voltar não desfaz nem reabre a gravação concluída.
Múltiplos baldes exigem o PIN administrativo **já existente das Configurações**; autorização temporária por operador e sessão. Não se criou cargo novo de servidor nem segurança baseada apenas em esconder botão.
Cada balde tem ID/número/snapshot e baixa própria. `producaoConjunta` informa a geração em grupo; não são inventadas durações individuais. Balde simples mantém sua duração medida.
Diário local `fdo_baldes_pendentes_v2661` preserva IDs/números e permite retomar falha parcial. Incluído na exportação de backup. Retomada de múltiplos após reiniciar pede nova autorização.
Reimprimir não gera baldes nem movimenta estoque. Quantidade de etiquetas 1–8 independente da quantidade de baldes, com total explícito por balde/grupo.

## 4. LAMINAÇÃO / CORTE
Laminação agora abre duas entradas: Primeira laminação e Laminação final — Corte/Fatias.
Novas primeiras laminações usam exatamente duas massas e registram uma massa com manteiga (`modeloFisico:'duas_massas_v1'`, `massasComManteiga:1`). Regras existentes de compatibilidade mantidas.
Conclusão da primeira fase não abre o corte automaticamente. Corte pendente inclui massas de dias anteriores.
Registros antigos não são reinterpretados como novas massas físicas. Campos novos são opcionais.
Corte preserva produtos e quantidades sugeridas existentes, mas pede quantidade real; gravação não registra frio automaticamente. Corte parcial permanece na fila até confirmação explícita. `etapas.corte` e `corteEventos` conservam o encerramento/reabertura; não se presume corte completo em legados.
Proteção contra duplo toque e rechecagem de saldo antes de gravações assíncronas. Sequências locais reservadas por dia/tipo evitam números repetidos na mesma operação offline; IDs seguem como identidade, sem promessa de numeração global exclusiva entre aparelhos desconectados.

## 5. FRIO / MODELAGEM
Sequência existente preservada: corte → freezer rápido → freezer conservador → descongelamento → modelagem/formas.
Tela separa filas de frio/modelagem/formas, destaca próxima ação e recolhe detalhes técnicos. Modelagem exige conferência explícita, sem criar tempo/temperatura de processo.
Cancelar a pergunta de temperatura não grava descongelamento; confirmar em branco mantém temperatura ausente.
Forma somente usa saldo em estado `modelagem`; não consome automaticamente fatias congeladas ou ainda não conferidas. Mistura de origens é mostrada para confirmação e composição continua no histórico.

## 6. ETIQUETAS / RETORNO
Fatias usam quatro faixas horizontais por etiqueta grande; 1–8 grandes correspondem a 4–32 identificações menores. Produto, identificação, data e TESTE quando aplicável; não repetir total como conteúdo de cada embalagem.
Configurações técnicas da impressora ficam recolhidas. Transporte e linguagens de impressão anteriores preservados.
Retorno visível nas telas operacionais e integração com o histórico do navegador/gesto Android. Telas de autorização não podem ser contornadas; cronômetro usa saída segura existente; operação de gravação/impressão em andamento bloqueia retorno.

## 7. VALIDAÇÃO EXECUTADA
Validação estrutural, sintaxe JavaScript, handlers/IDs/assets/manifest/cache e todas as suítes anteriores de regressão passaram.
No GitHub Actions, execução `34291029511`, passaram o smoke real de boot autorizado, os **50 testes de usabilidade em navegador com origem local/localStorage reais** e o Firebase Emulator. A mesma suíte também passou no DOM isolado local.
Testes usam dados sintéticos e não alteram o Firebase de produção. O CI permanente inclui `tools/test_usabilidade_v26_6_1.py` e guarda capturas/resultados como artefato.
Receitas padrão preservadas: R1 15.464 g; R2 15.690 g; R3 15.544 g; R4 15.564 g; R5 15.714 g. Receita Teste de referência: 15.448 g. Comparação automática antes/depois incluiu receitas, fermentos, tempos e produtos.
Android físico, voz no ruído da fábrica e impressora Bluetooth física **não foram testados**. Conferir retorno/retomada e uma etiqueta real de quatro faixas antes de adotar a rotina na produção.

## 8. CONTINUIDADE / REVERSÃO
Atualizar aparelhos pelo fluxo normal do PWA, sem apagar dados/cache de produção. Conferir a versão em Configurações.
Ponto de restauração é de código, não substitui backup dos dados locais/Firebase. Não apagar chaves novas ao reverter. Uma reversão em aparelhos já atualizados precisa de novo identificador de cache, não apenas recolocar o antigo `sw.js`.
A confirmação da publicação das Rules v26.6 no Firebase real permanece pendência externa anterior. Esta revisão não altera nem publica Rules e não inicia v26.7.
