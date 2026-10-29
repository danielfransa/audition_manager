# 0028 — Polimento da interface e execução no Windows

Data: 29 de outubro de 2026

## Contexto

O primeiro ZIP executou em Windows, mas o estilo nativo deixou as listas NAM e
IR pequenas, cada chamada do renderer abriu uma janela de console e o pacote não
levava os exemplos usados no roteiro inicial.

## Decisão

- Aumentar a janela inicial para 960 × 900 e dar às duas listas altura mínima de
  110 px e participação equivalente no espaço vertical disponível.
- Colocar todo o formulário central em uma área rolável e redimensionável. Se a
  resolução ou escala do Windows não comportar a altura mínima, a janela passa a
  rolar verticalmente em vez de sobrepor widgets.
- Iniciar o processo NAM com `CREATE_NO_WINDOW` somente no Windows. Linux mantém
  a chamada padrão do `subprocess`.
- Copiar para o ZIP apenas arquivos sob `samples/` retornados por `git ls-files`.
  Arquivos locais não rastreados não podem entrar no artefato por acidente.
- Não confundir ocultar o console com reduzir inferência: A2 Full/Lite continuará
  sendo medido no Windows antes de decidir otimizações de processo ou cache.
- Publicar o ZIP como arquivo direto no GitHub Actions (`archive: false`), pois o
  modo padrão criava uma segunda camada ZIP ao redor do pacote já compactado.

## Consequências

O pacote fica utilizável no primeiro início e não pisca uma janela DOS ao trocar
capturas. A janela exige mais espaço inicial, mas preserva mínimo de 760 × 700 e
pode ser redimensionada. A latência remanescente será tratada com medidas, sem
alterar a fidelidade silenciosamente.
