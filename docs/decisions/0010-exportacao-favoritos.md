# 0010 — Exportação dos IRs favoritos por pasta

O usuário refinou o fluxo: primeiro exportar favoritos para uma pasta e então
usar as ferramentas das pedaleiras. Transferência direta para Blackbox e IR-Box
será estudada posteriormente, de forma independente para cada equipamento.

- A exportação inclui todos os favoritos válidos da pasta atualmente escaneada,
  sem depender dos filtros visuais. Favoritos de outras raízes não são misturados
  silenciosamente; basta abrir cada biblioteca para criar sua exportação.
- O usuário escolhe o diretório pai e o nome da nova pasta. A estrutura relativa
  é preservada, evitando colisões entre arquivos de subpastas com o mesmo nome.
- A aplicação não sobrescreve uma pasta existente. Também rejeita nomes inválidos
  no Windows e destinos dentro da própria raiz escaneada, que gerariam duplicatas.
- Os arquivos são copiados com metadados básicos via `copy2`. Primeiro é criada
  uma área temporária no mesmo destino; somente após todas as cópias ela é
  renomeada para o nome final. Falhas não publicam uma exportação parcial.
- A exportação contém apenas arquivos de áudio, sem banco ou manifesto que possa
  confundir o software da pedaleira. Nenhum favorito original é movido ou alterado.
- Este serviço não conhece Blackbox ou IR-Box. A mesma fronteira poderá receber
  exportação de capturas quando modelos e formatos confiáveis forem suportados.

Limitação atual: somente favoritos da biblioteca de IRs são exportados. Não há
conversão, limite de slots, achatamento de diretórios nem comunicação USB/MIDI.
