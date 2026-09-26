# Plano de execução

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
   auditoria. O campo de notas existe no esquema; editor e filtros permanecem
   para incrementos próprios.**
4. Seleção de dispositivo, ganho, mensagens de erro e validação Windows/Linux/WSLg.

Cada item acima é uma rodada com revisão própria. Critério do MVP completo:
DI em loop, navegação contínua entre IRs e metadados persistentes.

## 2 — Capturas NAM

Pesquisar runtime oficial/open source, manutenção, licença e viabilidade no
Windows. Documentar alternativas antes de instalar dependências. Definir
`CaptureEngine` com supports/load/process/unload e contrato de canais,
blocos, sample rate e estado. Implementar apenas um formato comprovado.

## 3 — Entrada ao vivo

Investigar WASAPI/ASIO, buffers, taxas, concorrência e latência. Medir antes de
migrar DSP. Meta exploratória: 48 kHz, 64/128 amostras; não é compromisso desta
fase. Callbacks não devem fazer I/O, carregar modelos ou alocar grandes buffers.
Convolução por blocos e eventual backend C++/JUCE exigem contrato próprio.

## 4 — ANN / A2 / Blackbox

Pesquisar separadamente formatos e ferramentas; classificação por extensão
não comprova compatibilidade. Não inventar parsers ou conversores proprietários.
Investigar exportação e USB/MIDI/SysEx somente com evidências/documentação.

## 5 — Biblioteca e distribuição

Filtros, comparação de centenas de capturas/IRs, exportação, instalador Windows,
reprodutibilidade das dependências e revisão das licenças redistribuídas.

## Riscos técnicos

- Memória e tempo de pré-processamento crescem com duração, canais e sample rate.
- Troca contínua exige sincronização entre resultado, cursor e callback de áudio.
- Taxas distintas, nível dos IRs e caudas afetam comparação e loops.
- Drivers/PortAudio/Qt precisam ser testados no Windows real, além do WSL.
- Disponibilidade e licenças de runtimes NAM/ANN/A2 ainda precisam de pesquisa.
- PySide6 e demais dependências têm licenças próprias; MIT cobre nosso código.
