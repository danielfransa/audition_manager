# Instalação e execução

O Audition Manager ainda é distribuído pelo código-fonte. Python 3.12 é a versão
fixada para desenvolvimento e teste. Os comandos abaixo instalam a aplicação em
um ambiente virtual, sem alterar os pacotes Python globais do sistema.

## Clonar o repositório

Na página do projeto no GitHub, abra **Code → HTTPS** e copie a URL:

```bash
git clone URL_HTTPS_DESTE_REPOSITORIO
cd audition_manager
```

O repositório local desta fase ainda não possui remoto público configurado; por
isso a documentação não fixa uma URL que poderia apontar para o local errado.

## Linux

É necessário ter uma sessão gráfica, uma fonte, bibliotecas usadas pelo Qt e uma
saída de áudio acessível pelo PortAudio. PipeWire, PulseAudio e ALSA podem servir
como backend conforme a configuração da distribuição.

### Debian, Ubuntu, Linux Mint, Pop!_OS e derivados

```bash
sudo apt update
sudo apt install -y git curl cmake g++ libxkbcommon-x11-0 libxcb-cursor0 libgl1 libegl1 fontconfig fonts-dejavu-core libportaudio2 libsndfile1
```

### Fedora e derivados

```bash
sudo dnf install -y git curl cmake gcc-c++ libxkbcommon-x11 xcb-util-cursor mesa-libGL mesa-libEGL fontconfig dejavu-sans-fonts portaudio libsndfile
```

### Arch Linux, Manjaro, EndeavourOS e derivados

```bash
sudo pacman -Syu --needed git curl cmake gcc libxkbcommon libxkbcommon-x11 libxcb xcb-util-cursor mesa fontconfig ttf-dejavu portaudio libsndfile
```

Esses nomes foram conferidos nos catálogos Debian, Fedora e Arch. Distribuições
antigas podem usar nomes diferentes, especialmente para `libxcb-cursor` e Mesa.

### Opção recomendada: mise

Instale o [mise conforme a documentação oficial](https://mise.jdx.dev/getting-started.html)
e habilite sua integração com o shell. No Bash, normalmente é usada esta linha
no `~/.bashrc`:

```bash
eval "$(mise activate bash)"
```

Dentro do repositório:

```bash
mise trust
mise install
mise run install
./scripts/build-nam-runtime.sh
mise run run
```

O projeto fixa Python 3.12.13. O mise cria e ativa `.venv`; a instalação das
dependências continua explícita no comando `mise run install`.

### Alternativa: venv manual

Com Python 3.12 já instalado pela distribuição ou por outro gerenciador:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e .
audition-manager
```

Para executar os testes, instale o extra de desenvolvimento:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

### Verificar áudio e fontes

```bash
fc-list | head
python -m sounddevice
```

Se os textos aparecerem como quadrados, confirme a instalação da fonte DejaVu,
execute `fc-cache -f` e reabra a aplicação. Se não houver dispositivo de saída,
verifique se a sessão PipeWire/PulseAudio/ALSA da distribuição está ativa.

## Windows 10/11

Instale [Python 3.12 para Windows](https://www.python.org/downloads/windows/)
e marque a opção que instala o launcher `py`. Em PowerShell:

```powershell
git clone URL_HTTPS_DESTE_REPOSITORIO
cd audition_manager
py -3.12 -m venv .venv-win
.\.venv-win\Scripts\python.exe -m pip install --upgrade pip
.\.venv-win\Scripts\python.exe -m pip install -e ".[dev]"
.\.venv-win\Scripts\audition-manager.exe
```

O Windows usa sua própria venv. Não copie `.venv` do Linux ou do WSL.

Para usar capturas NAM pela venv, instale também Git, CMake e o compilador C++
do Visual Studio Build Tools e execute `scripts\build-nam-runtime.ps1`.

### Criar o pacote portátil

Na raiz do projeto:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\build-windows.ps1
```

O script cria `.venv-package`, instala os extras, executa os testes e gera:

```text
dist\AuditionManager\AuditionManager.exe
dist\AuditionManager-Windows-x64.zip
```

Extraia e distribua a pasta completa. O `.exe` depende das DLLs incluídas ao
lado dele. A máquina que executa o ZIP não precisa ter Python instalado. Como o
binário ainda não possui assinatura, o Windows pode mostrar o SmartScreen.

## WSL/WSLg

WSL é útil para desenvolvimento e testes rápidos, mas não substitui a validação
em Windows ou Linux nativo. Preserve `DISPLAY`, `WAYLAND_DISPLAY` e
`PULSE_SERVER` fornecidas pelo WSLg.

No Arch dentro do WSL, além das dependências gerais, a ponte PortAudio para o
servidor PulseAudio do WSLg requer:

```bash
sudo pacman -S --needed alsa-plugins pulseaudio-alsa
pactl info
mise exec -- python -m sounddevice
```

`pactl info` deve alcançar o servidor do WSLg e `sounddevice` deve listar uma
saída. `Error querying device -1` geralmente indica que o PortAudio não encontrou
uma saída padrão acessível.

## Dados locais

O banco e as preferências não ficam dentro do repositório:

| Sistema | Diretório |
| --- | --- |
| Windows | `%LOCALAPPDATA%\Audition Manager\` |
| Linux | `$XDG_DATA_HOME/audition-manager/` ou `~/.local/share/audition-manager/` |

Os arquivos são `library.sqlite3` e `preferences.json`. Para testes isolados,
defina `AUDITION_MANAGER_DATA_DIR` antes de iniciar a aplicação.

## Solução rápida de problemas

- **Janela não abre no Linux:** execute pelo terminal e confira a biblioteca
  mencionada na mensagem; reinstale os pacotes Qt/XKB/XCB da sua distribuição.
- **Textos em quadrados:** instale DejaVu e execute `fc-cache -f`.
- **Sem dispositivo de áudio:** execute `python -m sounddevice` e corrija o
  backend PipeWire/PulseAudio/ALSA antes de testar o player.
- **Windows abre e fecha imediatamente:** execute o programa pelo PowerShell para
  observar a mensagem ou teste primeiro pela venv antes do pacote portátil.
