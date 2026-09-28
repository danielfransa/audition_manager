# Audition Manager

Aplicação desktop open source para guitarristas experimentarem Impulse Responses
(IRs) e, futuramente, capturas de amplificadores antes de transferir os arquivos
para uma pedaleira/modelador, inicialmente a M-VAVE Blackbox.

Os alvos são **Windows e Linux**. O WSL com WSLg também é um ambiente para
executar a interface e fazer testes rápidos de reprodução. A validação de áudio
e latência é feita separadamente em cada ambiente.

## Estado atual — player com troca automática de IR

Abra uma DI WAV, selecione uma pasta de IRs e escolha um IR: o processamento
e a primeira reprodução começam automaticamente. Clique em outro IR ou use
↑/↓ na lista e ←/→ na janela para trocar. A busca é recursiva. A reprodução usa o dispositivo
padrão do sistema. Após processar, o botão alterna entre Play e Pause.
Pause preserva a posição, Stop volta ao início e Loop pode ser alterado durante
a reprodução. O contador e a barra mostram a posição no resultado processado.
A convolução roda em uma thread de trabalho para manter a janela responsiva.

O seletor de saída lista os dispositivos fornecidos pelo PortAudio. A opção
inicial acompanha a saída padrão do sistema. Trocar o dispositivo preserva a
posição e o estado do player, com uma breve interrupção enquanto o stream é
reaberto. O ganho de saída vai de -24 a 0 dB e não altera o áudio em cache.

Ao trocar o IR, o áudio anterior continua durante o processamento. A nova
seleção assume a posição atual e preserva Pause/Stop. Navegação rápida aplica
apenas a última seleção. O rótulo IR ativo identifica o áudio realmente aplicado.
Trocar a DI ou pasta encerra o áudio atual.

Use **B** ou a opção **Bypass IR** para ouvir a DI sem IR; **Espaço** alterna
Play/Pause. Bypass também funciona sem selecionar um IR. A volta ao IR mantém
a posição e o estado do player. A DI sem IR mantém sua duração original, sem
a cauda da convolução, e recebe a mesma proteção de pico (0,95).

Um cache de sessão retém até 4 resultados ou 128 MiB (o que atingir primeiro),
incluindo bypass. Voltar a um IR reutiliza o resultado se os arquivos não
mudaram. Trocar DI ou pasta limpa o cache. Esse limite não inclui buffers ativos
e temporários do processamento.

Use **F** para alternar favorito e **1..5** para avaliar o IR selecionado. Esses
dados persistem em SQLite e reaparecem após fechar, abrir ou reescanear a pasta.
O banco armazena caminhos e metadados; os arquivos de áudio não são copiados.
Use **0** para limpar a avaliação. A lista mostra favorito e estrelas ao lado
do caminho relativo.

A busca filtra por nome ou caminho dentro da pasta aberta. Também é possível
mostrar somente favoritos e exigir uma avaliação mínima. Aplicar um filtro não
interrompe nem troca o áudio atual. As notas são salvas pelo botão **Salvar
notas**; mudar de item sem salvar descarta a edição ainda não gravada. Enquanto
o editor está em foco, F, B, Espaço, setas e números são texto normal.

**Exportar favoritos…** copia todos os IRs favoritos da pasta escaneada para
uma nova pasta escolhida por você, mesmo que filtros estejam ocultando itens.
Informe a pasta pai e o nome da nova pasta. As subpastas relativas são mantidas,
facilitando copiar o resultado para uma pedaleira. A aplicação recusa sobrescrever
uma pasta existente e também impede exportar para dentro da própria biblioteca,
o que criaria duplicatas no próximo scan.

Esta entrega fecha as funções planejadas da biblioteca do MVP. O próximo passo,
após validação prática, é o polimento técnico: scan assíncrono, persistência de
preferências e decisão sobre crossfade. NAM, ANN, A2, entrada ao vivo e envio à
Blackbox e IR-Box não estão implementados.

## Desenvolvimento no WSL com mise e venv

O `mise.toml` fixa Python 3.12.13 e configura a criação/ativação de `.venv`.
Com o mise instalado, a integração Bash deve estar habilitada no `~/.bashrc`:

```bash
eval "$(mise activate bash)"
```

Na primeira configuração, dentro da pasta do projeto:

```bash
mise trust
mise install
mise run install
mise run test
```

Depois de confiar na configuração e instalar o Python, entrar na pasta em um
shell com mise ativo cria/ativa a `.venv`. A instalação das dependências é
explícita (`mise run install`), não acontece a cada entrada na pasta.
Não é necessário instalar `uv`.

```bash
mise run run
# Ou, com a venv ativa:
audition-manager
python -m pytest
```

## Linux e Arch Linux no WSL

No Arch, instale as dependências nativas e uma fonte antes de abrir a GUI:

```bash
sudo pacman -Syu --needed libxkbcommon libxkbcommon-x11 libxcb xcb-util-cursor mesa fontconfig ttf-dejavu portaudio
fc-cache -f
mise run run
```

O comando `-Syu` também atualiza o sistema. As bibliotecas e fontes ficam no
sistema operacional, fora da venv. PySide6 é instalado pelo pip.

Se a janela abre, mas todos os textos aparecem como quadradinhos, verifique
`fc-list`: uma saída vazia indica ausência de fontes. Para corrigir esse caso
em um sistema já atualizado, basta `sudo pacman -S --needed ttf-dejavu`, seguido
de `fc-cache -f`. Feche e reabra a aplicação. A inicialização verifica se uma
fonte consegue desenhar os textos e acentos antes de criar a janela.

No WSL, a sessão precisa de WSLg (ou um servidor gráfico configurado). Preserve
as variáveis `DISPLAY`, `WAYLAND_DISPLAY` e `PULSE_SERVER` fornecidas pela sessão.
Para listar as saídas de áudio disponíveis:

```bash
mise exec -- python -m sounddevice
```

No Arch com WSLg, o PortAudio usa ALSA e precisa da ponte para PulseAudio:

```bash
sudo pacman -S --needed alsa-plugins pulseaudio-alsa
pactl info
mise exec -- python -m sounddevice
```

Reabra o aplicativo após instalar. `pactl info` deve conectar ao servidor do
WSLg (normalmente com saída `RDPSink`) e sounddevice deve listar uma saída.
`Error querying device -1` significa que o dispositivo padrão não pôde ser
consultado; se a lista está vazia, confira essa ponte. O WSLg já fornece o
servidor PulseAudio: não é necessário iniciar outro servidor dentro do Arch.
Essa configuração é específica de WSLg; Linux nativo deve usar a integração
ALSA correspondente ao servidor de áudio da distribuição.

A reprodução depende de uma saída padrão disponível via PortAudio e da ponte
de áudio do WSLg. Abra uma DI para validar o som: testes automatizados com saída
falsa não validam essa ponte. Em Linux nativo, use a sessão gráfica e de áudio
normal da distribuição. Testes de DSP não exigem Qt nem PortAudio.

## Executar nativamente no Windows

Use Python 3.12+ para Windows e uma cópia do projeto em uma pasta do Windows.
A venv do Linux não pode ser compartilhada com o Windows. Em PowerShell:

```powershell
py -3.12 -m venv .venv-win
.\.venv-win\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv-win\Scripts\audition-manager.exe
.\.venv-win\Scripts\python.exe -m pytest
```

Abra uma DI de até 5 minutos e uma pasta com IRs WAV de até 2 segundos.
Selecione um IR para processar e reproduzir automaticamente. Teste Pause, Stop e Loop.
Arquivos inválidos são ignorados e contabilizados após a leitura do cabeçalho.

## Arquitetura e dependências

- `audio/files.py`: carregamento e validação de WAV; `AudioBuffer` padroniza dados.
- `audio/ir_processor.py`: convolução offline e reamostragem de IR.
- `audio/render_cache.py`: cache LRU limitado e preparação do bypass.
- `audio/transport.py`: estados, cursor e preenchimento de blocos de reprodução.
- `audio/output.py`: stream próprio sounddevice/PortAudio, pausa e liberação.
- `library/scanner.py`: descoberta e leitura de metadados WAV.
- `library/repository.py`: migração e persistência SQLite de metadados do IR.
- `library/exporter.py`: cópia transacional dos favoritos para uma nova pasta.
- `config/settings.py`: caminho do banco conforme Windows/Linux.
- `ui/main_window.py`: janela e coordenação da tarefa de processamento.
- `main.py`: composição da aplicação e logging.

PySide6 fornece a GUI; NumPy representa as amostras; SciPy faz convolução FFT e
reamostragem; soundfile lê WAV; sounddevice reproduz áudio; pytest valida o
núcleo. SQLite da biblioteca padrão persiste a biblioteca local.
Princípios SOLID e Clean Code orientam responsabilidades pequenas, nomes claros,
tipos e dependências isoladas. Interfaces adicionais serão introduzidas quando
houver uma necessidade concreta, sem criar engines fictícias.

## Testes e limitações

```bash
python -m pytest
```

Os testes usam WAVs sintéticos temporários e verificam convolução, canais,
reamostragem, headroom, descoberta e rejeição de arquivos inválidos. O teste de
interface usa Qt offscreen e saída falsa, sem acessar o dispositivo; é marcado
como ignorado se as bibliotecas nativas do Qt não estiverem disponíveis.
Veja o [roteiro manual por plataforma](docs/validacao.md).

O banco fica em `%LOCALAPPDATA%\Audition Manager\library.sqlite3` no Windows e
em `$XDG_DATA_HOME/audition-manager/library.sqlite3` no Linux (ou
`~/.local/share/audition-manager/library.sqlite3`). Para testes isolados, defina
`AUDITION_MANAGER_DATA_DIR` antes de iniciar. O scan é síncrono nesta etapa;
pastas muito grandes podem deixar a janela ocupada enquanto os cabeçalhos são
lidos. Arquivos removidos permanecem no banco para preservar a classificação,
mas não aparecem na lista quando não estão presentes na pasta escaneada.

O processamento carrega DI, IR e resultado na memória. São aceitos mono/estéreo
até 192 kHz, DI até 300 s e IR até 2 s. O IR é reamostrado para a taxa da DI;
IR mono é aplicado a cada canal, DI mono com IR estéreo gera saída estéreo.
A cauda completa da convolução é mantida, inclusive no loop. A posição exibida
representa amostras entregues ao dispositivo e pode adiantar o som pela latência
da saída. A barra é informativa, sem busca por posição. Pause aguarda os buffers
já enviados terminarem; pode haver um pequeno atraso. Picos acima de
0,95 são atenuados: isso evita clipping digital, mas altera o nível relativo
entre alguns IRs. Não há normalização de volume perceptual, crossfade ou
promessa de baixa latência. O dispositivo precisa aceitar a taxa da DI.
O fechamento aguarda o usuário tentar novamente após um processamento ativo.
Dispositivo e ganho ainda não são persistidos: cada execução começa na saída
padrão e em 0 dB. Dispositivos desconectados durante a reprodução podem exigir
selecionar outra saída ou reiniciar o aplicativo.

As dependências usam faixas de versões em `pyproject.toml`; ainda não há lockfile
multiplataforma. Empacotamento e auditoria de licenças de distribuição ficam
para uma etapa própria.

## Documentação e processo

- [Plano e pontos de auditoria](PLAN.md)
- [Prompt original preservado](docs/prompt-inicial.md)
- [Decisões iniciais](docs/decisions/0001-fundacao.md)
- [Linux, WSL e fontes](docs/decisions/0002-linux-wsl-fontes.md)
- [Player com posição e pausa](docs/decisions/0004-player.md)
- [Troca automática e Git](docs/decisions/0005-troca-ir-git.md)
- [Bypass, atalhos e cache](docs/decisions/0006-bypass-cache.md)
- [Biblioteca SQLite](docs/decisions/0007-biblioteca-sqlite.md)
- [Dispositivo e ganho](docs/decisions/0008-dispositivo-ganho.md)
- [Filtros e notas](docs/decisions/0009-filtros-notas.md)
- [Exportação de favoritos](docs/decisions/0010-exportacao-favoritos.md)
- [Validação](docs/validacao.md)

Cada incremento deve registrar decisões, testes e limitações em `docs/`, e
terminar em um ponto de revisão antes de iniciar o próximo incremento.

## Licença

O código do projeto é distribuído sob a [licença MIT](LICENSE).
Dependências, capturas e arquivos de áudio mantêm suas próprias licenças;
nenhum conteúdo de terceiros está incluído em `samples/`.

## Versionamento

Repositório Git local na branch `main`. Os commits registram incrementos
revisáveis; não há remoto configurado nem publicação automática. `.venv`, dados
locais e os áudios de `exemples/` ficam fora do histórico. Os arquivos originais
continuam na pasta para testes locais.

```bash
git log --oneline
git status
```
