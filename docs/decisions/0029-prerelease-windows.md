# 0029 — Primeira pré-release Windows

Data: 29 de outubro de 2026

## Contexto

O usuário validou em Windows real o pacote portátil gerado na revisão `eeed30f`,
incluindo interface responsiva, reprodução, runtime NAM oculto e samples. Os
artefatos comuns do Actions expiram após 14 dias.

## Decisão

- Integrar `develop` na `main` após registrar o aceite.
- Criar a tag `v0.1.0-alpha` e tratá-la como pré-release, não como versão estável.
- Em tags `v*`, reconstruir e testar o ZIP em `windows-2022` e publicá-lo em
  GitHub Releases com notas bilíngues.
- Manter instalador e assinatura fora desta etapa; o pacote portátil facilita
  identificar problemas antes de adicionar outra camada de distribuição.

## Consequências

O download deixa de depender de artefatos temporários e passa a ter uma versão
identificável. A tag reconstrói o pacote a partir da fonte promovida, portanto a
release ainda depende do workflow concluir com sucesso após o push da tag.
