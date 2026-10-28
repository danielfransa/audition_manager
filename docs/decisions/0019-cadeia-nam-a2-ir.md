# 0019 — Cadeia offline NAM A2 com IR

## Contexto

As capturas adicionadas para teste são arquivos `.nam` versão 0.7.0, arquitetura
`SlimmableContainer`, com dois submodelos WaveNet e taxa de 48 kHz. Elas modelam
o amplificador sem gabinete e precisam ser combinadas com um IR.

## Decisão

Usar o renderer do NeuralAmpModelerCore oficial, fixado no commit
`0b3d3c97b0859a3a8c92a8628c4dd89a25eb5842`, em um processo nativo separado.
A aplicação valida o container, converte a DI para mono/48 kHz, executa a captura
e convolui o resultado com o IR: `DI → NAM → IR`.

O cache inclui DI, captura e IR nas identidades, evitando reutilizar áudio quando
qualquer arquivo mudar. O modo somente com IR permanece disponível. Com uma
captura selecionada, o bypass do IR produz `DI → NAM`, útil para comparação.
Outras arquiteturas NAM são rejeitadas nesta etapa.

## Distribuição

Scripts reproduzíveis compilam o runtime no Linux e Windows. O pacote Windows
inclui `nam-render.exe`. As capturas de terceiros não são incluídas no commit
até que seus termos de redistribuição sejam conhecidos.

NeuralAmpModelerCore usa licença MIT. Eigen, nlohmann/json e AudioDSPTools
mantêm suas próprias licenças, que deverão ser revisadas antes de publicar
binários oficiais.
