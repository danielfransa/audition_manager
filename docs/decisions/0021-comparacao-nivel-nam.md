# 0021 — Ganho e medição para comparação NAM

## Contexto

Capturas podem produzir níveis diferentes. Uma captura mais alta pode parecer
melhor apenas pela diferença de volume, e aumentos de ganho podem causar clipping.

## Decisão

Adicionar ganho NAM de -24 a +12 dB depois da captura e antes do IR. O valor é
persistido e faz parte da chave do cache, portanto cada ajuste produz o áudio
correspondente. O ganho de saída existente continua sendo o volume geral enviado
ao dispositivo.

Um medidor exibe o pico do resultado processado em dBFS, antes do ganho geral de
saída. Todos os caminhos offline mantêm a proteção de pico em 0,95; o caminho
NAM sem IR passa a receber a mesma proteção já usada na convolução.

A interface descreve a cadeia como `DI → NAM (arquivo) → IR (arquivo)` e lista
explicitamente os estágios em bypass.
