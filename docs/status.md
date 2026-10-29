# Status atual do projeto

Atualizado em **29 de outubro de 2026**. Este arquivo é o resumo vigente; os
registros em `docs/decisions/` e as seções antigas de `docs/validacao.md` formam
o histórico de cada incremento e podem mencionar limitações já resolvidas.

## Entregue

- Aplicação desktop Python/PySide6 para Windows e Linux, executada e validada
  pelo usuário no WSL/WSLg.
- Seleção de DI WAV e scan recursivo, assíncrono e cancelável de bibliotecas IR.
- Convolução offline, reamostragem, proteção de pico, reprodução, posição,
  Play/Pause/Stop/Loop e bypass.
- Troca automática de IR, cache limitado e crossfade linear de 10 ms quando o
  formato do stream permanece igual.
- Biblioteca SQLite com favoritos, avaliação de 0 a 5, estrelas clicáveis,
  atalhos, busca, filtros e notas.
- Exportação de IRs e capturas favoritos para uma pasta escolhida, separados em
  `IRs` e `Capturas` e preservando as subpastas de origem.
- Seleção de saída, ganho e mensagens específicas para configuração WSLg.
- Preferências JSON com DI, pasta de IRs, destino de exportação, dispositivo,
  ganho e Loop, incluindo fallback para recursos removidos.
- Configuração `mise`/venv, licença MIT, documentação técnica e versionamento
  Git em commits pequenos.
- Duas DIs e quatro IRs de exemplo para o primeiro teste após o clone.
- Duas capturas A2 de guitarra do RiffSmith, redistribuídas sob licença MIT com
  origem e commit documentados.
- Seletor Português/English na aplicação, com troca imediata dos principais
  controles e persistência da preferência.
- README público bilíngue e guias completos de instalação e uso em Português e
  Inglês, com navegação separada por idioma.
- Documentação técnica navegável nos dois idiomas, incluindo status,
  desenvolvimento, validação, plano e registro das 25 decisões anteriores.
- Script PowerShell para gerar pacote portátil Windows com PyInstaller.
- Capturas NAM A2 combinadas com IR na cadeia offline `DI → NAM → IR`.
- Bypasses independentes para captura NAM e IR, com atalhos `N` e `B`.
- Biblioteca NAM com busca, filtros, favoritos, avaliação, notas e persistência.
- Exportação conjunta implementada com separação em `Favoritos/Capturas` e
  `Favoritos/IRs`, seleção das categorias e sem criar pastas vazias.
- Ganho NAM independente, medidor de pico e proteção de pico em toda a cadeia.
- Modos A2 Full/Lite e suporte estrutural a NAM legado WaveNet, LSTM, ConvNet,
  Linear e Sequential.

## Verificação atual

- Suíte automatizada: **85 testes passando**.
- Compilação de bytecode e `git diff --check`: sem erros na última entrega.
- Reprodução e interface: confirmadas no WSL/WSLg pelo usuário.
- Saída PortAudio no WSLg: validada com a ponte ALSA/PulseAudio.
- Branch local: `develop`.

## Em andamento — NAM A2

- A2 foi escolhido como o primeiro formato de captura de amplificador.
- `NeuralAmpModelerCore` foi integrado como processo nativo isolado e fixado no
  commit `0b3d3c9`. O renderer oficial carregou uma captura A2 real no WSL.
- A interface aceita uma pasta de capturas, valida `SlimmableContainer`, converte
  a DI para mono/48 kHz e combina a saída com o IR selecionado.
- A compilação e audição ainda precisam ser validadas em Windows e Linux nativo.
- O pacote Python de treinamento, com PyTorch, não será adicionado sem necessidade.

## BlackBox e AM4DATA

- O software oficial da M-VAVE documenta conversão NAM para AM4DATA.
- A primeira solução prevista é exportar/organizar o `.nam` no Audition Manager
  e usar o conversor oficial para a BlackBox.
- Geração direta de AM4DATA e transferência para BlackBox ou IR-Box não estão
  implementadas e dependem de documentação ou protocolo confiável.

## Validações pendentes

- Gerar `AuditionManager-Windows-x64.zip` em Windows real e executar o roteiro
  de interface, WASAPI, preferências, exportação e encerramento.
- Executar o roteiro completo em Linux nativo; WSLg não substitui essa validação.
- Avaliar instalador e assinatura somente após aprovar o pacote portátil.
- Validar auditivamente as estrelas clicáveis e o crossfade no uso cotidiano.
- Revisar licenças e avisos das dependências antes de distribuir binários.

## Referências de acompanhamento

- `PLAN.md`: etapas, ordem de implementação e riscos.
- `docs/validacao.md`: resultados e roteiros manuais acumulados.
- `docs/decisions/`: decisões técnicas numeradas e fontes consultadas.
- `README.md`: apresentação bilíngue e acesso à documentação de cada idioma.
- `docs/pt-BR/` e `docs/en/`: visão, instalação e guia de uso completos.
- `docs/pt-BR/technical.md` e `docs/en/README.md`: índices técnicos por idioma.
- `docs/installation.md`: seletor de idioma para os guias de instalação.
- `docs/development.md`: arquitetura, testes e limites internos.
