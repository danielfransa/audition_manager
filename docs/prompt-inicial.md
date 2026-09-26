Quero iniciar um projeto chamado **Audition Manager**, uma aplicação desktop para Windows destinada a guitarristas testarem rapidamente capturas de amplificadores e Impulse Responses (IRs) antes de transferi-los para uma pedaleira/modelador, inicialmente pensando na M-VAVE Blackbox.

Estou desenvolvendo dentro do **WSL**, mas o aplicativo final deve ser executado **nativamente no Windows**.

O objetivo principal é resolver este problema:

Tenho muitas capturas de amplificadores e IRs. Atualmente preciso transferir os arquivos para a pedaleira para descobrir se gosto deles. Quero poder testar esses arquivos diretamente no computador, usando:

1. Uma faixa de guitarra DI previamente gravada, em loop.
2. Entrada de guitarra ao vivo por uma interface de áudio.
3. Troca rápida entre capturas.
4. Troca rápida entre IRs.
5. Sistema de favoritos e classificação.
6. Posteriormente, possibilidade de enviar/exportar os arquivos selecionados para a Blackbox.

## Tecnologias iniciais

Quero começar com:

* Python 3.12+
* PySide6 para GUI
* NumPy
* SciPy
* soundfile
* sounddevice
* SQLite para biblioteca/favoritos/configurações

Não quero começar com C++ neste momento.

Porém, organize o projeto de maneira que componentes de processamento de áudio possam futuramente ser substituídos por implementações em C++/JUCE caso Python não forneça performance suficiente para processamento em tempo real.

## Sistemas

O desenvolvimento está sendo feito dentro do WSL.

Entretanto:

* o código deve ser multiplataforma quando razoável;
* o principal target é Windows;
* áudio de baixa latência deve ser pensado para execução nativa no Windows;
* futuramente quero estudar suporte a ASIO;
* não considere áudio dentro do WSL como requisito do aplicativo;
* WSL está sendo usado principalmente como ambiente de desenvolvimento, Git, Codex e organização do projeto.

## Capturas de amplificadores

Quero eventualmente suportar diferentes tipos de captura/modelo, como:

* Neural Amp Modeler / NAM
* formatos relacionados a M-VAVE ANN
* formatos como A2 caso sejam encontrados entre minhas capturas
* outros formatos compatíveis que venham a surgir

IMPORTANTE:

Não assuma que NAM, ANN ou A2 possuem a mesma estrutura.

Não invente implementações de formatos proprietários.

Crie uma abstração de `CaptureEngine` que permita diferentes engines.

Algo conceitualmente semelhante a:

```python
class CaptureEngine(ABC):
    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        ...

    @abstractmethod
    def load(self, file_path: Path) -> None:
        ...

    @abstractmethod
    def process(self, audio: np.ndarray) -> np.ndarray:
        ...

    @abstractmethod
    def unload(self) -> None:
        ...
```

E implementações futuras como:

```text
NamCaptureEngine
AnnCaptureEngine
A2CaptureEngine
```

Por enquanto, se não existir uma forma confiável de executar determinado formato, apenas detecte/classifique o arquivo e deixe a engine marcada como ainda não implementada.

Não faça engenharia reversa especulativa.

## Pipeline de áudio desejado

A arquitetura conceitual deve ser:

```text
                  ┌── DI WAV/File
                  │
AudioSource ──────┤
                  │
                  └── Live Guitar Input
                           │
                           ▼
                    Capture Engine
                           │
                           ▼
                       IR Engine
                           │
                           ▼
                      Output Gain
                           │
                           ▼
                     Audio Output
```

Quero que os componentes sejam independentes.

Por exemplo:

```text
AudioSource
CaptureProcessor
IRProcessor
AudioEngine
AudioOutput
```

Isso deve permitir testar:

```text
DI → Capture → IR → Output
```

ou:

```text
DI → Bypass Capture → IR → Output
```

ou futuramente:

```text
Guitar Input → Capture → IR → Interface Output
```

## ETAPA 1 — MVP

Não tente implementar todo o projeto de uma vez.

Na primeira etapa quero apenas:

### Biblioteca de IRs

Permitir selecionar uma pasta contendo arquivos `.wav`.

Escanear recursivamente:

```text
irs/
    Mesa/
        V30_SM57.wav
        V30_R121.wav

    Marshall/
        Greenback_SM57.wav
```

Mostrar os arquivos encontrados na interface.

### DI Player

Permitir escolher um arquivo WAV contendo guitarra DI.

Ter:

* Play
* Pause
* Stop
* Loop

O objetivo principal é deixar uma DI tocando em loop enquanto navego pelos IRs.

### Processamento de IR

Implementar convolução do áudio DI com o IR.

Considere eficiência.

Para processamento offline ou blocos maiores podemos utilizar FFT convolution.

Estruture a implementação para futuramente suportar convolução em tempo real usando processamento em blocos/partitioned convolution.

Não faça uma implementação excessivamente complexa no MVP.

### Troca de IR

Quero poder trocar rapidamente entre IRs.

Atalhos:

```text
LEFT        IR anterior
RIGHT       próximo IR

SPACE       play/pause

B           bypass IR

F           favorito

1..5        rating
```

Quando trocar de IR, não quero ter que reiniciar manualmente a música.

A DI deve continuar tocando.

Se possível, evite clicks/pops nas trocas utilizando posteriormente um pequeno crossfade, mas isso não precisa bloquear o primeiro MVP.

## Interface inicial

Quero algo simples.

Exemplo conceitual:

```text
┌────────────────────────────────────────────────────────────┐
│                     AUDITION MANAGER                       │
├────────────────────────────────────────────────────────────┤
│                                                            │
│ DI                                                         │
│ ┌───────────────────────────────────────────────────────┐ │
│ │ guitar_test.wav                                       │ │
│ └───────────────────────────────────────────────────────┘ │
│                                                            │
│ [ Play ] [ Stop ] [ Loop ✓ ]                              │
│                                                            │
├──────────────────────────┬─────────────────────────────────┤
│ CAPTURES                 │ IRs                             │
│                          │                                 │
│ Future                   │ Mesa/V30_SM57.wav               │
│ NAM support              │ Mesa/V30_R121.wav               │
│ ANN support              │ Marshall/Greenback.wav          │
│ A2 support               │                                 │
│                          │                                 │
├──────────────────────────┴─────────────────────────────────┤
│                                                            │
│ Current IR: Mesa / V30 SM57                               │
│                                                            │
│ ★ Favorite                                                 │
│ Rating: ★★★★☆                                             │
│                                                            │
│ [ BYPASS IR ]                                              │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

Não se preocupe ainda em deixar a interface bonita.

Priorize:

* arquitetura;
* funcionamento;
* separação de responsabilidades;
* testes;
* facilidade de evolução.

## Biblioteca

Quero armazenar metadados localmente em SQLite.

Por exemplo:

```text
ImpulseResponse
- id
- path
- name
- sample_rate
- channels
- favorite
- rating
- notes
- created_at
```

Posteriormente teremos algo semelhante para:

```text
Capture
```

Não copie os arquivos para o banco.

Armazene apenas metadados e caminhos.

## Estrutura desejada

Não precisa seguir exatamente, mas quero algo próximo de:

```text
audition_manager/
│
├── README.md
├── pyproject.toml
├── .gitignore
│
├── src/
│   └── audition_manager/
│       │
│       ├── main.py
│       │
│       ├── audio/
│       │   ├── engine.py
│       │   ├── sources.py
│       │   ├── ir_processor.py
│       │   └── capture/
│       │       ├── base.py
│       │       ├── nam.py
│       │       ├── ann.py
│       │       └── a2.py
│       │
│       ├── library/
│       │   ├── scanner.py
│       │   ├── models.py
│       │   └── repository.py
│       │
│       ├── ui/
│       │   ├── main_window.py
│       │   ├── ir_browser.py
│       │   └── capture_browser.py
│       │
│       ├── database/
│       │   ├── connection.py
│       │   └── migrations.py
│       │
│       └── config/
│           └── settings.py
│
├── tests/
│
├── samples/
│   ├── di/
│   ├── ir/
│   └── captures/
│
└── data/
```

Evite overengineering.

A estrutura pode ser simplificada se houver um motivo técnico claro.

## ETAPA 2 — Capturas NAM

Depois que o MVP de IR estiver funcionando, quero investigar integração com Neural Amp Modeler.

Objetivo:

```text
DI
 ↓
NAM
 ↓
IR
 ↓
Output
```

Antes de implementar, pesquise qual é atualmente a forma adequada de executar modelos `.nam` programaticamente.

Não invente parser para `.nam`.

Se existir biblioteca/runtime oficial ou open source apropriado, documente as alternativas.

A engine NAM deve respeitar a interface `CaptureEngine`.

## ETAPA 3 — Live Input

Depois:

```text
Guitar
 ↓
Audio Interface
 ↓
Capture
 ↓
IR
 ↓
Audio Interface
```

Precisaremos estudar:

* WASAPI
* ASIO
* buffer size
* sample rate
* latency
* callback realtime
* evitar alocações dentro do callback
* thread safety
* troca de modelo sem interromper áudio

Meta futura aproximada:

```text
48 kHz
64 / 128 samples
```

Mas não otimize prematuramente.

## ETAPA 4 — ANN / Blackbox

Posteriormente quero investigar os formatos utilizados pela M-VAVE Blackbox.

Isso deve ser uma etapa separada.

Quero analisar:

* formatos ANN utilizados pela Blackbox;
* formatos A2 se aplicável;
* ferramentas open-source existentes;
* possibilidade de conversão;
* possibilidade de comunicação USB/MIDI/SysEx com a Blackbox;
* gerenciamento de capturas;
* gerenciamento de IRs.

Não tente implementar isso agora.

Apenas mantenha arquitetura preparada.

## ETAPA 5 — Workflow ideal

No futuro quero conseguir fazer algo assim:

```text
Abrir pasta com:

500 captures
300 IRs

        ↓

carregar uma DI

        ↓

testar

Capture anterior/próxima
IR anterior/próximo

        ↓

F = favorito

1..5 = rating

        ↓

filtrar

★★★★★
★★★★
Favoritos

        ↓

selecionar melhores

        ↓

Export / Send to Blackbox
```

## Requisitos de código

Quero:

* type hints;
* dataclasses quando apropriado;
* pathlib em vez de strings de path;
* logging;
* tratamento claro de erros;
* código modular;
* funções pequenas;
* classes apenas onde fizer sentido;
* pytest;
* evitar dependências desnecessárias;
* evitar abstrações prematuras.

Use nomes de classes, métodos e variáveis em inglês.

Comentários também podem ficar em inglês.

README deve explicar claramente como executar o projeto.

## Ambiente Python

Prefiro utilizar ambiente virtual isolado.

Pode utilizar `uv` se for adequado ao projeto.

Caso utilize, documente comandos como:

```bash
uv sync
uv run audition-manager
uv run pytest
```

O projeto deve utilizar `pyproject.toml`.

## IMPORTANTE SOBRE O PROCESSO

Não quero que você saia implementando todas as etapas agora.

Primeiro:

1. Analise estes requisitos.
2. Proponha a arquitetura inicial.
3. Mostre a estrutura de diretórios proposta.
4. Liste as principais dependências.
5. Identifique riscos técnicos.
6. Separe claramente o que será MVP do que será futuro.
7. Crie um arquivo `PLAN.md` com as etapas do projeto.
8. Crie um `README.md` inicial.
9. Inicialize o projeto Python.
10. Implemente somente a primeira vertical slice mínima.

A primeira vertical slice deve conseguir:

```text
iniciar aplicação
      ↓
abrir uma DI WAV
      ↓
selecionar diretório de IR
      ↓
listar IRs
      ↓
selecionar um IR
      ↓
processar DI + IR
      ↓
reproduzir resultado
```

Depois disso, pare.

Não avance automaticamente para NAM, ANN, A2 ou live input.

Ao terminar esta primeira etapa, me apresente:

* arquivos criados;
* decisões arquiteturais;
* como executar;
* como testar;
* limitações atuais;
* próximos passos sugeridos.

Antes de adicionar qualquer biblioteca pouco conhecida, verifique sua manutenção, licença e adequação.

O foco do projeto é construir incrementalmente uma ferramenta realmente utilizável, e não apenas uma demonstração técnica.
