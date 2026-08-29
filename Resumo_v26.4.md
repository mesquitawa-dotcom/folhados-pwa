# Folhados d'Ouro — Resumo v26.4

Data: 29/08/2026
Versão: v26.4
Tema: Segurança Firebase e históricos append-only

## Objetivo

Endurecer a segurança do Firebase Realtime Database sem alterar receitas, pesos, fermentos, tempos, snapshots históricos nem o fluxo operacional do chão de fábrica.

## Principais mudanças

- `fdo_v25` deixa de ter gravação ampla e passa a usar allowlist explícita dos caminhos realmente utilizados pelo PWA.
- Auditoria de receitas (`fdo_v25/receitas_auditoria`) torna-se append-only no servidor.
- Movimentos de estoque (`fdo_v25/estoque/movimentos`) tornam-se append-only no servidor.
- Logs de acesso (`fdo_acessos`) tornam-se append-only e continuam sem leitura pelo cliente.
- O cliente reconhece retry idempotente de registros históricos por leitura/comparação, sem regravar registros existentes.
- Se o mesmo ID histórico existir com conteúdo diferente, o registro da nuvem é preservado e o PWA sinaliza conflito em vez de sobrescrever.
- O cache do Service Worker passa para `fdo-v26-4`.
- O CI permanente passa a testar a v26.4 e as Firebase Rules no Realtime Database Emulator Suite.

## Compatibilidade preservada

Continuam graváveis para aparelho Firebase autorizado:

- baldes canônicos e ponte legada;
- laminações;
- metadados e sequências transacionais;
- operadores;
- lotes atuais de farinha;
- receitas definitivas versionáveis;
- observações de receitas;
- configurações e contagens de estoque.

Caminhos canônicos não previstos em `fdo_v25` ficam fechados por padrão.

## Receitas

Nenhuma receita foi alterada.

Totais validados:

- R1: 15.464 g
- R2: 15.690 g
- R3: 15.544 g
- R4: 15.564 g
- R5: 15.714 g
- Receita Teste de referência v25.3: 15.448 g

## Validação

Passaram no CI final da branch limpa:

- validação geral do PWA e sintaxe JavaScript;
- handlers, IDs, manifest, assets e cache;
- regressões v25.1 até v26.4;
- smoke de boot offline em Chrome;
- Realtime Database Emulator Suite;
- bloqueio de acesso anônimo;
- bloqueio de aparelho não autorizado;
- criação permitida das estruturas operacionais compatíveis;
- alteração/exclusão negadas para auditoria, movimentos de estoque e logs de acesso;
- retry idempotente reconhecido sem sobrescrita;
- mesmo ID com conteúdo divergente detectado como conflito.

## Git

- Base anterior preservada: `backup/pre-v26-4-2026-08-29`
- Branch de desenvolvimento: `agent/seguranca-firebase-v26-4`
- Commit funcional v26.4 materializado após testes: `414418e5e71c4d1269512a1873cd87d1ac9c2192`
- Após esse commit, a branch recebeu apenas limpeza de ferramentas temporárias e atualização do CI permanente.

## Publicação segura

A implantação das Rules mais estritas deve respeitar esta ordem:

1. publicar/atualizar o PWA v26.4;
2. confirmar que os aparelhos de produção receberam a v26.4;
3. somente então publicar `database.rules.json` no Firebase Realtime Database.

Não publicar as Rules v26.4 antes de atualizar os aparelhos.

## Próximos passos

- proteger a branch `main` no GitHub;
- decidir estratégia de repositório público x privado considerando GitHub Pages;
- revisar PINs administrativos e sua rotação;
- avaliar Firebase App Check como camada futura, após validar impacto operacional nos aparelhos do chão de fábrica.
