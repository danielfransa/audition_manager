# 0023 — A2 Full/Lite e modelos NAM legados

## Contexto

A extensão `.nam` não identifica uma única arquitetura. A implementação inicial
aceitava somente `SlimmableContainer` A2 e sempre escolhia o submodelo Full.

## Decisão

Para A2, oferecer **Full** e **Lite**. O renderer oficial recebe `--slim 1.0`
para Full e `--slim 0.0` para Lite. Full permanece como padrão; a preferência é
persistida e faz parte da chave de cache.

Aceitar também as arquiteturas registradas no NeuralAmpModelerCore utilizado:
`WaveNet`, `LSTM`, `ConvNet`, `Linear` e `Sequential`. Esses arquivos são enviados
ao renderer sem `--slim`. Arquiteturas desconhecidas são recusadas durante o
scan, antes do processamento.

A biblioteca mostra arquitetura e versão. O seletor Full/Lite é habilitado
somente para A2. A aceitação estrutural não garante que toda versão histórica ou
configuração arbitrária seja compreendida pelo commit fixado do runtime; nesse
caso, o erro retornado pelo NeuralAmpModelerCore é apresentado ao usuário.

## Validação

Uma captura A2 real foi processada nos dois modos: Full em aproximadamente
1,02 s e Lite em 0,25 s para a mesma DI no WSL. Os dois produziram 820.028
amostras mono a 48 kHz. Modelos legados ainda precisam de audição prática com
arquivos reais licenciados para teste.
