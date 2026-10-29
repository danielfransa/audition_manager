# 0025 — Documentação pública bilíngue

Data: 29 de outubro de 2026

## Contexto

O README anterior misturava apresentação pública, instalação, uso e detalhes de
desenvolvimento. Com a interface disponível em Português e Inglês, visitantes do
repositório também precisam encontrar instruções completas no idioma escolhido.

## Decisão

- Manter o `README.md` raiz curto e bilíngue, apresentando o produto, o status e
  links diretos para cada idioma.
- Organizar visão completa, instalação e uso em `docs/pt-BR/` e `docs/en/`.
- Manter `docs/installation.md` como seletor de idioma para preservar links já
  publicados sem duplicar instruções.
- Adiar a tradução dos documentos técnicos e históricos para o próximo
  incremento, mantendo essa limitação explícita no índice em Inglês.

## Consequências

A página inicial fica adequada ao GitHub e novos usuários encontram instruções
para Debian, Fedora, Arch, Windows e WSL sem atravessar detalhes internos. Cada
instrução de instalação passa a ter uma fonte por idioma, reduzindo divergências.
