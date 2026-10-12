# 0011 — Scan assíncrono e cancelável

Primeiro incremento do polimento técnico aprovado pelo usuário.

- Enumeração recursiva e leitura dos cabeçalhos WAV acontecem em `ScanWorker`,
  separado da thread Qt da interface. Banco, widgets e troca da biblioteca
  continuam exclusivamente na thread principal.
- A biblioteca já aberta permanece disponível durante o novo scan. Somente um
  resultado completo e correspondente à última pasta escolhida atualiza SQLite,
  lista, filtros e raiz de exportação.
- Escolher outra pasta solicita interrupção do worker atual e registra a nova
  raiz desejada. Não são criadas várias threads concorrentes. Ao terminar a
  interrupção, inicia somente o pedido mais recente.
- Cancelar limpa a raiz desejada e mantém lista, reprodução, favoritos e notas
  anteriores. O botão e a barra existem apenas enquanto há trabalho ativo.
- Progresso é determinado após enumerar os candidatos e avança por cabeçalho
  analisado, incluindo arquivos inválidos. Durante a enumeração, a barra fica
  indeterminada. A interrupção ocorre entre arquivos; uma chamada de leitura de
  cabeçalho já iniciada precisa retornar primeiro.
- Fechar durante o scan solicita cancelamento e adia o fechamento até a thread
  terminar, evitando destruir um `QThread` ainda ativo.
- O helper `inspect_wav` mantém a leitura unitária reutilizável e testável; o
  scanner síncrono existente continua útil fora da interface.

O upsert SQLite e a reconstrução visual ainda ocorrem na thread principal após
o scan. Para centenas de registros são operações curtas; serão medidas com uma
biblioteca real antes de adicionar outra camada assíncrona.
