# Folhados d'Ouro — Resumo v26.5

Data: 29/08/2026
Versão: v26.5
Tema: Firebase App Check com reCAPTCHA Enterprise

## Objetivo

Adicionar Firebase App Check ao PWA para aumentar a proteção contra clientes/copias não legítimas fazendo chamadas ao Firebase, sem alterar receitas, pesos, fermentos, tempos, snapshots históricos nem o fluxo operacional.

Nesta versão, o App Check é integrado ao cliente, mas o enforcement no Realtime Database permanece DESATIVADO até todos os aparelhos estarem atualizados e as métricas serem conferidas.

## App Check

- App Web `Fdo PWA` registrado no Firebase App Check.
- Provedor: reCAPTCHA Enterprise, chave Web baseada em pontuação e sem desafio visível.
- Domínio autorizado: `mesquitawa-dotcom.github.io`.
- TTL configurado no Firebase: 1 hora.
- SDK compat 10.13.2 do App Check é servido localmente pelo PWA e incluído no pré-cache.
- O App Check é inicializado antes do Realtime Database e Authentication.
- Renovação automática de token ativada.
- Configurações mostra diagnóstico do aparelho:
  - `App Check: ✓ token válido · reCAPTCHA Enterprise` quando o token é obtido corretamente;
  - aviso simples quando o token não pode ser obtido;
  - estado offline não bloqueia o boot.

A site key do reCAPTCHA é pública por definição e pode existir no JavaScript do cliente. Ela não deve ser tratada como segredo.

## Enforcement

NÃO ativado na v26.5.

Enquanto o enforcement estiver desativado:
- aparelhos v26.5 passam a enviar tokens App Check;
- aparelhos antigos continuam funcionando;
- nenhuma requisição ao Realtime Database é rejeitada apenas por falta de token App Check.

Ordem segura para ativação futura:
1. publicar a v26.5;
2. atualizar todos os aparelhos de produção;
3. em cada aparelho, conferir `Versão 26.5 · cache fdo-v26-5` e `App Check: ✓ token válido`;
4. publicar no Firebase real as Rules v26.4 já testadas, caso ainda estejam pendentes;
5. observar as métricas de App Check no Firebase;
6. somente depois ativar enforcement do App Check para Realtime Database.

## GitHub

A branch `main` está protegida pelo ruleset `Proteção da main - Folhados PWA`:
- Pull Request obrigatório;
- 0 aprovações humanas obrigatórias;
- somente merge por Squash;
- checks obrigatórios `validate` e `firebase-rules`;
- exclusão e force push bloqueados;
- Repository admin possui bypass somente via Pull Request.

## Arquitetura preservada

- `index.html` monolítico;
- HTML/CSS/JavaScript vanilla;
- sem framework e sem build de produção;
- Firebase SDK compat 10.13.2 local;
- localStorage offline-first;
- Service Worker com cache versionado;
- autorização do aparelho e login do operador continuam separados.

O App Check acrescenta uma camada contra abuso de requisições, mas não torna o JavaScript público secreto e não substitui a autorização do aparelho no Realtime Database.

## Cache

- anterior: `fdo-v26-4`
- atual: `fdo-v26-5`

## Receitas

Nenhuma receita foi alterada.

Totais invariantes validados:
- R1: 15.464 g
- R2: 15.690 g
- R3: 15.544 g
- R4: 15.564 g
- R5: 15.714 g
- Receita Teste de referência v25.3: 15.448 g

## Testes

O CI permanente da v26.5 inclui:
- validação estrutural, sintaxe JavaScript, handlers, IDs, manifest e assets;
- totais de receitas;
- regressões v25.1 até v26.5;
- teste específico do App Check;
- verificação da ordem App → App Check → Auth → Database;
- verificação do SDK App Check local no Service Worker;
- smoke de boot offline em Chrome;
- job separado de Firebase Rules no Realtime Database Emulator Suite.

## Git / rollback

- Base anterior: v26.4, commit `2a299a1ee20fd7d227de38ad1e54dbed56732c6a`.
- Backup pré-v26.5: `backup/pre-v26-5-2026-08-29`.
- Branch de desenvolvimento: `agent/app-check-v26-5`.

## Próximos passos

- publicar v26.5 somente após PR e checks verdes;
- atualizar o aparelho disponível e confirmar token App Check;
- na segunda-feira, atualizar e conferir o segundo aparelho;
- manter enforcement App Check desligado até validação de todos os aparelhos e métricas;
- publicar as Firebase Rules v26.4 no Realtime Database real somente na ordem planejada;
- depois revisar PINs administrativos/operadores e estratégia de proteção da propriedade intelectual do código/receitas.
