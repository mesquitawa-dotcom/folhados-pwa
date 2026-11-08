# Resumo v26.9 — piloto em homologação

Atualizado em 08/11/2026. Este resumo complementa Resumo_v26.8.1.md e PONTO_PILOTO_v26.9.md. O código vigente do GitHub continua sendo a fonte de verdade.

## Ambientes

- Produção: main, v26.8.1, commit 41bb4c3bae958c77879069f49ecb008d8af57317. Não alterada nesta configuração.
- Homologação: branch homologacao, piloto Ponto v26.9, https://fdo-homologacao-mesquita.web.app/.
- PR de promoção #24 permanece em rascunho; nenhuma rotina executa merge.
- Backup: backup/pre-homologacao-2026-11-08.

## Última mudança

Firebase fdo-homologacao-mesquita configurado no plano Spark: login anônimo, Realtime Database us-central1 separado e Hosting. Primeiro deploy de Hosting e regras confirmado na execução 42449512010, tentativa 2. Nenhum cadastro da fábrica foi copiado.

GitHub Actions usa identidade temporária OIDC, restrita ao repositório, proprietário, branch homologacao e workflow de publicação. Conta exclusiva com administração de Hosting/Realtime Database e leitura de Service Usage somente no projeto de testes. Não foi criada chave privada permanente. Variables do projeto e app Web cadastradas.

O workflow exige aprovação de toda a suíte automatizada antes de publicar. Nove verificações adicionais bloqueiam destino, banco, app, branch ou repositório incompatíveis. A suíte de receitas, regressões, interface, piloto e regras passou no primeiro deploy.

A conferência real identificou App Check sendo iniciado sem chave. Correção no empacotador evita iniciar reCAPTCHA sem a chave opcional e preserva sua ativação quando configurada; testes executam os inicializadores de Produção e Ponto. Cache exclusivo recebe hash do conteúdo gerado. Código-fonte funcional, receitas, pesos, tempos e dados de produção não foram alterados.

## Próximos passos

1. Testar o piloto exclusivamente com dados fictícios.
2. Autorizar o primeiro gerente de testes em fdo_ponto_gerentes conforme PONTO_PILOTO_v26.9.md; esta autorização não foi feita automaticamente.
3. Autorizar aparelhos de Produção no banco de testes quando necessário para testar sincronização. Login anônimo não substitui essas autorizações.
4. Somente após aprovação expressa de Wagner revisar e promover PR #24.

Configuração e manutenção detalhadas em HOMOLOGACAO_E_PRODUCAO.md. Sem promoção automática para produção.
