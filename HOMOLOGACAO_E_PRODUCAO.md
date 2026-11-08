# Folhados d'Ouro — Homologação e Produção (configuração permanente)

**Situação inicial (08/11/2026):** Produção continua na versão v26.8.1, publicada em GitHub Pages a partir de **main**. O piloto v26.9 do Ponto está na branch **homologacao**; nenhuma regra ou cadastro do banco real foi alterado.

## 1. Fluxo das versões

| Ambiente | Endereço | Branch | Firebase |
|---|---|---|---|
| **PRODUÇÃO** | https://mesquitawa-dotcom.github.io/folhados-pwa/ | **main** | Projeto atual, com dados reais |
| **HOMOLOGAÇÃO** | https://ID_DO_PROJETO.web.app/ | **homologacao** | **Outro projeto Firebase, sem dados reais** |

O endereço de homologação só existirá após a primeira configuração. Não inventar o ID: usar o criado pelo Firebase.

1. Uma nova versão é colocada em **homologacao**.
2. GitHub Actions executa automaticamente os testes do aplicativo, receitas, interface e segurança das Rules no emulador.
3. **Somente após todos passarem**, publica o aplicativo de testes e as Rules de testes no Firebase de homologação.
4. Wagner testa no celular com registros fictícios e aprova ou solicita correções.
5. Após aprovação expressa, abrir/revisar Pull Request de **homologacao para main** e mesclar. O GitHub Pages existente publica automaticamente a **main** na produção.
6. Se falhar, reverter por novo commit do Git, preservando todos os dados reais.

**Ninguém promove automaticamente para produção sem a aprovação de Wagner.**

## 2. Configuração necessária UMA VEZ — Firebase

Abrir https://console.firebase.google.com/ e:
1. Criar projeto NOVO, sugestão de nome: Folhados d'Ouro — Homologação. NÃO escolher o projeto de produção **producaofolhadosdouro-b6fb5**.
2. Em Build → Realtime Database, criar novo banco (sem copiar informações reais).
3. Em Authentication → Sign-in method, habilitar **Anonymous**.
4. Em Hosting, iniciar o serviço (a URL terá o formato https://ID_DO_PROJETO.web.app).
5. Em Project settings → General → Your apps, registrar um novo app **Web**. Copiar a configuração completa **firebaseConfig** do projeto NOVO: apiKey, authDomain, databaseURL, projectId, storageBucket, messagingSenderId e appId.
6. **App Check:** inicialmente manter o enforcement desativado. Se desejar, configurar uma chave reCAPTCHA Enterprise própria da homologação; nunca aproveitar a chave da produção.
7. Criar uma **conta de serviço do projeto NOVO**, com permissões limitadas ao deploy do Hosting e das Database Rules. Baixar a credencial JSON, mantê-la secreta, nunca colocar no Git e nunca compartilhá-la pelo chat.

O armazenamento local também fica separado, pois o site de homologação usa outro domínio.

## 3. Configuração necessária UMA VEZ — GitHub

Abrir https://github.com/mesquitawa-dotcom/folhados-pwa/settings/secrets/actions

Em **Variables → New repository variable**:
- **FDO_HOMOLOG_FIREBASE_PROJECT_ID** = ID exato do NOVO projeto Firebase.
- **FDO_HOMOLOG_FIREBASE_WEB_CONFIG** = JSON completo do firebaseConfig do NOVO app Web.
- **FDO_HOMOLOG_APP_CHECK_KEY** = opcional; chave pública do App Check NOVO.

Em **Secrets → New repository secret**:
- **FDO_HOMOLOG_FIREBASE_SERVICE_ACCOUNT** = conteúdo completo da credencial JSON da conta de serviço do projeto NOVO.

O workflow verifica que a credencial de serviço, a configuração Web e o projectId são do mesmo projeto e **recusa o ID da produção**. A credencial fica apenas na execução do GitHub Actions e não é publicada no PWA.

## 4. Como iniciar o primeiro deploy

Depois de configurar as Variables e o Secret, abrir a última execução de:
https://github.com/mesquitawa-dotcom/folhados-pwa/actions/workflows/deploy-homologacao.yml

Reexecutar os jobs. O workflow também dispara automaticamente sempre que houver nova atualização na branch **homologacao**. Se o botão Run workflow não aparecer porque a rotina ainda não existe em main, usar **Re-run jobs** na execução já criada.

Se faltarem dados de configuração, os testes podem passar, mas a publicação ficará bloqueada — isso é proposital.

Após publicação:
- Abrir o endereço informado no GitHub Actions e verificar faixa fixa **HOMOLOGAÇÃO · USE SOMENTE DADOS FICTÍCIOS**.
- Confirmar que o Firebase é o projeto NOVO.
- Instalar o PWA de teste pelo domínio novo, sem desinstalar a produção.
- Testar ponto normal, fora da fábrica, pendências, relatórios, PDF e PNG usando dados fictícios.
- Testar Produção com operações fictícias, conferindo que receitas e telas estão preservadas.
- A primeira autorização gerencial do Ponto ainda exige cadastrar manualmente o UID no caminho **fdo_ponto_gerentes** do Firebase NOVO, conforme PONTO_PILOTO_v26.9.md.

## 5. Proposta automática de publicação (sem merge automático)

Quando a publicação da HOMOLOGAÇÃO terminar com sucesso, o GitHub Actions **tentará abrir um Pull Request em RASCUNHO** de homologacao → main, caso ainda não exista um aberto. O PR fica pronto para sua conferência, **mas nenhuma automação o aprova ou mescla**.

Para ativar esse conforto opcional uma única vez, abrir https://github.com/mesquitawa-dotcom/folhados-pwa/settings/actions e, em **Actions → General → Workflow permissions**, habilitar **Allow GitHub Actions to create and approve pull requests**. O nome da opção é do GitHub; nosso workflow está programado apenas para criar PR em rascunho, nunca para aprovar ou executar merge. Se não habilitar, a homologação ainda poderá ser publicada normalmente e o PR será aberto manualmente por um administrador.

O PR #23 é o rascunho original do piloto Ponto, anterior à configuração permanente da homologação. **Não o mesclar isoladamente.** Quando o Firebase de testes estiver ativado, a proposta correta será homologacao → main, após teste real.

## 6. Proteção recomendada no GitHub

Em https://github.com/mesquitawa-dotcom/folhados-pwa/settings/rules ou Settings → Branches:
- Proteger **main**: exigir Pull Request e checks aprovados; impedir force push/exclusão; não exigir um segundo revisor quando só houver um responsável.
- Restringir quem altera a branch **homologacao**.
- Nunca usar credenciais ou dados do Firebase da fábrica na homologação.

Essas configurações de proteção exigem ação no GitHub; **não foram realizadas automaticamente**.

## 7. Estado da implementação e retorno seguro

Automatizado: suíte existente de testes é reutilizada pela rotina de deploy, build com Firebase de testes, alerta visual, cache de homologação, deploy do Hosting e das Rules no projeto NOVO. A publicação de produção após merge segue GitHub Pages como atualmente.

Depende de ação uma única vez: criar/configurar Firebase novo e cadastrar Variables/Secret. Depende de aprovação a cada versão: mesclar Pull Request para main.

Backup do main preservado em **backup/pre-homologacao-2026-11-08**, commit **41bb4c3bae958c77879069f49ecb008d8af57317**.

Arquivos novos: **firebase.homologacao.json**, **tools/build_homologacao.py**, **tools/test_build_homologacao.py**, **tools/preparar_credencial_homologacao.py**, **.github/workflows/deploy-homologacao.yml**. A validação permanente foi adaptada para poder ser reutilizada, sem retirar testes de receitas ou alterar módulos já funcionais.

A automação **não modifica receitas, pesos, tempos, PINs, histórico, parâmetros ou o Firebase de produção**.
