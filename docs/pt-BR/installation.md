# Instalação — Português

O projeto requer Python 3.12. O runtime NAM também requer Git, CMake e um
compilador C++ para ser construído a partir do NeuralAmpModelerCore oficial.

## Clonar

```bash
git clone https://github.com/danielfransa/audition_manager.git
cd audition_manager
```

## Linux

### Debian, Ubuntu, Mint e derivados

```bash
sudo apt update
sudo apt install -y git curl cmake g++ libxkbcommon-x11-0 libxcb-cursor0 libgl1 libegl1 fontconfig fonts-dejavu-core libportaudio2 libsndfile1
```

### Fedora e derivados

```bash
sudo dnf install -y git curl cmake gcc-c++ libxkbcommon-x11 xcb-util-cursor mesa-libGL mesa-libEGL fontconfig dejavu-sans-fonts portaudio libsndfile
```

### Arch, Manjaro, EndeavourOS e derivados

```bash
sudo pacman -Syu --needed git curl cmake gcc libxkbcommon libxkbcommon-x11 libxcb xcb-util-cursor mesa fontconfig ttf-dejavu portaudio libsndfile
```

### Usar mise

Depois de [instalar o mise](https://mise.jdx.dev/getting-started.html):

```bash
mise trust
mise install
mise run install
./scripts/build-nam-runtime.sh
mise run run
```

O `mise.toml` instala Python 3.12.13, cria `.venv` e ativa o ambiente ao entrar
na pasta quando a integração do mise com o shell estiver habilitada.

### venv manual

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
./scripts/build-nam-runtime.sh
audition-manager
```

## Windows 10/11

Instale Python 3.12 com o launcher `py`. Para capturas NAM, instale também Git,
CMake e Visual Studio Build Tools com o componente de desenvolvimento C++.

```powershell
git clone https://github.com/danielfransa/audition_manager.git
cd audition_manager
py -3.12 -m venv .venv-win
.\.venv-win\Scripts\python.exe -m pip install --upgrade pip
.\.venv-win\Scripts\python.exe -m pip install -e ".[dev]"
.\scripts\build-nam-runtime.ps1
.\.venv-win\Scripts\audition-manager.exe
```

Para criar o pacote portátil:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\build-windows.ps1
```

O resultado fica em `dist\AuditionManager-Windows-x64.zip`. A geração precisa
ser feita no Windows; o pacote ainda aguarda validação em uma máquina Windows real.

Também é possível abrir **Actions → Windows portable package → Run workflow** no
GitHub. Ao final, baixe o artefato `AuditionManager-Windows-x64`. Artefatos de
desenvolvimento não são uma release assinada e expiram após 14 dias.

## WSL/WSLg com Arch

Além das dependências do Arch, instale a ponte de áudio:

```bash
sudo pacman -S --needed alsa-plugins pulseaudio-alsa
pactl info
mise exec -- python -m sounddevice
```

## Dados locais

| Sistema | Diretório |
| --- | --- |
| Windows | `%LOCALAPPDATA%\Audition Manager\` |
| Linux | `$XDG_DATA_HOME/audition-manager/` ou `~/.local/share/audition-manager/` |

Os arquivos são `library.sqlite3` e `preferences.json`.

## Problemas comuns

- Textos em quadrados: instale DejaVu, execute `fc-cache -f` e reabra o programa.
- Sem dispositivo: execute `python -m sounddevice` e confira PipeWire/PulseAudio/ALSA.
- Runtime NAM ausente: execute o script `build-nam-runtime` do seu sistema.
- Windows fecha imediatamente: execute pela PowerShell para ler a mensagem.

Próximo passo: [guia de uso](usage.md).
