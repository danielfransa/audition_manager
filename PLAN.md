# Plano de execução

O resumo vigente de entregas, verificações e pendências está em
[`docs/status.md`](docs/status.md). Este plano registra a ordem do trabalho.

## Processo

Entregar uma fatia pequena por rodada, com código, verificação e decisões
registradas em `docs/decisions/`. Ao terminar, parar para auditoria e correções.
O prompt original está em `docs/prompt-inicial.md`; os ajustes posteriores do
usuário e as decisões técnicas estão nos registros de `docs/decisions/`.
Windows e Linux são alvos; WSL/WSLg é ambiente de testes rápidos da aplicação
(conforme decisão 0002, que amplia o escopo inicial).

## 0 — Fundação e primeira fatia (implementada; aceite por plataforma pendente)

- [x] README, licença MIT, pyproject, mise + venv e documentação.
- [x] GUI: selecionar DI WAV e diretório de IRs; listar recursivamente.
- [x] Selecionar IR, convoluir offline e iniciar reprodução com Stop/Loop.
- [x] Isolar DSP, leitura, saída e descoberta da interface.
- [x] Testes automatizados com dados sintéticos.
- [ ] Executar roteiro manual com dispositivo real no Windows.
- [ ] Executar roteiro manual em Linux nativo.
- [x] Usuário confirmou funcionamento da primeira fatia no WSL/WSLg.
- [x] Usuário autorizou o próximo incremento após testar.

## 1 — MVP de IRs (em andamento, em pequenas entregas)

1. Player com posição, Play/Pause/Stop/Loop; saída desacoplada de conveniências
   globais do sounddevice. Testes de transições e término da faixa.
   **Validado pelo usuário; avanço autorizado.**
2. Troca de IR preservando posição e reprodução; cache limitado e descarte de
   resultados obsoletos. Bypass, LEFT/RIGHT, SPACE e B. Avaliar crossfade.
   **Troca automática, posição preservada, descarte de resultados obsoletos e
   LEFT/RIGHT validados pelo usuário. Cache limitado, bypass e SPACE/B
   implementados para auditoria. Crossfade avaliado e adiado: exige transição
   entre buffers e política para mudanças de canais, sem bloquear o MVP.**
3. Biblioteca SQLite: metadados e caminhos, migrações, favorito, rating 1–5,
   notas; atalhos F e 1–5. Sem copiar áudio para o banco.
   **Metadados, migração, favorito, rating e atalhos implementados para
   auditoria. Busca, filtros por favorito/rating, indicador na lista e editor
   persistente de notas implementados. As estrelas agora são clicáveis e mantêm
   os atalhos numéricos; aguardando validação prática.**
4. Seleção de dispositivo, ganho, mensagens de erro e validação Windows/Linux/WSLg.
   **Seleção de saída e ganho de -24 a 0 dB implementados para auditoria;
   validação automática e stream real no WSLg concluídos. Windows e Linux
   nativo permanecem nos roteiros manuais por plataforma.**

Cada item acima é uma rodada com revisão própria. Critério do MVP completo:
DI em loop, navegação contínua entre IRs e metadados persistentes.

5. Exportar os IRs favoritos da pasta aberta para uma nova pasta escolhida pelo
   usuário, preservando subpastas e sem sobrescrever exportações existentes.
   **Implementado para auditoria:** a exportação conjunta inclui favoritos das
   duas bibliotecas em subpastas separadas, `Favoritos/Capturas` e
   `Favoritos/IRs`, preserva subpastas e não sobrescreve destinos existentes.
   O diálogo permite incluir ambos os tipos ou somente um deles.

## 1.1 — Polimento do MVP

1. Scan assíncrono com progresso, cancelamento e descarte de resultados antigos.
   **Implementado para auditoria; 57 testes automatizados passando.**
2. Persistir última DI/pasta de IR/exportação, dispositivo, ganho e Loop, com
   fallback quando recursos não estiverem disponíveis.
   **Implementado para auditoria; preferências JSON têm escrita atômica e
   fallback para caminhos ou dispositivos ausentes.**
3. Medir e decidir a implementação de crossfade curto na troca de IR.
   **Crossfade linear de 10 ms implementado para trocas com mesma taxa e canais;
   preparação medida em cerca de 10 µs por troca. Mudança de canais continua
   reabrindo o stream sem crossfade.**

## 2 — Capturas NAM A2

Pesquisar runtime oficial/open source, manutenção, licença e viabilidade no
Windows. Documentar alternativas antes de instalar dependências. Definir
`CaptureEngine` com supports/load/process/unload e contrato de canais,
blocos, sample rate e estado. Implementar apenas um formato comprovado.

**Decisão inicial:** priorizar NAM A2 em `.nam`, com NeuralAmpModelerCore como
runtime candidato. Não adicionar o pacote de treinamento PyTorch ao aplicativo.
Validar `SlimmableContainer`, A2 Full/Lite, desempenho e integração Windows/Linux
em um protótipo isolado antes da interface.

**Implementado para auditoria:** validação de A2 `SlimmableContainer`, runtime
oficial fixado por commit, downmix/reamostragem para 48 kHz e cadeia offline
`DI → NAM → IR`. A interface lista capturas separadamente e preserva o fluxo
somente com IR. Falta a validação prática e auditiva em Windows e Linux nativo.

**Biblioteca implementada para auditoria:** busca, filtros, favoritos, estrelas,
notas, navegação `Ctrl+←/→` e restauração da última pasta/seleção. A migração
SQLite versão 2 preserva os metadados em novos scans.

**Comparação de nível implementada para auditoria:** ganho NAM de -24 a +12 dB,
medidor do pico processado, proteção contra clipping e descrição explícita da
cadeia e dos bypasses. O ganho é persistido e participa da chave do cache.

**Compatibilidade ampliada para auditoria:** A2 permite escolher Full ou Lite;
modelos legados WaveNet, LSTM, ConvNet, Linear e Sequential são encaminhados ao
runtime sem parâmetro de slimming. Arquitetura e versão aparecem na biblioteca.

## 3 — Internacionalização

1. Catálogo i18n da aplicação, seletor Português/English, troca em tempo de
   execução e persistência. **Implementado para auditoria.**
2. README público bilíngue curto com links para guias completos de instalação e
   uso em PT e EN. **Implementado para auditoria.**
3. Espelhar documentação técnica, status e decisões nos dois idiomas, com
   navegação clara. **Pendente.**

## 4 — Distribuição Windows

Gerar e validar o pacote portátil em Windows real já com os dois idiomas e o
runtime NAM. Depois avaliar instalador, assinatura e publicação em Releases.

## 5 — Entrada ao vivo

Investigar WASAPI/ASIO, buffers, taxas, concorrência e latência. Medir antes de
migrar DSP. Meta exploratória: 48 kHz, 64/128 amostras; não é compromisso desta
fase. Callbacks não devem fazer I/O, carregar modelos ou alocar grandes buffers.
Convolução por blocos e eventual backend C++/JUCE exigem contrato próprio.

## 6 — AM4DATA / Blackbox / IR-Box

Pesquisar separadamente formatos e ferramentas; classificação por extensão
não comprova compatibilidade. Não inventar parsers ou conversores proprietários.
Investigar exportação e USB/MIDI/SysEx somente com evidências/documentação.
Usar inicialmente o conversor oficial NAM → AM4DATA da M-VAVE. Tratar Blackbox
e IR-Box como destinos independentes: pesquisar protocolos,
limites, formatos e ferramentas de cada equipamento antes de transferência direta.

## 7 — Biblioteca em escala

Comparação de centenas de capturas/IRs, reprodutibilidade das dependências e
revisão das licenças redistribuídas.

## Riscos técnicos

- Memória e tempo de pré-processamento crescem com duração, canais e sample rate.
- Troca contínua exige sincronização entre resultado, cursor e callback de áudio.
- Taxas distintas, nível dos IRs e caudas afetam comparação e loops.
- Drivers/PortAudio/Qt precisam ser testados no Windows real, além do WSL.
- Disponibilidade e licenças de runtimes NAM/ANN/A2 ainda precisam de pesquisa.
- PySide6 e demais dependências têm licenças próprias; MIT cobre nosso código.
