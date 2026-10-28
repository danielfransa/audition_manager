# Audition Manager

Aplicação desktop open source para guitarristas ouvirem, compararem e organizarem
Impulse Responses antes de copiá-los para pedaleiras e modeladores.

O projeto busca reunir em um único fluxo a audição de IRs, a futura comparação
de capturas de amplificadores **NAM A2** e a preparação de bibliotecas para
equipamentos como M-VAVE BlackBox e IR-Box. Windows e Linux são os sistemas alvo.

> **Estado do projeto:** o player e a biblioteca de IRs estão funcionais e têm
> 76 testes automatizados. A reprodução offline de NAM A2 está em validação;
> transferência direta para pedaleiras e o
> instalador ainda estão em desenvolvimento. Consulte o [status completo](docs/status.md).

## O que já funciona

- Seleção de uma DI WAV e scan recursivo de pastas de IRs; o seletor exibe os
  arquivos WAV antes de confirmar a pasta.
- Processamento e reprodução automática ao selecionar ou trocar um IR.
- Play, Pause, Stop, Loop, bypass, posição e crossfade curto entre IRs.
- Navegação com mouse, teclado e setas, sem bloquear a interface.
- Busca, filtros, favoritos, estrelas clicáveis, notas e persistência em SQLite.
- Seleção do dispositivo de áudio e ganho de saída de -24 a 0 dB.
- Exportação dos IRs favoritos para uma nova pasta, preservando subpastas.
- Restauração da última DI, biblioteca, dispositivo, ganho, Loop e destino.
- Cadeia offline **DI → captura NAM A2 → IR**, com troca automática do IR.
- Biblioteca NAM com busca, filtros, favoritos, estrelas, notas e restauração da
  última pasta e captura selecionada.

## Instalação rápida

Ainda não há binários publicados em Releases. Para testar agora, clone o código
e execute a aplicação com Python 3.12. Na página do GitHub, abra **Code → HTTPS**,
copie a URL e use:

```bash
git clone URL_HTTPS_DESTE_REPOSITORIO
cd audition_manager
```

### Linux com mise

Instale primeiro as bibliotecas nativas correspondentes à sua distribuição.

**Debian, Ubuntu, Mint e derivados:**

```bash
sudo apt update
sudo apt install -y git curl libxkbcommon-x11-0 libxcb-cursor0 libgl1 libegl1 fontconfig fonts-dejavu-core libportaudio2 libsndfile1
```

**Fedora e derivados:**

```bash
sudo dnf install -y git curl libxkbcommon-x11 xcb-util-cursor mesa-libGL mesa-libEGL fontconfig dejavu-sans-fonts portaudio libsndfile
```

**Arch, Manjaro, EndeavourOS e derivados:**

```bash
sudo pacman -Syu --needed git curl libxkbcommon libxkbcommon-x11 libxcb xcb-util-cursor mesa fontconfig ttf-dejavu portaudio libsndfile
```

Depois de [instalar e ativar o mise](https://mise.jdx.dev/getting-started.html):

```bash
mise trust
mise install
mise run install
./scripts/build-nam-runtime.sh
mise run run
```

O `mise.toml` instala Python 3.12.13 e cria a `.venv` do projeto. Para usar uma
venv manual ou resolver problemas de áudio/Qt, veja a
[instalação detalhada](docs/installation.md).

### Windows 10/11

Instale [Python 3.12 para Windows](https://www.python.org/downloads/windows/)
com o launcher `py`, clone o repositório e abra PowerShell na pasta do projeto:

```powershell
py -3.12 -m venv .venv-win
.\.venv-win\Scripts\python.exe -m pip install -e "."
.\.venv-win\Scripts\audition-manager.exe
```

Também existe um script que executa os testes e produz um pacote portátil:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\build-windows.ps1
```

O resultado fica em `dist\AuditionManager-Windows-x64.zip`. O script também
compila o runtime NAM e requer CMake, Git e o compilador C++ do Visual Studio
Build Tools. Extraia o ZIP
inteiro antes de abrir `AuditionManager.exe`; um instalador ainda não é necessário
para testar. O build precisa ocorrer no Windows, pois PyInstaller não gera o
executável Windows oficialmente a partir do Linux/WSL.

## Primeiro teste

O repositório inclui [duas DIs e quatro IRs de exemplo](samples/README.md),
portanto é possível testar sem procurar outros áudios:

1. Em **Abrir DI WAV**, abra `samples/di/clean_guitar.wav`.
2. Opcionalmente, escolha `samples/captures` e selecione uma captura `.nam`.
3. Em **Selecionar pasta de IRs**, escolha `samples/ir`.
4. Clique em um IR para processar e reproduzir automaticamente.
5. Troque de IR com o mouse ou ←/→ e ajuste Loop, bypass, saída e ganho.
6. Clique nas estrelas para avaliar e marque seus favoritos.
7. Use **Exportar favoritos…** para preparar uma pasta para sua pedaleira.

Atalhos principais: `Espaço` para Play/Pause, `B` para bypass do IR, `N` para
bypass da captura NAM, `F` para favorito, `1–5` para avaliação e `0` para
limpar a nota. Use `Ctrl+←/→` para navegar entre capturas NAM e **Sem captura**
para removê-la da cadeia sem fechar a biblioteca.

## Limites atuais

- São aceitos WAVs mono/estéreo de até 192 kHz, DI de até 5 minutos e IR de até
  2 segundos. O processamento é offline e mantém a cauda da convolução.
- Capturas NAM A2 `SlimmableContainer` são processadas offline a 48 kHz pelo
  NeuralAmpModelerCore. Outras arquiteturas NAM ainda não são aceitas.
- AM4DATA e transferência direta para BlackBox/IR-Box ainda não estão implementados.
- O pacote Windows portátil ainda precisa de validação em Windows real.
- A aplicação foi validada no WSL/WSLg; Linux nativo continua no roteiro de teste.

## Documentação

- [Instalação detalhada — Linux, Windows e WSL](docs/installation.md)
- [Status atual e pendências](docs/status.md)
- [Plano de execução](PLAN.md)
- [Desenvolvimento, arquitetura e dados locais](docs/development.md)
- [Validação automática e roteiros manuais](docs/validacao.md)
- [Decisões técnicas](docs/decisions/)
- [Prompt que iniciou o projeto](docs/prompt-inicial.md)

## Licença

O Audition Manager é distribuído sob a [licença MIT](LICENSE). Dependências,
capturas e arquivos de áudio, incluindo `samples/`, mantêm suas próprias
licenças e condições de redistribuição.
