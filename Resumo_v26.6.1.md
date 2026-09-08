# Folhados d'Ouro — Resumo v26.6.1

Data: 08/09/2026
Versão: **v26.6.1 — revisão de usabilidade**
Base: v26.6, `04e3a34f6aba6436859a51b9c2c0e6216942492d`
Branch de trabalho: `agent/usabilidade-v26-6-1`
Restauração: `backup/pre-v26-6-1-usabilidade-2026-09-08`

## Objetivo

Simplificar a operação sem iniciar a v26.7: porcionamento mais rápido, primeira laminação separada do corte, próxima ação do frio explícita e retorno seguro. O código vigente no GitHub prevalece sobre este resumo. Confirmar merge e implantação antes de considerar esta revisão publicada.

## Implementado

- Voltar visível nas telas operacionais; retorno do navegador/Android direcionado ao mesmo controle. Retorno não desfaz registros e é bloqueado durante gravação/impressão. Telas de autorização/login não são contornadas.
- Lotes das farinhas: cabeçalho compacto, botão “MESMOS LOTES” no alto, números visíveis e edição recolhida; texto de confirmação acompanha alterações.
- Finalização dos secos: operador comum gera um balde. Múltiplos exigem o PIN administrativo já existente das Configurações, com autorização temporária por operador/sessão. Não foi criado um novo cargo nem alterado PIN.
- Cada balde tem ID, número, snapshot e baixa de estoque próprios. Diário local de geração permite retomar falha parcial sem repetir baldes/baixas. Tempos individuais não são inventados para uma preparação conjunta.
- Etiquetas: escolha de 1 a 8; contagem independente dos baldes; seleção de todos ou de um balde e prévia identificada. Reimprimir não grava produção.
- Laminação tem duas entradas. Primeira etapa: duas massas selecionadas geram um registro de massa com manteiga; não abre mais o corte automaticamente. Segunda etapa: escolha entre massas aguardando corte, inclusive de dias anteriores.
- Laminações antigas mantêm sua quantidade/composição e são identificadas como legadas; não são reinterpretadas como massas físicas de uma unidade.
- Corte pode ter vários produtos e registros parciais. Só a confirmação explícita de que toda a massa foi cortada tira o item das pendências. Reabertura administrativa preserva fatias/formas e registra evento.
- Fatias: quatro faixas de identificação em uma etiqueta grande; de 1 a 8 etiquetas grandes = 4 a 32 identificações. Não se repete a quantidade total como se fosse quantidade por embalagem.
- Frio e Modelagem: abas Frio / Modelagem / Formas, próxima ação principal por estado e detalhes recolhidos. Cancelar a temperatura não inicia descongelamento. Confirmar sem medição conserva temperatura ausente.
- Modelagem exige conferência. Complemento de forma usa apenas fatias já em modelagem, com confirmação das origens; nunca usa automaticamente saldo ainda no freezer ou sem conferência.

## Dados e compatibilidade

Coleções existentes `fdo_lotes`, `fdo_laminacoes`, `fdo_partidas` e `fdo_formas` preservadas. Nenhuma conversão destrutiva nem descarte automático de histórico.

Campos opcionais novos: `producaoConjunta` nos baldes de um grupo; `modeloFisico`, `massasComManteiga`, `etapas.corte` e `corteEventos` nas novas laminações/conclusões. Legados não recebem estados de conclusão por suposição.

Diário local `fdo_baldes_pendentes_v2661` incluído no backup. Contadores locais por dia/tipo evitam números repetidos ao registrar vários produtos offline no mesmo aparelho. Isso não elimina a possibilidade já existente de números visuais iguais entre aparelhos offline diferentes; os IDs internos continuam distintos.

Firebase Rules, App Check, autenticação, dependências de produção, manifest, ícones e SDKs locais não foram alterados. Permissões administrativas do aplicativo não equivalem a uma nova segurança de servidor. A pendência anterior de confirmar as Rules v26.6 no Firebase real continua separada.

## Preservado

Receitas, pesos, fermentos, tempos, sugestões de produto/formas e parâmetros de frio. Totais: R1 15.464 g; R2 15.690 g; R3 15.544 g; R4 15.564 g; R5 15.714 g. Receita Teste de referência: 15.448 g.

Módulo antigo Fermentação intacto. Fermentação Final e Forno continuam fora desta alteração.

## Cache

Anterior: `fdo-v26-6`. Novo: `fdo-v26-6-1`.

## Validação e pendências

Validação estrutural/JS/handlers/IDs/PWA e suítes de regressão mantidas. Nova suíte `tools/test_usabilidade_v26_6_1.py` cobre fluxos, falhas simuladas, dados sintéticos, duplicações, impressão e retorno. O workflow executa a suíte em navegador com origem local real, compara receitas/produtos com a base e guarda evidências. Os resultados exatos devem ser conferidos no PR/Actions correspondente.

Não foi feita validação presencial no Android de produção, reconhecimento em ambiente ruidoso ou impressão Bluetooth na MDK-022 física. Antes de adoção operacional, conferir as quatro faixas impressas e executar uma passagem controlada com dados de teste, sem movimentar estoque real por engano. Não limpar os dados do Android para atualizar.

## Reversão

Usar revert do commit/PR da revisão, preservando o histórico Git. Se já houver aparelhos com a revisão instalada, publicar a reversão com uma nova versão de cache; não apenas copiar o `sw.js` antigo. Não apagar dados novos nem usar force push.

## Próximo passo

Conferência operacional da revisão de usabilidade. Não iniciar v26.7 automaticamente. Substituir o resumo antigo nas Fontes do Projeto por este após confirmar a publicação correspondente.
