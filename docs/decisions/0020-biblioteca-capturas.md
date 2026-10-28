# 0020 — Biblioteca de capturas NAM

## Contexto

Após validar a cadeia `DI → NAM → IR`, a lista simples de arquivos não permitia
organizar capturas, reencontrar a seleção anterior ou removê-la claramente.

## Decisão

A migração SQLite versão 2 cria uma tabela própria para capturas. Ela armazena
caminho, versão, arquitetura, taxa, quantidade de submodelos, favorito,
avaliação e notas. Um novo scan atualiza os dados técnicos sem apagar os dados
do usuário.

A interface mantém busca e filtros próprios para capturas, estrelas clicáveis,
favorito e editor de notas. `Ctrl+←/→` navega pela lista e **Sem captura** remove
o modelo da cadeia. A última pasta e a última captura são gravadas nas
preferências e restauradas quando ainda existem.

IRs e capturas usam tabelas e controles separados porque seus metadados e seus
ciclos de exportação serão diferentes nas próximas etapas.
