# Ponto da Folhados d'Ouro — piloto técnico v26.9

Status: **EM TESTES, NÃO PUBLICADO**. Branch: \`agent/ponto-piloto-v26-9\`.
Base: Produção v26.8.1, \`main\` em 41bb4c3. A Produção continua operacional.

## Objetivo e limites

- \`index.html\` oferece Ponto e Produção; o Ponto abre \`ponto.html\` com JS próprio (\`ponto.js\`).
- O funcionário instala o **FdO Ponto** pelo \`ponto-manifest.json\`, cujo \`id\` e \`start_url\` são diferentes dos de Produção. O manifesto antigo não foi modificado.
- Acesso individual permanece conectado via Firebase Authentication anônima, identidade do aparelho, vínculo autorizado pela gerência.
- Funcionário: entrada, saída, intervalos flexíveis, GPS no momento da marcação, horas confirmadas/provisórias, mês corrente e anterior, confirmação do mês anterior, avisos e solicitação de correção.
- Fora da área / GPS impreciso / offline / relógio divergente: marcação registrada com situação pendente para a gerência. Nunca descartar o horário original.
- Gerência: cadastros mensalista/horista, jornada por dia e histórico de vigência, salário individual versionado em árvore separada, vínculo/revogação de celular, marcações supervisionadas, aprovação/rejeição, correção auditada, folga/feriado/justificativa, avisos e fechamento mensal.
- Relatório de ponto **sem salários** por mês/calendário (1 ao último dia), individual ou equipe; PDF por impressão do navegador (“Salvar como PDF”) e PNG de resumo para baixar/compartilhar. Financeiro é estimativa básica **apenas gerencial**, não folha de pagamento.
- Banco de horas permanece desativado; sua futura ativação, com saldo inicial e transporte condicionado à legislação, requer etapa própria.

## Segurança e preparação antes de qualquer uso

1. **Não mesclar/publicar automaticamente.** Revisar PR, validar CI e preservar a versão anterior.
2. Publicar as **Rules específicas** de \`database.rules.json\` em um ambiente Firebase de testes primeiro; só depois migrar para produção com revisão. As Rules atuais da produção não possuem ainda \`fdo_ponto_*\`.
3. Na primeira execução gerencial, abrir \`ponto.html\` em **aparelho pessoal da gerência**, copiar o UID exibido e ativar manualmente \`fdo_ponto_gerentes/<UID> = {"ativo":true}\` no Firebase (somente pelo Console ou acesso administrativo seguro, nunca pelo navegador de funcionário).
4. Em seguida criar o funcionário, preencher jornada/valor quando houver, abrir Ponto no celular dele, copiar UID, vinculá-lo pela gerência. Testar primeiro com funcionário de demonstração.
5. Não ativar a gerência no Android **compartilhado** da fábrica. O UID gerencial libera a leitura financeira. Revisar as Rules para evitar acesso a dados de colegas e da produção.
6. Configurar centro e raio do GPS na área da gerência, e realizar testes físicos de precisão dentro e fora da fábrica.
7. Não limpar dados de navegador sem verificar a fila de registros offline.
8. Só considerar entrega publicada após avaliação em branch, CI verde, backup Git e autorização expressa.

## Modelo de dados (novas raízes)

\`fdo_ponto_gerentes\` (whitelist gerencial), \`fdo_ponto_vinculos\`, \`fdo_ponto_colaboradores\`, \`fdo_ponto_regras\`, \`fdo_ponto_financeiro\`, \`fdo_ponto_config\`, \`fdo_ponto_marcacoes\`, \`fdo_ponto_aprovacoes\`, \`fdo_ponto_ajustes\`, \`fdo_ponto_solicitacoes\`, \`fdo_ponto_solucoes\`, \`fdo_ponto_ocorrencias\`, \`fdo_ponto_conferencias\`, \`fdo_ponto_fechamentos\`, \`fdo_ponto_avisos_gerais\`, \`fdo_ponto_avisos_individuais\`.

Marcações/decisões/correções/conferências/fechamentos/ocorrências são append-only. A autorização da produção permanece sob \`fdo_dispositivos\`; celulares do Ponto **não recebem** essa autorização.

## Questões ainda não implementadas

- **Terminal Android fixo compartilhado:** requer escolha de autenticação individual segura; neste piloto o registro funcional é pelo próprio celular com GPS. O botão QR da gerência copia links de Entrada/Saída, sem produzir ou ler códigos impressos automaticamente.
- **Notificação push com PWA fechado:** nesta fase os avisos aparecem ao abrir a aplicação.
- **Banco de horas** e compensação: indisponíveis nesta fase.
- **Registro eletrônico de ponto oficial (REP-P):** não é alegado. Este piloto é controle interno e depende de verificação jurídica antes de uso como registrador legal.
- **Fechamento financeiro definitivo:** adicionais, pagamento noturno, faltas, descontos, feriados remunerados e vigências salariais no meio do mês não estão apurados automaticamente; cálculo financeiro exibido é referência gerencial.
- **GPS:** prova aproximada, não verificação antifraude definitiva. Browser pode sofrer alteração de localização e horário; exceções devem ser conferidas.
- **Offline:** utiliza \`localStorage\` com fila local e envio quando reconecta. Marcações locais não sincronizadas dependem da preservação dos dados do navegador.
- **Controle de ausência:** dias sem marcação de jornada cadastrada aparecem para conferência, não são automaticamente lançados como falta. Folgas e feriados precisam de lançamento pela gerência.

## Como validar

- \`python3 tools/validate_fdo.py\`: estrutura, produção, receitas e cache.
- \`node tools/test_ponto_piloto.js\`: sintaxe, HTML/JS, jornada fragmentada, exceções, correções, ausências, manifesto separado.
- \`npx firebase emulators:exec --only database --project demo-fdo-rules "node tools/test_database_rules_v26_6.js && node tools/test_fluxo_emulator_v26_7.js && node tools/test_ponto_rules.js"\`: banco, finanças, privacidade, gravação append-only.
- \`python tools/smoke_ponto_v26_9.py\`: Chromium com Firebase simulado; captura telas sem dados reais.
- Os testes anteriores v25–v26.8.1 permanecem no workflow.

## Publicação / retorno

Publicar apenas depois de validar em ambiente de teste e confirmar Firebase Rules. O Service Worker do piloto usa \`fdo-v26-9\`, adicionando ponto HTML/JS e o manifest Ponto ao pré-cache. O manifesto de Produção mantém \`id\`, \`scope\`, \`start_url\` e ícones anteriores.

Reversão: restaurar o commit funcional anterior pela história GitHub ou pela branch \`backup/pre-v26-8-1-2026-11-03\`, sem force push. Se a versão piloto tiver sido ativada no banco, primeiro pausar novos registros e preservar/exportar os dados novos antes de reverter regras.
