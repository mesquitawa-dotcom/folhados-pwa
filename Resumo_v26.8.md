# Folhados d'Ouro — Resumo v26.8

## 1. IDENTIFICAÇÃO
- Entrega: **v26.8 — reaproveitamento variável da R2 e navegação sem loops**.
- Repositório: `mesquitawa-dotcom/folhados-pwa`.
- Base anterior: v26.7, `b92bea6db598c3700e2335ffc2d3aaf940bb1513`.
- Código publicado: `bc350c66abd44298dffb0618cb2d53a417bdc206`.
- Cache: `fdo-v26-8` (anterior `fdo-v26-7`).
- Branch de desenvolvimento: `agent/aproveitamento-usabilidade-v26-8`.
- Pull Request de código: **#19**, revisado pelo Wagner e mesclado em 03/11/2026.
- Restauração: `backup/pre-v26-8-2026-11-03`, apontando para a v26.7.
- Fonte de verdade continua sendo o código vigente no `main`; este Resumo é documentação de continuidade.

## 2. PRESERVADO
Arquitetura vanilla concentrada em `index.html`, tema escuro/dourado e Georgia, PWA, Firebase, App Check, autorização de aparelhos, operadores/PINs, voz, impressão Bluetooth, estoque, snapshots, históricos e todos os módulos v26.7.
Manifest, identidade instalada, ícones, vendor e Rules não foram alterados.
Totais das receitas definitivas preservados: R1 **15.464 g**, R2 **15.690 g**, R3 **15.544 g**, R4 **15.564 g**, R5 **15.714 g**; teste de referência **15.448 g**.
Fermento da R2 continua definido exclusivamente pelo fluxo existente de temperatura/horas.

## 3. R2 — MASSA REAPROVEITADA VARIÁVEL
A R2 verificada pode informar, por execução, de **0 a 3.000 g** de massa reaproveitada já laminada com manteiga, em passos compatíveis com balança de **2 g**.
Fluxo: **Receita → Massa reaproveitada → Lotes das farinhas → Clima → Fermento → Porcionamento**.
O padrão de 3.000 g mantém exatamente os pesos vigentes da R2. Quantidades menores recalculam somente a cópia daquela execução (`st.receitaExecucao`); a receita definitiva não é modificada.
Regra automática fica bloqueada se a R2 vigente não coincidir exatamente com o padrão verificado. Não aplicar a mesma fórmula a R1/R3/R4/R5 sem composição confirmada.
Cenários automatizados conferidos: **0 g, 1.200 g, 1.500 g e 3.000 g**. No cenário de 1.200 g: Bagatelle 3.870 g, Italiana 00 4.730 g, açúcar 970 g, água 3.950 g, leite 194 g, manteiga 428 g e sal 194 g.

## 4. REGISTRO E ESTOQUE
Cada balde salva a receita efetivamente executada em `receitaSnapshot`, incluindo metadados do reaproveitamento: padrão, quantidade usada, perfil e passo da balança.
O Histórico mostra a massa reaproveitada usada e o padrão da receita.
Ao retomar Líquidos, os pesos vêm do snapshot daquele balde, não da receita definitiva atual.
A baixa automática de estoque continua baseada no snapshot da execução, portanto acompanha os ingredientes realmente usados.
Na geração administrativa de vários baldes iguais, a quantidade informada é **por balde** e a tela mostra o total de massa reaproveitada necessário.

## 5. NAVEGAÇÃO
Corrigido o mecanismo central de `Voltar` introduzido anteriormente: a navegação de retorno não reinsere a tela atual na pilha e não forma mais “pingue-pongue”.
Retornos semânticos do porcionamento:
- Reaproveitamento → Receitas.
- Lotes → Reaproveitamento quando a etapa estiver ativa; caso contrário → Receitas/teste correspondente.
- Clima → Lotes.
- Fermento → Clima.
Quando não existe retorno anterior seguro, `Voltar` cai para **Início**.
Cabeçalhos permanecem compactos para não prejudicar telas pequenas; não foi adicionado botão extra de Home indiscriminadamente.

## 6. VALIDAÇÃO
Antes do merge, CI da branch: execução **41671026322 / run 273**, com `validate`, `usabilidade` e `firebase-rules` em sucesso.
Após o merge, CI do `main`: execução **41673020196 / run 275**; todos os três jobs e suas etapas concluíram com sucesso.
GitHub Pages: execução **41673019764 / run 68**; build, deploy e report concluídos com sucesso.
O teste v26.8 percorreu em Chromium a R2 com 1.200 g desde seleção da receita, retornos sem loop, secos e geração do balde até Histórico e retomada dos Líquidos.
Regressões anteriores permaneceram verdes, inclusive telas pequenas e fonte grande (até 320×568 com fonte 33 px), boot offline, Firebase Emulator e suites v25–v26.7.
Testes usam dados sintéticos. Android físico, voz, impressora Bluetooth e Firebase de produção não foram alterados nesta entrega.

## 7. ARQUIVOS ALTERADOS
Código/PWA: `index.html`, `sw.js`.
Validação: `tools/validate_fdo.py`, `tools/test_v26_6.js`, `tools/test_porcionamento_v26_6_2.py`, `tools/test_v26_8.js`, `tools/test_v26_8.py`, `.github/workflows/validate-fdo.yml`.
Este `Resumo_v26.8.md` é documentação posterior ao commit de código publicado e não altera o comportamento do PWA.

## 8. CONTINUIDADE / REVERSÃO
Nos aparelhos: recarregar conectado, fechar e abrir novamente e conferir em Configurações **Versão 26.8 · cache fdo-v26-8**. Não limpar dados nem desinstalar como primeira medida.
Teste operacional inicial recomendado: executar uma R2 com quantidade conhecida de reaproveitamento, conferir os pesos antes de pesar e confirmar no Histórico a quantidade registrada.
Reversão: criar novo commit a partir de `backup/pre-v26-8-2026-11-03` / v26.7, sem force push. Uma reversão publicada deve usar novo identificador de cache; não reutilizar `fdo-v26-7`.
Próximo passo possível: validar a composição de reaproveitamento das demais receitas antes de habilitar ajuste variável nelas. Nunca reutilizar automaticamente a fórmula da R2.
