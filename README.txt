# Folhados d'Ouro — Deploy

## O que está nesta pasta
- index.html — app completo
- manifest.json — config PWA
- sw.js — cache offline

## Como hospedar (GitHub Pages — grátis, 5 min)

1. Crie conta em github.com
2. Clique em "New repository" → nome: folhados-pwa → Public
3. Arraste os 3 arquivos para dentro
4. Settings → Pages → Branch: main → Save
5. Seu app fica em: https://SEU-USUARIO.github.io/folhados-pwa

## Instalar no Android
1. Abra o link no Chrome do Android
2. Menu (3 pontos) → "Adicionar à tela inicial"
3. Pronto — fica como ícone de app

## Chave API Gemini
1. Acesse aistudio.google.com
2. Get API key → Create API key
3. Copie e cole na tela de Config do app
4. Plano gratuito: 60 req/min — suficiente para produção

## Alterar receita
No index.html, localize o array RECEITA (linha ~60)
Edite quantidades substituindo "— kg" pelos valores reais.

Exemplo:
  {id:3, cat:'AÇÚCAR', nome:'Açúcar refinado', qty:'0,480 kg', ...}
