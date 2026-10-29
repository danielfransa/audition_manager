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
- Disponibilizar um workflow em `windows-2022`, com permissões somente de
  leitura e retenção do artefato por 14 dias. Enquanto ele não estiver na branch
  padrão, alterações relevantes na `develop` iniciam o build automaticamente;
  `workflow_dispatch` permanece disponível após o merge.
- Fixar o runner em `windows-2022`, que inclui Visual Studio 2022, evitando que a
  migração de `windows-latest` para Visual Studio 2026 altere o compilador sem
  uma decisão explícita.
- Verificar o código de saída de cada comando Git e CMake e interromper no ponto
  da causa, em vez de continuar até faltar o arquivo final.
- Corrigir localmente, durante o build, as três ocorrências upstream de
  `COMPILE_FLAGS "-Wno-error"` para o equivalente MSVC `/WX-`. O commit do Core
  permanece fixado e a substituição falha se a estrutura esperada mudar.
- Não incluir os áudios locais ou capturas TONE3000 no pacote.

## Consequências

Um colaborador pode obter um ZIP Windows pela interface do GitHub sem manter uma
máquina de build. O autoteste detecta pacote incompleto, mas não substitui os
testes de interface, WASAPI, som audível, SmartScreen e latência em Windows real.
