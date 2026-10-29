# 0022 — Exportação conjunta de capturas e IRs favoritos

## Contexto

A exportação existente copiava somente IRs. Misturar arquivos `.nam` e `.wav`
na mesma pasta dificultaria identificar o que deve ser carregado em cada seção
de uma pedaleira ou aplicativo.

## Decisão

O comando **Exportar favoritos…** reúne os favoritos das duas bibliotecas e cria:

```text
Nome escolhido/
├── Capturas/
└── IRs/
```

Cada categoria preserva suas subpastas relativas. As duas pastas são criadas
mesmo quando uma categoria está vazia, deixando o pacote previsível. É possível
exportar apenas capturas, apenas IRs ou ambos.

O diálogo que solicita o nome contém as opções **Capturas** e **IRs**, ambas
marcadas inicialmente. O usuário pode excluir uma categoria da exportação; a
confirmação fica desativada quando as duas opções estão desmarcadas.

A preparação ocorre em uma pasta temporária e só depois é renomeada para o nome
final. Destinos existentes não são sobrescritos e destinos dentro das bibliotecas
abertas são recusados para evitar que um novo scan encontre cópias exportadas.
