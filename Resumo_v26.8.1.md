# Folhados d'Ouro — Resumo v26.8.1

## 1. IDENTIFICAÇÃO
- Entrega: **v26.8.1 — etiquetas com reaproveitamento e líquidos em destaque**.
- Repositório: `mesquitawa-dotcom/folhados-pwa`.
- Base anterior: v26.8, `3d9ec1f69f77d7e184331bbe6f66833c8d7905fa`.
- Código publicado: `95ee4d943a9dbbba753e9576d772c8bdcf81b3d4`.
- Cache: `fdo-v26-8-1` (anterior `fdo-v26-8`).
- Branch de desenvolvimento: `agent/etiquetas-v26-8-1`.
- Pull Request de código: **#21**, revisado pelo Wagner e mesclado em 03/11/2026.
- Restauração: `backup/pre-v26-8-1-2026-11-03`.
- Fonte de verdade: código vigente no `main`.

## 2. PRESERVADO
Nenhuma receita, peso, fermento, tempo, regra de produção, histórico, Firebase/Rules, manifest, ícone, vendor ou impressão Bluetooth foi alterado.
O tamanho físico das etiquetas permanece **60×50 mm**.
Totais das receitas definitivas permanecem: R1 **15.464 g**, R2 **15.690 g**, R3 **15.544 g**, R4 **15.564 g**, R5 **15.714 g**.
Toda a lógica da v26.8 de reaproveitamento variável da R2 e snapshots por balde foi preservada.

## 3. ETIQUETA DAS MASSAS
Para execuções com reaproveitamento conhecido, a primeira linha passa a ser dividida em duas metades:
- esquerda: receita curta, por exemplo **Receita 2**;
- direita: quantidade real de massa reaproveitada usada naquela execução, por exemplo **650 g**.
Uma linha vertical separa os dois campos.
A segunda linha continua mostrando data, temperatura e horas de fermentação.
A informação vem do snapshot/evento do balde, nunca do nome antigo da receita.
Para R2 antiga sem metadado v26.8, o sistema pode recuperar os **3.000 g** do campo Massa laminada do snapshot. Outras receitas sem metadado não recebem valor inventado.

## 4. ETIQUETA DO BALDE
O corpo principal foi reorganizado para leitura rápida no chão de fábrica.
Três informações ganham fonte maior, espaçamento vertical e peso alinhado à direita:
- **Água/gelo**
- **Leite em pó**
- **Massa laminada**
Temperatura/horas e eventual Massa sem laminar permanecem secundárias no rodapé.
Quando a execução da R2 tem reaproveitamento variável, o cabeçalho usa **Receita 2** e deixa de exibir o nome antigo **Receita 2 - MASSA 3 KG**, evitando conflito com a quantidade realmente usada.

## 5. EXEMPLO VALIDADO
Cenário usado na validação visual: R2 com **650 g** de massa reaproveitada.
Etiqueta das massas: **Receita 2 | 650 g**.
Etiqueta do balde: Água/gelo **4,060 kg**, Leite em pó **194 g**, Massa laminada **650 g**, com **20°C / 14 horas** preservados como informação secundária.

## 6. VALIDAÇÃO
Antes do merge, CI da branch: execução **41694249514 / run 286**, com `validate`, `usabilidade` e `firebase-rules` em sucesso.
Foram adicionadas **18 verificações específicas de etiquetas** em Chromium, incluindo conteúdo, posicionamento, tamanho mínimo das fontes e ausência de valor inventado em outras receitas.
As imagens reais do canvas foram geradas pelo teste e revisadas visualmente.
Após o merge, CI do `main`: execução **41695082559 / run 289**, com os três jobs em sucesso.
GitHub Pages: execução **41695079772 / run 70**, com build e deploy concluídos com sucesso.
Regressões anteriores v25–v26.8, boot offline, estoque, receitas, fluxo e Firebase Emulator permaneceram verdes.

## 7. ARQUIVOS ALTERADOS
Código/PWA: `index.html`, `sw.js`.
Validação: `tools/validate_fdo.py`, `tools/test_etiquetas_v26_8_1.py`, `.github/workflows/validate-fdo.yml`.
Este `Resumo_v26.8.1.md` é documentação posterior ao código publicado.

## 8. CONTINUIDADE / REVERSÃO
Nos aparelhos: recarregar conectado, fechar e abrir novamente e confirmar em Configurações **Versão 26.8.1 · cache fdo-v26-8-1**.
Não limpar dados nem desinstalar como primeira medida.
Teste físico recomendado: imprimir uma etiqueta das massas e uma do balde usando uma R2 com reaproveitamento conhecido e conferir a leitura no ambiente real.
Reversão: novo commit a partir de `backup/pre-v26-8-1-2026-11-03`, sem force push e sempre com novo identificador de cache se houver publicação reversa.
