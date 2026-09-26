# 0001 — Fundação e primeira fatia vertical

Data: 2026-09-26. Estado: implementada para revisão; aceite nativo pendente.

## Requisitos adicionais do usuário

Além do [prompt original](../prompt-inicial.md), o usuário pediu venv gerenciada
pelo mise instalado no WSL, arquivo TOML com criação automática ao entrar na
pasta, SOLID e Clean Code, incrementos pequenos para auditoria, pasta docs com
histórico das decisões, README com objetivo e licença MIT open source.

## Decisões

1. Python 3.12.13 no mise, já instalado neste ambiente. `_.python.venv` com
   `create = true` cria/ativa `.venv` quando a configuração confiável é carregada.
   O hook do shell é requisito. Dependências são instaladas explicitamente via
   pip; uv não é necessário nesta etapa. Se uv estiver instalado e for usado
   pelo mise, `uv_create_args = ["--seed"]` garante pip na venv criada.
   Windows usa venv separada.
2. Layout `src/` com pacote instalável. Apenas módulos com comportamento real;
   banco, configuração persistente e engines de captura não recebem stubs vazios.
3. SRP: scanner descobre; loader valida; processador transforma; saída reproduz;
   UI coordena. Composição em `main.py`, saída injetada para permitir testes.
   Abstrações de fontes/capturas serão introduzidas com contratos concretos.
4. Convolução FFT offline por eixo de tempo, com cauda completa. IR reamostrado
   para DI; mono pode ser expandido para estéreo. Estéreo usa convolução por
   canal, não uma matriz de convolução true-stereo.
5. Atenuar picos acima de 0,95, sem amplificar material silencioso. A comparação
   absoluta de níveis é limitada por essa política e precisa de revisão no MVP.
6. Limitar DI a 300 s, IR a 2 s, até 192 kHz e 2 canais antes de carregar dados.
   Isso limita, mas não elimina, custo de memória. Sem streaming nesta fatia.
7. Trabalho de leitura/convolução em QThread; resultado entregue por sinal à
   GUI. Operações conflitantes ficam desabilitadas; fechamento é adiado durante
   o trabalho. Busca de diretório ainda é síncrona, adequada a bibliotecas pequenas.
8. sounddevice fica encapsulado e é importado apenas ao acessar a saída. Nesta
   fatia usa `play/stop`; player contínuo futuro usará uma saída com cursor/stream.
9. Loop e Stop já são úteis para o fluxo mínimo. Pause, atalhos, bypass, troca
   sem reiniciar e SQLite pertencem aos próximos incrementos do MVP.
10. Projeto MIT, copyright dos contribuidores. Sem assets externos ou bibliotecas
    pouco conhecidas. Não presumir licença MIT para dependências ou modelos.

## Estrutura atual

```text
mise.toml / pyproject.toml / LICENSE / README.md / PLAN.md
src/audition_manager/
  main.py / __main__.py
  audio/   files.py / ir_processor.py / output.py
  library/ scanner.py
  ui/      main_window.py
tests/
docs/      prompt-inicial.md / decisions/ / validacao.md
samples/   di/ / ir/ / captures/
data/
```

SQLite via stdlib, repositório e migrações serão adicionados no incremento de
metadados. O futuro `CaptureEngine` deverá isolar runtimes sem assumir que NAM,
ANN e A2 compartilham estrutura. O processador offline atual não constitui um
contrato para tempo real; substituição por blocos/C++ exigirá medição e decisão.

## Referências consultadas

- [mise — Python e virtualenv](https://mise.jdx.dev/lang/python.html)
- [SciPy — fftconvolve](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.fftconvolve.html)
- [Qt — QThread](https://doc.qt.io/qtforpython-6/PySide6/QtCore/QThread.html)
- [sounddevice — uso](https://python-sounddevice.readthedocs.io/en/latest/usage.html)

As dependências foram solicitadas no prompt; não foi incluída biblioteca
adicional de runtime. O empacotamento Windows e a revisão de licenças da
redistribuição serão tratados antes de publicar binários.
