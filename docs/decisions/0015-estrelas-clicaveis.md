# 0015 — Avaliação por estrelas clicáveis

O usuário identificou que somente exibir as estrelas e depender dos atalhos
numéricos não era intuitivo.

- As cinco estrelas da área de metadados são botões. Clicar na posição desejada
  define imediatamente uma avaliação de 1 a 5 e persiste o valor no SQLite.
- As estrelas ficam desabilitadas sem um IR selecionado. Cada botão expõe nome
  acessível e tooltip com seu valor.
- Os atalhos `1` a `5` continuam disponíveis e `0` continua removendo a nota.
  Isso preserva o fluxo rápido pelo teclado sem esconder a ação principal.
- A mesma interação deverá ser reutilizada na futura biblioteca NAM A2.
