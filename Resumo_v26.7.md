# Folhados d'Ouro — Resumo v26.7

## 1. IDENTIFICAÇÃO
- Entrega: **v26.7 — Formas nos armários, assamento e rastreabilidade do fluxo**.
- Repositório: `mesquitawa-dotcom/folhados-pwa`.
- Base conferida: v26.6.2, `3472acaff69bb4b09cd44f61e0bd27d0231f7726`.
- Cache: `fdo-v26-7` (anterior `fdo-v26-6-2`).
- Branch: `agent/fluxo-formas-rastreabilidade-v26-7`.
- Pull Request: **#15**.
- Código revisado antes da publicação: `2d693e0d87446b762d0ce24efda0b3047249be99`; esta revisão do Resumo altera somente documentação.
- Restauração: `backup/pre-v26-7-2026-09-09`, confirmada na base acima.
- Fonte de verdade: código vigente no `main`; confirmar HEAD, PR, CI e publicação antes de novas alterações. O commit final de publicação deve ser consultado no merge do PR #15, não inferido do commit de preparação.

## 2. PRESERVADO
Arquitetura vanilla concentrada em `index.html`, tema escuro/dourado e Georgia, snapshots, históricos, Firebase local, App Check, autorização dos aparelhos, operadores/PINs, voz e impressão Bluetooth.
Sem mudança no manifest, identidade instalada, ícones, vendor, Rules, receitas, pesos, fermentos, temperaturas/tempos prescritos ou configurações dos produtos.
Totais: R1 **15.464 g**, R2 **15.690 g**, R3 **15.544 g**, R4 **15.564 g**, R5 **15.714 g**; teste de referência **15.448 g**.
Porcionamento, batimento, laminação, corte, frio, modelagem, estoque e mecanismos offline anteriores permanecem. Nenhuma limpeza/migração destrutiva de dados de produção.

## 3. MODELO FÍSICO E SEQUENCIAMENTO
Diretriz do Wagner: visualizar rapidamente todos os estágios e as junções/desmembramentos, com poucas ações e aproveitando o que já foi lançado.
Fluxo rastreável: **balde → massas do batimento → massa laminada → fatias/produtos → croissants nas formas → armário → assamento**.
O exemplo de 8 massas por balde não virou regra fixa: usamos as partes realmente registradas em `etapas.batimento.partes`; o divisor/configuração anterior não foi alterado. A primeira laminação nova continua usando exatamente duas massas compatíveis. Registros antigos não ganham nova interpretação física.
As massas intermediárias continuam vinculadas por quantidade ao balde, sem inventar IDs individuais de cada parte. Fatias guardam sua laminação; formas guardam todas as partidas/quantidades consumidas. Composição e sobras compatíveis da modelagem anterior são preservadas. Quantidade por forma continua a real, com a sugestão já existente por produto (não fixa 16 para todos os produtos).

## 4. FERMENTAÇÃO CORRIGIDA
A entrada do módulo mantém o nome Fermentação, mas **seleciona formas com croissants, nunca baldes**.
- Formas prontas: informar o número real do armário, selecionar individualmente ou até as vagas disponíveis, revisar e confirmar a colocação física.
- Nos armários: grupos por armário, **máximo de 20 formas**, seleção individual ou do grupo, conferência do ponto e retirada real para assamento.
- Entrada/saída gravam horário de confirmação, operador/aparelho e armário. Abrir a tela não inicia cronômetro. Tempo decorrido não conclui processo nem substitui avaliação do ponto.
- Temperaturas mínima/máxima da retirada são medições opcionais, inicialmente vazias; zero é válido. Não presumir 24°C/28°C nem criar receita/tempo novo.
- Saída parcial libera só as vagas das formas efetivamente retiradas. Formas já retiradas ficam pré-selecionadas em Assamento quando o operador tem acesso.
Registros antigos em `balde.etapas.fermentacao` continuam intocados no Histórico, identificados como **legado**; não foram transformados automaticamente em formas ou entradas de armário.

## 5. ASSAMENTO E VISUALIZAÇÃO
Menu **Forneamento** ativado, com tela Assamento: **Para assar → No forno → Assamento concluído**. Entrada e conclusão são manuais, em seleção de formas, com revisão física. Não se presume capacidade do forno, temperatura, tempo ou programa.
Novo atalho inicial **Ver fluxo e estágios da produção**: painel compacto de dez estágios com saldos separados; tocar leva à fila/ação existente quando permitida.
Histórico ganha Massas laminadas, Fatias cortadas/produtos e Formas, com busca e carregamento incremental. Cada registro exibe estágio, próxima ação, **De onde veio**, **O que gerou** e eventos. Ligações preservam junções/divisões e chegam aos baldes de origem. Origem indisponível é indicada, não reconstruída.
Voltar funciona entre os níveis de rastreio; revisões já confirmadas não reaparecem como tarefas pendentes. Telas novas têm retorno visível, conteúdo rolável e confirmação fixa; revisão e resultado são falados, mas quantidade e ponto exigem conferência visual.
**Limite desta entrega:** acompanha até conclusão do assamento nas mesmas formas. Não registra embalagem, expedição, descarte/perdas ou estoque de unidades vendáveis. O total assado no painel é cumulativo do Histórico e não equivale a produto embalado/expedido.

## 6. DADOS, CONCORRÊNCIA E PERMISSÕES
Usa a coleção existente `fdo_v25/formas` / `fdo_formas`, sem novo backend/path. Novos campos opcionais: `fluxoVersao:1` e `eventos.entradaArmario`, `saidaArmario`, `assamentoInicio`, `assamentoFim`, com identificação de operação e metadados.
**Confirmações novas de armário/assamento exigem conexão e sincronização das formas.** A operação é uma transação na coleção de formas: revalida estágio, origem/quantidade, operador, horário e ocupação; grava todas as selecionadas ou nenhuma. Não anuncia sucesso offline. Consulta/rastreio continuam offline após receber os dados, e os fluxos offline anteriores não foram removidos.
Duplo toque bloqueado; retry da mesma operação é idempotente. A mesclagem de formas do cliente atualizado preserva etapas existentes contra cópias desatualizadas. Exclusão de forma que já avançou é bloqueada na interface atual, preservando as fatias consumidas.
Nova permissão de interface `forneamento`: apenas quando ausente, herda `fermentacao`; negativa explícita permanece. Não constitui nova segurança de banco: as Rules existentes continuam sendo a autorização dos aparelhos. Nenhuma Rule foi publicada nesta sessão.
**Atualizar todos os aparelhos antes de operar os novos estágios.** Clientes antigos não têm os novos bloqueios de estágio/exclusão; não afirmar garantia de imutabilidade de formas contra cliente antigo ou gravação direta autorizada no banco. Endurecimento de esquema/regras fica para alteração dedicada.

## 7. VALIDAÇÃO E ARQUIVOS
Preparação local: validação estrutural/sintaxe extraída, handlers/IDs, manifest/assets/cache, receitas, todas as suítes Node anteriores e **43 verificações novas** do núcleo de formas. Comparação integral das receitas, tempos, fermentos e produtos com a base v26.6.2: idênticos.
**CI do PR #15 conferida com sucesso:** execução `34311790851`, correspondente ao código `2d693e0d87446b762d0ce24efda0b3047249be99` e ao merge de teste `4a8db5bda7378c89d31510d82eead2bbf0be2dad`. Jobs `validate`, `usabilidade` e `firebase-rules` concluídos com sucesso.
Foram confirmadas **151 verificações novas em Chromium com origem/localStorage reais**, nove combinações de viewport/fonte, comparação das receitas com a base e as regressões anteriores de usabilidade e porcionamento. O artefato `10088629304` contém resultados e capturas de tela com dados sintéticos; telas de armário, painel e rastreio foram inspecionadas na revisão final.
No Firebase Emulator passaram **12 verificações novas**, incluindo dois aparelhos disputando a última vaga (apenas um obtém a vaga), retirada parcial, atomicidade de grupos, retry, preservação de eventos na mesclagem e manutenção da autorização existente. Também passaram a suíte de Rules anterior e o smoke de boot.
Esta atualização do Resumo não substitui a conferência da CI do commit final e do deploy após o merge. Android, voz, impressora Bluetooth e Firebase de produção físicos/reais não foram testados nem alterados nesta sessão. Testes usam dados sintéticos.
Arquivos: `index.html`, `sw.js`, `tools/validate_fdo.py`, `tools/test_v26_6.js`, `tools/test_porcionamento_v26_6_2.py`, `.github/workflows/validate-fdo.yml`, `tools/fluxo_v26_7_test_helper.js`, `tools/test_fluxo_v26_7.js`, `tools/test_fluxo_v26_7.py`, `tools/test_fluxo_emulator_v26_7.js`, este Resumo.
O teste do hotfix de porcionamento passou a comparar suas funções preservadas, em vez de exigir que todo o JavaScript permaneça idêntico e impedir os novos módulos autorizados. Verificações de receitas, geometria e fluxos completos permanecem.

## 8. CONTINUIDADE / REVERSÃO
Após publicação confirmada: recarregar conectado, fechar/abrir o PWA e conferir **Versão 26.7 · cache fdo-v26-7** em Configurações em todos os aparelhos. Não limpar dados nem desinstalar como primeira medida. Testar primeiro uma pequena seleção de formas reais, confirmando seu armário físico, retirada e assamento.
Reversão por novo commit a partir do histórico/backup, sem force push; uma reversão publicada precisa de identificador de cache NOVO. Backup de código não substitui backup dos dados locais/Firebase. Versão anterior não compreende os estágios novos: preservar/exportar os dados e suspender movimentações novas durante eventual reversão; não apagar os eventos.
Substituir o Resumo anterior nas Fontes do Projeto por este após publicação. Pendências externas anteriores mantidas: confirmação das Rules v26.6 no Firebase real e testes físicos de Android/voz/impressão. Evoluções futuras devem preservar o encadeamento e priorizar simplicidade do operador.
