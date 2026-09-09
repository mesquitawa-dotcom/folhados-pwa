# Folhados d'Ouro — Resumo v26.6.2

## 1. IDENTIFICAÇÃO
- Revisão: **v26.6.2 — Correção do avanço no porcionamento**.
- Repositório: `mesquitawa-dotcom/folhados-pwa`.
- Base conferida: v26.6.1, commit `c09b652ad079a02b5bb93fac31d71d61669edde3`.
- Cache: `fdo-v26-6-2` (anterior `fdo-v26-6-1`).
- Branch: `agent/corrigir-porcionamento-v26-6-2`.
- Restauração: `backup/pre-v26-6-2-2026-09-08`, na base v26.6.1.
- Fonte de verdade: código vigente no `main`; confirmar HEAD, PR e publicação no GitHub antes de novas alterações.

## 2. PRESERVADO
Arquitetura vanilla em `index.html`, tema escuro/dourado e Georgia, dados/snapshots, históricos, Firebase SDK local, App Check, autorização dos aparelhos, operadores, PINs, voz, impressão Bluetooth e funcionamento offline-first.
Manifest, ícones, Rules, vendor, cálculos, receitas, pesos, fermentos, tempos e parâmetros de produtos permanecem inalterados. O JavaScript de produção é idêntico à v26.6.1, exceto pelo número de versão nos metadados da exportação de backup.
Não foi iniciado Fermentação Final/Forno v26.7.

## 3. PORCIONAMENTO — CORREÇÃO v26.6.2
Problema reproduzido: na tela `s-pre-temp`, o botão existente **Definir Fermento →** era empurrado para fora da área visível em telas menores. A barra Voltar da v26.6.1 aumentou a altura ocupada; o contêiner do clima não rolava e a tela cortava o excedente. A previsão carregava, mas o operador não alcançava o avanço.
Correção somente de apresentação: reaproveita `ux-compact` no cabeçalho, reduz espaçamentos do cartão, torna a previsão rolável e move o mesmo botão para o rodapé fora da área rolável. Texto e handler `escolherTemp()` preservados; ID do botão: `pre-temp-continuar`. Voltar permanece no alto e recupera os lotes preenchidos.
A previsão continua sem bloquear a produção quando falha ou demora. R1–R3 seguem para as opções existentes de fermentação; R4/R5 mantêm seu fermento fixo e seguem para os ingredientes. Nenhum avanço automático nem escolha de fermento nova foi introduzido.
Funções da v26.6.1 preservadas: Mesmos lotes no alto; autorização administrativa temporária para múltiplos baldes; IDs/snapshots/baixas individuais; diário recuperável `fdo_baldes_pendentes_v2661`; etiquetas 1–8; revisão antes da gravação e proteção contra duplicidade.

## 4. LAMINAÇÃO / CORTE
Sem alteração nesta revisão. Duas entradas: Primeira laminação e Laminação final — Corte/Fatias.
Novas primeiras laminações usam exatamente duas massas compatíveis e registram `modeloFisico:'duas_massas_v1'`, `massasComManteiga:1`. Legados não são reinterpretados.
Corte retomável exige quantidade real e confirmação de encerramento; `etapas.corte` e `corteEventos` preservam trilha. Gravar corte não registra frio automaticamente. Proteção contra duplo toque e rechecagem de saldo preservadas.

## 5. FRIO / MODELAGEM
Sem alteração: corte → freezer rápido → freezer conservador → descongelamento → modelagem/formas. Filas e próxima ação, conferência de modelagem, saldo válido, composição de origens e históricos preservados.
Cancelar pergunta de temperatura não grava descongelamento; confirmar em branco mantém temperatura ausente.

## 6. ETIQUETAS / RETORNO
Sem alteração na impressão: etiquetas de baldes 1–8; fatias com quatro faixas horizontais por etiqueta grande; transporte e linguagens anteriores preservados.
Retorno visível e histórico do navegador/gesto Android preservados. Gravação/impressão em andamento bloqueiam retorno; telas de autorização não podem ser contornadas.

## 7. VALIDAÇÃO E ARQUIVOS
Passaram localmente: validação estrutural, sintaxe JavaScript extraída e `sw.js`, handlers/IDs, manifest/assets/cache e todas as suítes Node anteriores; 50 verificações de usabilidade e 192 verificações novas de porcionamento em Chromium com DOM/armazenamento isolados.
O teste novo reproduz a falha na base e testa nove combinações de viewport/fonte, retorno com lotes preservados e 15 fluxos completos (cinco receitas × previsão disponível, falha ou pendente), até balde, baixa única de estoque e abertura da etiqueta. Inclui a regra anterior de saltar manteiga de peso zero.
Na preparação GitHub Actions `34299897026`, passaram as mesmas 192 verificações novas e 50 anteriores em navegador com origem e localStorage reais, além das suítes Node, validação estrutural e smoke de boot.
CI permanente passou a incluir `tools/test_porcionamento_v26_6_2.py`, usando navegador com origem local e localStorage reais, junto do smoke de boot, regressões anteriores e Firebase Emulator. Confirmar a execução correspondente ao commit de entrega no GitHub.
Totais preservados: R1 **15.464 g**; R2 **15.690 g**; R3 **15.544 g**; R4 **15.564 g**; R5 **15.714 g**; Receita Teste de referência **15.448 g**.
Arquivos da entrega: `index.html`, `sw.js`, `tools/validate_fdo.py`, `tools/test_v26_6.js`, `.github/workflows/validate-fdo.yml`, novo `tools/test_porcionamento_v26_6_2.py` e este Resumo. Preparação/diagnóstico temporários não integram a entrega.
Android físico e impressora Bluetooth física não foram testados nesta sessão; testar o fluxo no aparelho da fábrica após atualizar.

## 8. CONTINUIDADE / REVERSÃO
Atualizar pelo fluxo normal do PWA: recarregar conectado, fechar/abrir e conferir **Versão 26.6.2 · cache fdo-v26-6-2** em Configurações. Não limpar dados do site nem desinstalar como primeira medida.
Restauração de código: commit `c09b652ad079a02b5bb93fac31d71d61669edde3` / branch de backup. Reverter por novo commit, sem force push; uma reversão publicada exige outro identificador de cache, não recolocar o antigo. Este backup de código não substitui backup dos dados locais/Firebase.
Substituir o Resumo anterior nas Fontes do Projeto por este após confirmar a publicação. Regressão de apresentação não exigiu migração nem alterações no Firebase real.
Pendências externas anteriores preservadas: confirmação das Rules v26.6 no Firebase real; testes físicos de Android, voz e impressão. Não executar mudanças de segurança ou de processo junto deste hotfix.
