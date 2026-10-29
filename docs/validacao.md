# Validação da primeira fatia

Este é o registro cronológico completo em Português. Para os roteiros vigentes,
consulte a [navegação técnica em Português](pt-BR/technical.md) ou o
[validation guide in English](en/validation.md).

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
- Os seis WAVs, agora em `samples/`, foram lidos sem erros: duas DIs estéreo a 44,1 kHz
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

1. Abra uma DI e um IR de `samples/`; clique em Processar e reproduzir.
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

## Troca automática de IR e Git

O usuário validou o player anterior e solicitou troca automática ao selecionar
IR e versionamento. O comportamento de seleção descrito nos roteiros anteriores
foi substituído: a seleção agora processa automaticamente.

Auditoria deste incremento:

1. Abrir DI/pasta; clicar no primeiro IR inicia reprodução automaticamente.
2. Com Loop ativo, clicar em outro IR: contador continua, rótulo IR ativo muda
   após o processamento. Repetir com ↑/↓ na lista e ←/→ na janela.
3. Navegar rapidamente por vários IRs: a seleção mais recente deve prevalecer.
4. Pausar e selecionar outro IR: deve permanecer pausado, na mesma posição.
5. Durante processamento, usar Stop: deve permanecer parado ao concluir.
6. Selecionar WAV inválido: mostrar erro e manter o áudio anterior identificado.
7. Trocar entre IRs mono/estéreo: preservar posição, admitindo breve interrupção
   se o formato de saída exigir reabrir o stream. Não há crossfade nesta entrega.

Testes automatizados cobrem reutilização de stream, cursor/pausa, mudança de
canais e descarte de solicitação antiga com Stop durante processamento.

Resultado desta implementação: `python -m pytest -q` — **23 passed**;
`git diff --check` sem erros. Validação audível da troca pelo usuário pendente.

## Bypass, atalhos e cache de sessão

- `python -m pytest -q`: **29 passed**. Inclui eventos de teclado reais no Qt
  offscreen para B/Espaço, preservação de pausa/posição, bypass durante tarefa
  antiga, Stop durante preparação, invalidação por mudança de arquivo,
  descarte LRU, limite de memória e resultado maior que o cache.
- `git diff --check`: sem erros.
- Teste local com `clean_guitar.wav` e `2x12 ML FNDR Ox.wav`: primeira renderização
  cerca de 0,073 s nesta execução; nova consulta retornou o mesmo buffer sem
  processar. Cache de DI seca e resultado reteve 12.119.928 bytes. Ambos mantêm
  estéreo a 44,1 kHz; duração seca não contém a cauda do IR.
- Validação audível deste incremento ainda depende de auditoria do usuário.

Roteiro:

1. Reproduzir uma DI com IR; usar Espaço para pausar e retomar.
2. Usar B: conferir rótulo Bypass ativo, continuidade e áudio sem IR.
3. Pausar, alternar B duas vezes e conferir que permanece pausado na mesma posição.
4. Navegar entre IRs, voltar ao anterior e comparar a rapidez da aplicação.
5. Alternar B e selecionar IR rapidamente; conferir que a última escolha prevalece.
6. Usar Stop durante preparação de bypass: não deve começar a tocar ao terminar.
7. Abrir somente uma DI e ativar Bypass; deve funcionar sem pasta/IR.

## Biblioteca SQLite, favoritos e avaliação

- `python -m pytest -q`: **34 passed** após este incremento.
- Migração e reabertura do banco, preservação de campos do usuário no rescan,
  validação de rating, WAV inválido e atalhos Qt F/4 foram cobertos.
- O teste de interface fecha e reabre duas janelas sobre o mesmo banco e confirma
  favorito e quatro estrelas após novo scan.

Roteiro manual:

1. Abra uma pasta de IRs, selecione um item, pressione F e depois 1..5.
2. Confira checkbox de favorito e estrelas; navegue e retorne ao item.
3. Feche e reabra a aplicação, escaneie a mesma pasta e confirme persistência.
4. Altere favorito pelo checkbox e confirme que F acompanha o novo estado.
5. Coloque um `.wav` corrompido na pasta: ele deve ser ignorado e contado, sem
   impedir os demais IRs de aparecerem.
6. Verifique o banco no diretório documentado no README. Ele deve conter somente
   metadados e caminhos, sem blobs de áudio.

## Dispositivo e ganho de saída

- `python -m pytest -q`: **37 passed** após este incremento.
- Os testes cobrem enumeração apenas de saídas, API do host, dispositivo passado
  ao stream, preservação de cursor/estado na troca e atenuação sem alterar cache.
- No WSLg real foram listadas `pulse` e `default` via ALSA. A saída `pulse` foi
  aberta explicitamente em estéreo a 44,1 kHz, com -12 dB, e recebeu 250 ms de
  silêncio sem erros.

Roteiro manual:

1. Inicie a reprodução e escolha cada saída disponível. Confirme que o contador
   e o estado continuam após a breve reabertura do stream.
2. Pause, troque a saída e confirme que permanece pausado na mesma posição.
3. Mova o ganho de 0 para -12 e -24 dB e confirme redução progressiva de volume.
4. Volte a 0 dB e confira que o nível original retorna sem novo processamento.
5. Desconecte uma saída, se seguro, e confirme mensagem de erro; selecione uma
   saída válida e retome. Repetir no Windows/WASAPI e no Linux nativo.

## Filtros e notas

- `python -m pytest -q`: **39 passed** após este incremento.
- Os testes cobrem busca parcial, favorito, avaliação mínima, combinação dos
  metadados na lista, preservação da seleção de reprodução e notas no SQLite.
- Um teste Qt digita `F B 12345` e espaço no editor e confirma que favorito,
  bypass e rating não são acionados; depois salva e recarrega a nota.

Roteiro prático para aprovação antes do polimento:

1. Abra uma pasta com subpastas e confirme caminho, favorito e cinco estrelas
   em cada linha. Use 1..5 e 0 para definir e limpar avaliações.
2. Busque partes do nome, da pasta e misture maiúsculas/minúsculas.
3. Combine busca, Somente favoritos e avaliação mínima; limpe os filtros e
   confirme que todos os IRs válidos reaparecem.
4. Com áudio tocando, aplique filtros que ocultem o IR ativo. O áudio e o rótulo
   IR ativo devem continuar; selecionar outro item deve fazer a troca normal.
5. Escreva notas contendo letras F/B, números, espaços e setas. Confirme que o
   player não reage. Salve, navegue para outro IR e volte para conferir o texto.
6. Edite sem salvar e navegue: a edição deve ser descartada, conforme indicado
   no README. Feche/reabra após salvar para confirmar persistência.

## Exportação dos favoritos

- `python -m pytest -q`: **55 passed** após este incremento.
- Testes cobrem subpastas, conteúdo copiado, contagem/tamanho, exportação apesar
  de filtro visual, nomes inválidos no Windows, destino existente, arquivo fora
  da raiz e rejeição de destino dentro da biblioteca.
- A exportação usa staging temporário e os testes confirmam que ele é removido.

Roteiro prático:

1. Marque favoritos em diferentes subpastas da biblioteca aberta.
2. Aplique um filtro que mostre apenas um deles e clique Exportar favoritos.
3. Escolha uma pasta fora da biblioteca e informe um nome novo. Confirme que
   todos os favoritos foram copiados, preservando as subpastas.
4. Compare tamanho/conteúdo dos WAVs originais e exportados e teste a pasta no
   software de transferência da sua pedaleira.
5. Repita usando o mesmo nome: a aplicação deve recusar sem alterar a primeira
   exportação. Cancele cada diálogo e confirme que nenhuma pasta é criada.
6. Tente escolher a própria pasta de IRs como destino: deve ser recusado para
   evitar duplicatas. Os favoritos e arquivos originais devem permanecer intactos.

## Scan assíncrono

- `python -m pytest -q`: **57 passed** após este incremento.
- Os testes Qt agora aguardam o worker real para scans normais.
- Testes específicos bloqueiam artificialmente a inspeção de um arquivo e
  confirmam que a biblioteca anterior permanece visível, que a pasta mais
  recente prevalece e que Cancelar preserva a raiz anterior.

Roteiro prático:

1. Abra uma pasta grande. Durante o scan, mova/redimensione a janela e controle
   o player da biblioteca anterior; a interface deve continuar respondendo.
2. Observe a barra sair do modo indeterminado e avançar até o total de WAVs.
3. Clique Cancelar scan: a lista anterior deve permanecer e nenhum resultado
   parcial deve entrar no banco ou nos filtros.
4. Inicie um scan e, antes de terminar, escolha duas outras pastas em sequência.
   Somente a última deve aparecer ao final.
5. Inclua WAVs inválidos e confirme a contagem de ignorados após conclusão.
6. Feche a janela durante um scan. Ela deve cancelar com segurança e fechar
   assim que a inspeção do arquivo em andamento retornar.

## Preferências da aplicação

- `python -m pytest -q`: **62 passed** após este incremento.
- Os testes cobrem JSON ausente/corrompido, validação, limite do ganho, escrita
  atômica, restauração automática da DI e pasta, identidade estável da saída e
  fallback para caminhos e dispositivo que deixaram de existir.
- `python -m compileall -q src tests` e `git diff --check`: sem erros.

Roteiro prático:

1. Abra uma DI e uma pasta de IRs; escolha uma saída, ajuste ganho e Loop.
2. Exporte favoritos para uma pasta e feche a aplicação normalmente.
3. Reabra: confirme DI, scan automático dos IRs, saída, ganho e Loop. Abra a
   exportação novamente e confirme que o seletor começa no último destino.
4. Feche, desconecte ou renomeie o dispositivo salvo e reabra. A aplicação deve
   selecionar a saída padrão e continuar utilizável.
5. Feche, mova temporariamente a DI e a pasta de IRs e reabra. A janela deve
   iniciar sem erro e esquecer somente os caminhos que não existem mais.

## Crossfade na troca de IR

- `python -m pytest -q`: **66 passed** após este incremento.
- Testes cobrem a rampa de 10 ms, cursor preservado, troca pausada, descarte no
  Stop e rejeição de canais diferentes no transporte de mesmo stream.
- Preparar a transição estéreo a 48 kHz levou cerca de **10 µs por troca** no
  WSL desta sessão, em cinco séries de mil trocas. Isso não mede áudio real.
- `python -m compileall -q src tests` e `git diff --check`: sem erros.

Roteiro prático:

1. Com Loop ativo, alterne rapidamente entre dois IRs mono. Compare com a troca
   anterior e confirme ausência de estalo ou queda perceptível de duração longa.
2. Pause, escolha outro IR e pressione Play. A retomada deve começar na mesma
   posição e aplicar a transição sem iniciar áudio enquanto estava pausado.
3. Selecione outro IR durante a reprodução e pressione Stop durante o preparo.
   O áudio deve continuar parado e, no próximo Play, começar limpo do início.
4. Troque entre resultados mono e estéreo. Confirme a breve reabertura já
   esperada; este caso não usa crossfade.

## Pacote portátil Windows

O script de build foi preparado no WSL, mas o `.exe` ainda precisa ser gerado e
validado em Windows real. PyInstaller não é um cross-compiler.

1. Copie/clone o projeto para uma pasta local do Windows e execute
   `scripts\build-windows.ps1` no PowerShell com Python 3.12 instalado.
2. Confirme que os testes passam antes do empacotamento e que o ZIP contém a
   pasta completa, `LICENSE` e `README.md`.
3. Extraia o ZIP em outra pasta e abra `AuditionManager.exe` sem ativar venv.
4. Repita o roteiro de IR, saída WASAPI, ganho, Loop, crossfade, preferências e
   exportação. Feche/reabra o executável e confirme a persistência.
5. Registre versão do Windows, dispositivo/driver, tamanho do ZIP, aviso do
   SmartScreen e qualquer DLL ausente antes de decidir o instalador.

### Automação do pacote — 2026-10-29

- `scripts/build-windows.ps1` agora executa o `.exe` com
  `--packaging-smoke-test` antes de compactar o ZIP. O teste confirma imports e
  a presença de `nam-render.exe` no caminho usado pela aplicação congelada.
- `.github/workflows/windows-portable.yml` gera o pacote em `windows-2022` e o
  mantém como artefato por 14 dias. Na `develop`, mudanças relacionadas ao build
  disparam a execução; após o merge na branch padrão, também há execução manual.
- Os dois caminhos do autoteste têm cobertura automatizada; a suíte local passa
  com **87 testes**.
- A execução real do workflow e o teste auditivo do ZIP continuam pendentes.
- A primeira execução encontrou a migração de `windows-latest` para Visual Studio
  2026. O runner foi fixado em `windows-2022`, compatível com o gerador CMake do
  Visual Studio 2022; o script agora para imediatamente no comando que falhar.
- A segunda execução chegou ao compilador MSVC e revelou três usos upstream de
  `-Wno-error`, opção exclusiva de GCC/Clang. O build substitui essas ocorrências
  por `/WX-`, equivalente no MSVC, e valida a quantidade antes de alterar o
  arquivo do commit fixado.

### Retorno prático da interface Windows — 2026-10-29

- A janela inicial passou para 960 × 900, com mínimo de 110 px e distribuição de
  espaço equivalente para as listas de capturas e IRs.
- `nam-render.exe` usa `CREATE_NO_WINDOW`; a troca de captura não deve mais abrir
  uma janela de console. O tempo de inferência A2 continua real e deve ser
  comparado nos modos Full e Lite.
- O ZIP copia somente arquivos de `samples/` rastreados pelo Git. Assim inclui os
  exemplos redistribuíveis sem capturas TONE3000 ou arquivos pessoais locais.
- A suíte local passa com **89 testes**. Interface, tempo de troca e conteúdo do
  novo ZIP aguardam a próxima validação no Windows.

## Avaliação por estrelas clicáveis

- O teste Qt clica nas estrelas 2 e 4, confirma a atualização visual, consulta o
  valor persistido no SQLite e reabre a janela. Os atalhos anteriores continuam
  cobertos. A suíte completa permanece com **66 testes passando**.

Roteiro prático:

1. Selecione um IR e clique sucessivamente nas estrelas 1, 3 e 5. Confirme a
   nota na área de metadados e na linha da biblioteca.
2. Feche e reabra a aplicação; confirme que a última avaliação reaparece.
3. Use `0` para limpar e `1..5` para avaliar pelo teclado.
4. Remova a seleção com um filtro e confirme que as estrelas ficam desabilitadas.

## Seletor visual da pasta de IRs

- A suíte completa passa com **67 testes**.
- O teste Qt confirma que o diálogo permanece no modo de seleção de diretório,
  não ativa `ShowDirsOnly`, filtra WAVs e mostra **Escolher esta pasta**.

Roteiro prático:

1. Clique em **Selecionar pasta de IRs** e entre em uma pasta com WAVs.
2. Confirme que os nomes dos IRs aparecem no seletor, embora a ação continue
   escolhendo a pasta inteira.
3. Navegue por subpastas, volte à raiz desejada e clique em **Escolher esta
   pasta**. Confirme que o scan recursivo mantém o comportamento anterior.
