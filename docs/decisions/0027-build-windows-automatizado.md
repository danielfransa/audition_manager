# 0027 — Build Windows automatizado e verificável

Data: 29 de outubro de 2026

## Contexto

O PyInstaller não gera executáveis Windows a partir do WSL. O script PowerShell
existente criava o pacote, mas não executava o resultado e exigia que cada teste
começasse em uma máquina Windows configurada para desenvolvimento.

## Decisão

- Adicionar `--packaging-smoke-test`, executado antes da inicialização do Qt,
  para confirmar imports e a localização do runtime NAM no pacote congelado.
- Fazer `build-windows.ps1` interromper a geração se o autoteste falhar.
- Incluir no ZIP um README bilíngue específico para o pacote portátil.
- Disponibilizar um workflow em `windows-latest`, com permissões somente de
  leitura e retenção do artefato por 14 dias. Enquanto ele não estiver na branch
  padrão, alterações relevantes na `develop` iniciam o build automaticamente;
  `workflow_dispatch` permanece disponível após o merge.
- Não incluir os áudios locais ou capturas TONE3000 no pacote.

## Consequências

Um colaborador pode obter um ZIP Windows pela interface do GitHub sem manter uma
máquina de build. O autoteste detecta pacote incompleto, mas não substitui os
testes de interface, WASAPI, som audível, SmartScreen e latência em Windows real.
