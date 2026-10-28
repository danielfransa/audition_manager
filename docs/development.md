# Desenvolvimento e arquitetura

## Ambiente

O `mise.toml` fixa Python 3.12.13, cria `.venv` e oferece três tarefas:

```bash
mise run install
mise run test
mise run run
```

Também é possível trabalhar com uma venv manual conforme
[`installation.md`](installation.md). Dependências usam faixas de versão no
`pyproject.toml`; ainda não existe lockfile multiplataforma.

## Estrutura

- `audio/files.py`: carregamento e validação de WAV.
- `audio/ir_processor.py`: convolução offline e reamostragem.
- `audio/render_cache.py`: cache LRU e preparação do bypass.
- `audio/transport.py`: estados, cursor, blocos e crossfade.
- `audio/output.py`: stream sounddevice/PortAudio.
- `library/scanner.py`: descoberta e metadados WAV.
- `library/repository.py`: migrações e persistência SQLite para IRs e capturas.
- `library/exporter.py`: exportação transacional dos favoritos.
- `config/settings.py`: caminhos de dados por sistema.
- `config/preferences.py`: preferências JSON com escrita atômica.
- `ui/main_window.py`: janela e coordenação de workers.
- `main.py`: composição da aplicação e logging.

PySide6 fornece a interface; NumPy representa amostras; SciPy processa convolução
e reamostragem; soundfile lê WAV; sounddevice envia áudio; SQLite persiste a
biblioteca. Responsabilidades e dependências são separadas para seguir SOLID e
Clean Code sem introduzir abstrações antes de uma necessidade concreta.

## Testes

```bash
python -m pytest
python -m compileall -q src tests
git diff --check
```

Os testes criam WAVs temporários e usam saída de áudio falsa. Eles verificam DSP,
scanner, banco, exportação, preferências, transporte e Qt offscreen, mas não
confirmam driver, som audível ou latência do hardware.

## Limites técnicos atuais

- WAV mono/estéreo até 192 kHz, DI até 300 s e IR até 2 s.
- Todo o DI, IR e resultado são mantidos em memória durante o processamento.
- IRs são reamostrados para a DI; a cauda completa entra no resultado e no Loop.
- Picos acima de 0,95 são atenuados, sem normalização perceptual.
- O ganho NAM ocorre após a captura e antes do IR; o medidor mostra o pico do
  resultado antes do ganho geral de saída.
- A posição representa amostras entregues ao dispositivo e pode adiantar o som
  pela latência do buffer. A barra ainda não permite buscar uma posição.
- Crossfade exige a mesma quantidade de canais; mono/estéreo reabre o stream.
- Scan é assíncrono, mas a enumeração inicial ocorre antes da contagem. O
  cancelamento acontece entre arquivos.
- Arquivos removidos deixam de aparecer, mas seus metadados permanecem no banco.

## Processo e versionamento

Cada incremento registra sua decisão em `docs/decisions/`, atualiza o plano e o
roteiro de validação, executa verificações apropriadas e termina em um commit
revisável. O repositório local usa a branch `develop` durante os incrementos;
ambientes virtuais, dados e áudios pessoais ficam fora do Git.

O histórico detalhado de WSL/WSLg, dependências, problemas de fontes e áudio está
em [`validacao.md`](validacao.md) e nas decisões 0002 e 0003. O estado vigente
está em [`status.md`](status.md).
