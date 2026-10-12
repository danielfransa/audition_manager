# 0012 — Preferências da aplicação

Segundo incremento do polimento técnico aprovado pelo usuário.

- Preferências ficam em `preferences.json`, separadas do SQLite da biblioteca.
  O banco representa IRs catalogados; o JSON representa escolhas da aplicação.
- O arquivo contém versão de formato, última DI, pasta de IRs, destino de
  exportação, saída de áudio, ganho e Loop. A gravação usa um arquivo temporário
  na mesma pasta e substituição atômica para evitar conteúdo parcial.
- O dispositivo é identificado pela combinação de nome e API do host. Índices
  do PortAudio não são persistidos porque podem mudar entre execuções.
- Ao abrir, a DI é restaurada e a última pasta de IRs inicia um scan assíncrono.
  A reprodução continua dependendo da seleção de um IR ou do bypass.
- Caminhos removidos são esquecidos. Uma saída ausente volta para a saída padrão
  do sistema. JSON ausente, corrompido ou de versão desconhecida usa os padrões
  seguros: saída do sistema, 0 dB e Loop ativo.
- Falha ao salvar é informada no status da janela e não impede áudio, scan ou
  encerramento. O ambiente de teste injeta seu próprio arquivo temporário.
