# Folhados d'Ouro — Resumo v26.6

Data: 29/08/2026  
Versão: **v26.6**  
Tema: **Espinha dorsal pós-laminação — fatias, frio e modelagem**

## Objetivo

Fazer o PWA acompanhar o objeto físico depois da laminação, sem alterar o fluxo anterior: lote de laminação → partidas de fatias → frio/descongelamento → formas.

## Implementado

- Ao criar uma laminação, abre imediatamente o registro de corte/fatias; também é possível registrar depois pelo card da laminação.
- Produtos: Croissant 11,5 cm (sug. 36), Croissant 10 cm (sug. 40), Croissant 9 cm (sug. 44), Mini, Pain au Chocolat e New York Roll.
- Sugestões nunca são travas: quantidade real é editável.
- Capacidades sugeridas por forma: croissants 16, mini 35, Pain au Chocolat 16, Rolls 14; sempre editáveis.
- Uma laminação pode originar várias partidas/produtos.
- Fluxo frio registra freezer rápido, freezer conservador (-15°C) e início do descongelamento em geladeira com temperatura opcional.
- Rota urgente permite modelagem direta sem fabricar eventos de frio.
- Formas preservam composição de uma ou mais partidas compatíveis e podem completar sobras automaticamente.
- Numeração visual de partidas e formas reinicia por dia; IDs internos continuam únicos.
- Etiqueta própria de fatias usa a infraestrutura Bluetooth existente e pode ser reimpressa.
- `fdo_partidas` e `fdo_formas` entram no backup e na sincronização granular.
- Firebase Rules autorizam as duas coleções somente para aparelhos autorizados; históricos append-only anteriores permanecem preservados.
- Permissão `modelagem` é criada para operadores existentes herdando o valor vigente de `laminacao` quando ainda não houver configuração explícita.

## Preservado

- Todas as funções anteriores à laminação.
- Módulo antigo chamado Fermentação (`lote.etapas.fermentacao`, mínima/máxima do balde) permanece intacto nesta versão; sua nomenclatura será tratada separadamente quando entrar Fermentação Final.
- Receitas, pesos, fermentos, tempos e snapshots históricos sem alteração.
- Arquitetura HTML/CSS/JS vanilla, offline-first, App Check v26.5 e trilhas append-only v26.4.

## Cache

- anterior: `fdo-v26-5`
- atual: `fdo-v26-6`

## Próxima versão planejada

**v26.7 — Fermentação Final + Fornadas**: formas → armário (temperatura/umidade) → previsto × real → fornada de até 5 formas → saída do forno.

## Publicação externa ainda necessária

As `database.rules.json` versionadas e testadas no repositório precisam estar efetivamente publicadas no Realtime Database real antes de depender das novas coleções em produção. App Check enforcement continua uma decisão separada, somente após validar todos os aparelhos.
