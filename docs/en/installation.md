# Installation — English

The project requires Python 3.12. The NAM runtime also requires Git, CMake, and a
C++ compiler because it is built from the official NeuralAmpModelerCore source.

## Clone

```bash
git clone https://github.com/danielfransa/audition_manager.git
cd audition_manager
```

## Linux

### Debian, Ubuntu, Mint, and derivatives

```bash
sudo apt update
sudo apt install -y git curl cmake g++ libxkbcommon-x11-0 libxcb-cursor0 libgl1 libegl1 fontconfig fonts-dejavu-core libportaudio2 libsndfile1
```

### Fedora and derivatives

```bash
sudo dnf install -y git curl cmake gcc-c++ libxkbcommon-x11 xcb-util-cursor mesa-libGL mesa-libEGL fontconfig dejavu-sans-fonts portaudio libsndfile
```

### Arch, Manjaro, EndeavourOS, and derivatives

```bash
sudo pacman -Syu --needed git curl cmake gcc libxkbcommon libxkbcommon-x11 libxcb xcb-util-cursor mesa fontconfig ttf-dejavu portaudio libsndfile
```

### Using mise

After [installing mise](https://mise.jdx.dev/getting-started.html):

```bash
mise trust
mise install
mise run install
./scripts/build-nam-runtime.sh
mise run run
```

`mise.toml` installs Python 3.12.13 and creates `.venv`.

### Manual venv

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
./scripts/build-nam-runtime.sh
audition-manager
```

## Windows 10/11

Install Python 3.12 with the `py` launcher. NAM support also requires Git, CMake,
and Visual Studio Build Tools with the C++ development component.

```powershell
git clone https://github.com/danielfransa/audition_manager.git
cd audition_manager
py -3.12 -m venv .venv-win
.\.venv-win\Scripts\python.exe -m pip install --upgrade pip
.\.venv-win\Scripts\python.exe -m pip install -e ".[dev]"
.\scripts\build-nam-runtime.ps1
.\.venv-win\Scripts\audition-manager.exe
```

Build the portable package with:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\build-windows.ps1
```

The result is `dist\AuditionManager-Windows-x64.zip`. It must be built on
Windows and still requires validation on a real Windows machine.

Alternatively, open **Actions → Windows portable package → Run workflow** on
GitHub, then download the `AuditionManager-Windows-x64` artifact. Development
artifacts are not signed releases and expire after 14 days.

## Arch on WSL/WSLg

Install the audio bridge in addition to the Arch packages:

```bash
sudo pacman -S --needed alsa-plugins pulseaudio-alsa
pactl info
mise exec -- python -m sounddevice
```

## Local data

| System | Directory |
| --- | --- |
| Windows | `%LOCALAPPDATA%\Audition Manager\` |
| Linux | `$XDG_DATA_HOME/audition-manager/` or `~/.local/share/audition-manager/` |

The files are `library.sqlite3` and `preferences.json`.

## Common issues

- Square glyphs: install DejaVu, run `fc-cache -f`, and restart the application.
- No output device: run `python -m sounddevice` and check PipeWire/PulseAudio/ALSA.
- Missing NAM runtime: run the `build-nam-runtime` script for your system.
- Windows closes immediately: launch it from PowerShell to read the error.

Next: [user guide](usage.md).
