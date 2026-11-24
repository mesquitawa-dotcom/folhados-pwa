# Folhados d'Ouro — Resumo v26.8.2

## 1. IDENTIFICAÇÃO
- Entrega: **v26.8.2 — aviso de massa laminada reconfigurável e voz na tela Massa reaproveitada**.
- Repositório: `mesquitawa-dotcom/folhados-pwa`.
- Base anterior: v26.8.1, `41bb4c3bae958c77879069f49ecb008d8af57317` (`main` conferido em 24/11/2026).
- Código publicado: `bfa71b5678ed822ca9a47b0a7f63e8e47c96c087`, em 24/11/2026.
- Cache: `fdo-v26-8-2` (anterior `fdo-v26-8-1`).
- Branch de desenvolvimento: `agent/aviso-voz-v26-8-2`.
- Pull Request de código: **#25**, mesclado em 24/11/2026 por pedido do Wagner (publicação automática após testes aprovados).
- Restauração: `backup/pre-v26-8-2-2026-11-24`, que aponta para a v26.8.1 (`41bb4c3`).
- Fonte de verdade: código vigente no `main`.

## 2. PRESERVADO
Nenhuma receita, peso, fermento, tempo, regra de produção, histórico, Firebase/Rules, manifest, ícone, vendor ou impressão Bluetooth foi alterado.
Totais das receitas definitivas permanecem: R1 **15.464 g**, R2 **15.690 g**, R3 **15.544 g**, R4 **15.564 g**, R5 **15.714 g**; teste de referência **15.448 g**.
A regra de cálculo do reaproveitamento variável da R2 (`aprovCalcularR2`), a trava que libera a etapa (`aprovPerfilDisponivel`), os snapshots por balde e as etiquetas da v26.8.1 não foram modificados.
O caminho por toque da tela Massa reaproveitada funciona como antes. O reconhecimento de voz do porcionamento (`iniciarVoz`) não foi alterado.

## 3. AVISO NA ESCOLHA DA RECEITA
Em **Porcionamento → Porcionamento de Secos → Selecione a receita**, o cartão da receita com massa reaproveitada variável mostra, em letras brancas, na base do cartão: **MASSA LAMINADA RECONFIGURÁVEL**.
- Texto pedido pelo Wagner; gravado com acento em "RECONFIGURÁVEL".
- O aviso ocupa uma linha própria, abaixo do nome da receita e do botão **📋 Receita**. A linha de ícone, nome e botão ficou idêntica à dos demais cartões.
- Usa a mesma trava que abre a tela **Massa reaproveitada**: aparece somente quando a R2 vigente no aparelho coincide com o padrão verificado. Hoje apenas a R2 pode exibi-lo.

## 4. VOZ NA TELA MASSA REAPROVEITADA
Frases curtas deduzidas com autorização do Wagner em 24/11/2026 (podem ser trocadas depois).
O microfone liga ao abrir a tela e desliga ao sair dela por qualquer caminho. A voz só preenche a quantidade; a receita da execução muda apenas com "confirmar" (voz ou toque).

Comandos aceitos:
- **Quantidade**: "1200", "1.200 gramas", "2 quilos", "1 quilo e 200", "1 quilo e meio", "meio quilo".
- **"sem massa"** ou **"zero"**: 0 g.
- **"padrão"**: volta ao padrão da receita.
- **"confirmar"** / "confirma" / "confirmado" / "continuar": confirma e segue para os lotes das farinhas.
- **"voltar"**: retorna às receitas. **"repetir"**: repete o valor atual.
- Frases com "não" são ignoradas. Valor ímpar, acima do padrão ou decimal sem unidade é recusado e o campo não muda.

Falas do app:
- Ao abrir: "Massa reaproveitada. Padrão 3000 gramas. Diga a quantidade ou confirme."
- Ao receber valor: "1200 gramas de massa reaproveitada. Confirme." / "Sem massa reaproveitada. Confirme."
- Valor recusado: "Quantidade inválida. Confira o limite na tela."
- Confirmar com campo inválido: "Confira a quantidade."
- Ao confirmar: "Confirmado. 1200 gramas de massa reaproveitada."

Proteções: as falas do app não contêm palavras que confirmam; o microfone ignora o que chega enquanto o app fala e por 0,8 s depois; intervalo mínimo de 0,8 s entre comandos; eco do mesmo valor não repete a fala.
Linha de estado na tela: `🎤 Diga a quantidade em gramas, "sem massa", "padrão" ou "confirmar".` Sem suporte, microfone bloqueado ou falha repetida: aviso na tela e uso normal por toque.
Limite: se uma sessão de porcionamento ainda estiver ouvindo, a tela não abre um segundo microfone e segue só por toque.

## 5. CÓDIGO ALTERADO
- Aviso: CSS `.modulo.modulo-com-aviso`, `.modulo-linha`, `.modulo-reconf`; função `receitaReconfiguravel(id,r)`; `renderReceitasPorcionamento()`.
- Voz: funções `aprovVoz*` e `aprovFalar`; `aprovAbrir()` liga o microfone e anuncia; `ir()` desliga o microfone ao sair da tela; linha `#aprov-voz` no HTML.
- Correção visual: os botões **Sem massa · 0 g** e **Usar padrão** estavam sem estilo (padrão claro do navegador, fora do tema) desde a v26.8; receberam o tema dourado/escuro (`.aprov-quick .btn-sec`).
- Versão em tela e no backup: `Versão 26.8.2 · cache fdo-v26-8-2`, `versao:'26.8.2'`.
- `index.html`: 6.403 linhas.

## 6. VALIDAÇÃO
Executada localmente em 24/11/2026 sobre o código final e depois na CI do GitHub.
- `tools/validate_fdo.py`: estrutura, cache, sintaxe, totais das receitas e marcadores do aviso e da voz — OK.
- 12 suítes Node (v25.1 a v26.8) — OK.
- Chromium: smoke de boot offline, usabilidade v26.6.1 (50), porcionamento v26.6.2 (192), fluxo v26.7 (151), R2 variável v26.8 (22), etiquetas v26.8.1 (18) — OK.
- Aviso: 63 verificações em cinco tamanhos de tela.
- Voz: 54 verificações com microfone e fala simulados — números, comandos, negação, eco das falas, silêncio enquanto o app fala, confirmação gravando o valor na execução, R2 definitiva intacta, microfone desligado ao sair, microfone bloqueado, falha repetida, navegador sem voz e telas pequenas.
Antes do merge, CI da branch: execuções **45441973321 / run 360** (push) e **45442025859 / run 361** (Pull Request), com `validate`, `usabilidade` e `firebase-rules` em sucesso.
Após o merge, CI do `main`: execução **45442313855 / run 362**, em sucesso.
GitHub Pages: execução **45442312783 / run 72**, build e deploy concluídos; o endereço de produção passou a servir `fdo-v26-8-2`.
Não executados: voz em aparelho Android real (reconhecimento, eco e ruído da fábrica) e impressora.

## 7. ARQUIVOS ALTERADOS
Código/PWA: `index.html`, `sw.js`.
Validação: `tools/validate_fdo.py` (versão esperada e marcadores do aviso e da voz).
Este `Resumo_v26.8.2.md` é documentação da entrega.

## 8. CONTINUIDADE / REVERSÃO
Nos aparelhos: recarregar conectado, fechar e abrir novamente e confirmar em Configurações **Versão 26.8.2 · cache fdo-v26-8-2**. Não limpar dados nem desinstalar como primeira medida.
Teste no aparelho: abrir a R2, falar uma quantidade, ouvir a confirmação, dizer "confirmar" e conferir os pesos antes de pesar.
Reversão: novo commit a partir de `backup/pre-v26-8-2-2026-11-24` / v26.8.1, sem force push e com novo identificador de cache.

### Registrado para próximas atualizações
- **Massa laminada reconfigurável nas demais receitas (R1, R3, R4, R5)**: adiada por decisão do Wagner em 24/11/2026. Depende da planilha ou da composição de cada receita; nunca reutilizar a fórmula da R2.
- Nomes de receita aparecem cortados na lista em telas estreitas.

### Revisão da v26.6/v26.7 contra o plano (24/11/2026)
Conforme o plano: partidas de fatias por produto, formas com composição e sobras, fermentação por formas (registros antigos por balde preservados), frio com temperatura opcional, Rules com `partidas` e `formas`, transação com validação de estado.
Não construído ou diferente do plano:
- Sem comparação **previsto × real** da fermentação; só a duração decorrida.
- Sem **umidade** e sem temperatura na entrada do armário; apenas mínima/máxima opcionais na retirada.
- Sem entidade **Fornada** e sem limite de formas por forno; formas assadas juntas compartilham só o identificador da operação.
- Entrada/saída de armário e assamento **exigem internet**; sem conexão a etapa não é registrada.
- Sem comandos de voz em corte, frio, modelagem, fermentação e assamento; confirmações por caixa de seleção e botão; temperatura do descongelamento em janela `prompt`.
- Rules de `partidas` e `formas` autorizam escrita por aparelho autorizado, sem validação por registro.
- Fora do escopo entregue: tempo e temperatura do forno, qualidade, foto, embalagem, perdas.

### Ponto (piloto v26.9)
- Liberado pelo Wagner para avançar em 24/11/2026. Continua na branch `homologacao`, PR #24 em rascunho; produção não alterada.
- Salário ou valor por hora, tipo, jornada por dia e vigência são campos da tela **Gerência → Funcionários**; a área de GPS fica em **Gerência → Área autorizada**. Nenhum valor financeiro está fixo no código.
- O `main` v26.8.2 foi mesclado na `homologacao` (commit `c3d0c33`, versão continua v26.9). A execução **45442448666 / run 14** rodou todos os testes, inclusive os do Ponto, e publicou no site de testes. O PR #24 voltou a ser mesclável sem conflito e segue em rascunho.
- Faltam, nesta ordem: autorizar o primeiro gerente no Firebase de testes, testar com dados fictícios, publicar as Rules do Ponto no Firebase de produção e só então mesclar o PR #24. Mesclar antes das Rules deixaria o Ponto visível na produção sem funcionar.
