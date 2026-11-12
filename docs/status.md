# Status atual do projeto

Atualizado em **12 de novembro de 2026**. Este arquivo é o resumo vigente; os
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
- Workflow do GitHub Actions para compilar o ZIP em `windows-2022`,
  com autoteste de imports e presença do runtime NAM no executável congelado.
- Pacote Windows com exemplos versionados, janela sem console durante a
  inferência NAM e listas de capturas/IRs com espaço mínimo legível.
- Capturas NAM A2 combinadas com IR na cadeia offline `DI → NAM → IR`.
- Bypasses independentes para captura NAM e IR, com atalhos `N` e `B`.
- Biblioteca NAM com busca, filtros, favoritos, avaliação, notas e persistência.
- Exportação conjunta implementada com separação em `Favoritos/Capturas` e
  `Favoritos/IRs`, seleção das categorias e sem criar pastas vazias.
- Ganho NAM independente, medidor de pico e proteção de pico em toda a cadeia.
- Modos A2 Full/Lite e suporte estrutural a NAM legado WaveNet, LSTM, ConvNet,
  Linear e Sequential.
- Pré-release `v0.1.0-alpha` publicada com ZIP portátil validado em Windows real.

## Verificação atual

- Suíte automatizada: **101 testes passando**.
- Compilação de bytecode e `git diff --check`: sem erros na última entrega.
- Reprodução e interface: confirmadas no WSL/WSLg pelo usuário.
- Saída PortAudio no WSLg: validada com a ponte ALSA/PulseAudio.
- Pacote portátil, interface, runtime NAM, samples e reprodução: validados pelo
  usuário em Windows real na revisão `eeed30f`.
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

- Executar o roteiro completo em Linux nativo; WSLg não substitui essa validação.
- Ampliar a validação pública da pré-release antes de avaliar instalador e
  assinatura digital.
- Validar auditivamente as estrelas clicáveis e o crossfade no uso cotidiano.
- Revisar licenças e avisos das dependências antes de distribuir binários.

## Próximos marcos aprovados

1. Nova alpha de comparação equilibrada: leitura dos metadados de nível NAM,
   equalização automática opcional e medição/cache para NAMs sem metadados e IRs.
2. Entrada de guitarra ao vivo, com latência e estabilidade medidas.
3. Comparação cega, ocultando identidade e avaliações até a nova classificação.
4. Instalador Windows, depois da consolidação dos três marcos anteriores.

O modo de comparação cega foi deliberadamente deixado para depois da entrada ao
vivo. O ZIP portátil continua sendo a distribuição oficial para Windows até a
etapa final do instalador. Detalhes e critérios estão no `PLAN.md` e na decisão
0030.

### Próxima alpha — incremento 1 em auditoria

- O scan NAM agora lê `metadata.loudness`, `metadata.input_level_dbu` e
  `metadata.output_level_dbu` quando forem números finitos.
- A migração SQLite v3 persiste os três campos opcionais sem perder favoritos,
  avaliações ou notas existentes.
- A interface apresenta os valores da captura selecionada em Português e Inglês.
- Metadados ausentes ou inválidos não invalidam a captura e aparecem como “não
  informado”. Este incremento não aplica compensação nem altera o áudio.

### Próxima alpha — incremento 2 em auditoria

- O checkbox **Igualar volume automaticamente** ativa ou desativa a compensação
  e tem sua escolha persistida nas preferências.
- Capturas com `metadata.loudness` são ajustadas em direção ao alvo de -18 dB,
  com compensação limitada entre -24 e +12 dB.
- O valor aplicado aparece ao lado do checkbox. Sem loudness, a interface informa
  que a compensação está indisponível e mantém o nível original.
- O ganho NAM manual continua independente e a proteção de pico permanece ativa.

### Próxima alpha — incremento 3 em auditoria

- A cadeia completa é processada sem limite, medida por loudness integrado
  BS.1770, compensada em direção a -18 LUFS e protegida contra pico ao final.
- A migração SQLite v4 guarda medições por identidade de DI, NAM, IR, Full/Lite,
  alvo e versão do algoritmo.
- Alterar qualquer componente gera outra chave e uma nova medição.
- Áudio curto ou silencioso usa fallback NAM identificado quando disponível; sem
  fallback, mantém 0 dB. Esses resultados também são armazenados.
- `pyloudnorm` 0.2.0, sob licença MIT, foi adicionada como dependência.

O desenho do terceiro incremento e seus critérios de aceite estão em
[`docs/comparacao-nivel.md`](comparacao-nivel.md). As mudanças entre a versão
atual e a próxima alpha serão mantidas no rascunho
[`docs/releases/v0.2.0-alpha.md`](releases/v0.2.0-alpha.md) até a publicação.

## Referências de acompanhamento

- `PLAN.md`: etapas, ordem de implementação e riscos.
- `docs/validacao.md`: resultados e roteiros manuais acumulados.
- `docs/decisions/`: decisões técnicas numeradas e fontes consultadas.
- `README.md`: apresentação bilíngue e acesso à documentação de cada idioma.
- `docs/pt-BR/` e `docs/en/`: visão, instalação e guia de uso completos.
- `docs/pt-BR/technical.md` e `docs/en/README.md`: índices técnicos por idioma.
- `docs/installation.md`: seletor de idioma para os guias de instalação.
- `docs/development.md`: arquitetura, testes e limites internos.
