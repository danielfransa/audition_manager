# 0017 — Mostrar IRs ao escolher a pasta

O usuário observou que o seletor de diretório permitia navegar pelas subpastas,
mas mostrava uma área vazia porque o diálogo nativo ocultava todos os arquivos.
Isso dava a impressão de que a pasta não continha IRs.

- A seleção continua retornando uma pasta, pois a biblioteca faz scan recursivo
  a partir dela; nenhum WAV individual passa a ser a raiz da biblioteca.
- O diálogo Qt não nativo é usado para manter o modo `Directory` e, ao mesmo
  tempo, exibir arquivos `.wav` e `.WAV` como referência visual.
- O botão de confirmação recebe o texto **Escolher esta pasta**, deixando claro
  que os arquivos visíveis não são a seleção final.
- O diálogo inicia na última biblioteca válida, como antes.
- Um teste Qt verifica modo de diretório, filtro WAV, visibilidade dos arquivos,
  uso do diálogo não nativo e texto do botão.
