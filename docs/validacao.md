# Validação da primeira fatia

## Automática

Execute `mise run test` no WSL ou `python -m pytest` com a venv ativa.
Os testes sintetizam áudio em diretórios temporários; não usam arquivos pessoais.
A saída da GUI é substituída por um objeto falso, sem dispositivo de áudio.
O teste da GUI é ignorado quando Qt não pode ser importado por falta de
bibliotecas nativas; esse resultado não equivale a uma validação da interface.

## Resultado nesta entrega — 2026-09-26

- Ambiente: WSL/Linux, Python 3.12.13, venv local e instalação editável.
- `python -m pytest -q`: **11 passed, 1 skipped**. Teste Qt ignorado porque
  `libxkbcommon.so.0` não está instalada no ambiente.
- `python -m compileall -q src tests`: concluído sem erros.
- TOML de `mise.toml` e `pyproject.toml`: sintaxe validada com `tomllib`.
- Versões utilizadas: NumPy 2.5.3, SciPy 1.18.1, soundfile 0.14.0,
  sounddevice 0.5.6, PySide6 6.11.2 e pytest 9.1.1.
- A venv foi criada explicitamente para os testes. O hook interativo do mise
  e a criação ao entrar na pasta não foram exercitados nesta sessão.
- Interface gráfica, reprodução real e execução nativa Windows: pendentes.

## Revisão Linux/WSL e fontes — 2026-09-26

- Após a instalação das bibliotecas Qt pelo usuário, os **12 testes passaram**,
  incluindo o fluxo da interface offscreen com saída de áudio falsa.
- `fc-list` retornou vazio; o Qt não encontrou fontes reais utilizáveis.
- A nova verificação de inicialização foi exercitada sem fontes: encerrou com
  código 1 e instrução de instalação legível no terminal.
- A instalação de `ttf-dejavu` depende de sudo no terminal do usuário; a
  tentativa automatizada não instalou o pacote porque exigiu senha.
- Renderização com fonte instalada e reprodução real no WSL ainda pendentes.
  A consulta PortAudio nesta sessão do agente não listou dispositivos de áudio.

## Roteiro de aceite por plataforma (pendente)

Executar separadamente no Windows, Linux nativo e WSL/WSLg.

1. Instalar em uma venv própria do sistema conforme README e abrir
   `audition-manager`. Confirmar que textos, acentos e nomes de arquivos estão
   legíveis na janela principal e nos seletores de DI e diretório.
2. Abrir DI WAV mono; escolher pasta com IRs em subdiretórios e extensões
   `.wav`/`.WAV`. Confirmar nomes relativos e seleção.
3. Selecionar IR e processar/reproduzir. Confirmar som no dispositivo padrão,
   responsividade da janela e funcionamento do Stop.
4. Repetir com Loop habilitado/desabilitado e verificar final da faixa/cauda.
5. Trocar o IR e clicar novamente: nesta fatia a reprodução reinicia do começo.
6. Testar DI/IR mono e estéreo e taxas de 44,1/48 kHz diferentes.
7. Testar pasta vazia, WAV inválido, IR acima de 2 s e DI acima de 300 s:
   a janela deve informar erro e continuar utilizável.
8. Verificar encerramento: durante processamento a janela pede para aguardar;
   depois de concluído, fechar encerra reprodução e aplicativo.
9. Registrar dispositivo, driver, versão Python, versões das dependências,
   resultados e eventuais falhas neste documento antes de marcar aceite.

Testes no WSL não comprovam reprodução nem latência no Windows.

## Revisão da saída WSLg e exemplos — 2026-09-26

- `PULSE_SERVER` aponta para `unix:/mnt/wslg/PulseServer`; consulta fora do
  isolamento confirmou servidor PulseAudio acessível e saída padrão `RDPSink`.
- PortAudio não listou dispositivos; `alsa-plugins` e `pulseaudio-alsa` ausentes.
  A instalação da ponte pelo usuário e o teste audível permanecem pendentes.
- Os seis WAVs de `exemples/` foram lidos sem erros: duas DIs estéreo a 44,1 kHz
  e quatro IRs mono a 44,1 kHz, cada um com 8192 amostras.
- As oito combinações DI × IR foram processadas com sucesso, com saída estéreo
  e picos aproximadamente em 0,95 após a atenuação já prevista.
- A mensagem da aplicação agora explica a indisponibilidade da saída padrão,
  com instruções da ponte quando detecta a configuração PulseAudio do WSLg.
- Esses testes de arquivos validam leitura e DSP, não reprodução audível.

### Confirmação após instalar a ponte ALSA/PulseAudio

O usuário instalou os plugins. A consulta fora do isolamento passou a listar
`pulse` e `default` (ALSA), com `default` selecionado como saída padrão.
A verificação de formato e a reprodução bloqueante de 250 ms de silêncio
estéreo a 44,1 kHz concluíram sem erros. Isso confirma abertura e envio de áudio
na taxa dos exemplos; a confirmação de som audível continua sendo manual.

## Incremento do player — 2026-09-26

O usuário confirmou reprodução funcional da primeira fatia no WSL/WSLg e
pediu a próxima etapa. O novo player passou em **20 testes automatizados**:
convolução, scanner, GUI, pausa/retomada, rewind no Stop, fim de faixa, sobra
zerada no último bloco, loop atravessando vários ciclos e erro ao abrir a saída.

Também foi exercitado o OutputStream real no WSLg com silêncio estéreo a
44,1 kHz: a posição ficou estável durante pausa; retomada, Stop, término,
replay e fechamento concluíram sem erros. Esse teste não confirma qualidade
sonora; a auditoria audível do novo player continua pendente.

### Roteiro manual deste incremento

1. Abra uma DI e um IR de `exemples/`; clique em Processar e reproduzir.
2. Confira contador, barra de progresso e botão Pause.
3. Pause: o contador deve parar. Clique Play: deve continuar da posição pausada,
   sem mostrar novamente a mensagem de processamento.
4. Clique Stop: contador retorna a zero. Play deve iniciar do começo sem
   processar novamente.
5. Desative Loop durante reprodução e aguarde: deve chegar a Finalizado.
   Clique Play para recomeçar.
6. Ative Loop e confira que, ao terminar, a faixa continua desde o início.
7. Selecione outro IR: nesta etapa o áudio para, o contador zera e o botão
   volta a Processar e reproduzir. Confirme novo processamento e reprodução.
8. Feche durante reprodução e confirme que o som termina.

Repetir no Windows e Linux nativo quando disponíveis. A barra ainda não permite
arrastar a posição; troca contínua e crossfade pertencem ao próximo incremento.
