# Comparação justa de volume

Este documento define como o Audition Manager reduzirá o viés de volume ao
comparar capturas NAM e IRs. “Nivelar volume” significa aplicar ganho; não é uma
equalização de graves, médios ou agudos.

## Estado atual

A aplicação já:

- lê `metadata.loudness`, `input_level_dbu` e `output_level_dbu` dos NAMs;
- oferece o checkbox **Igualar volume automaticamente**, desmarcado por padrão;
- usa o loudness do NAM para aproximá-lo do alvo de -18 dB;
- limita a compensação entre -24 e +12 dB;
- mantém o ganho NAM manual separado e a proteção de pico ativa.

Essa etapa melhora a comparação entre capturas com metadados compatíveis, mas
não considera a mudança de volume provocada pelo IR nem o conteúdo específico da
DI. Portanto, ela não é a normalização final.

## O que é LUFS

LUFS significa *Loudness Units relative to Full Scale*. Diferentemente do pico
dBFS, que observa apenas a maior amostra, LUFS estima quão alto um sinal é
percebido ao longo do tempo. Dois sons podem atingir o mesmo pico e ainda parecer
ter volumes muito diferentes por causa da duração, densidade e distribuição de
frequências.

A medição integrada usada aqui considera todo o loop de DI processado. O
algoritmo BS.1770 aplica ponderação de frequência (*K-weighting*) e combina a
energia dos canais. O gating descarta trechos muito silenciosos da média, evitando
que pausas longas façam uma captura parecer artificialmente mais baixa.

Termos importantes:

- **dBFS de pico:** maior amplitude digital; é usado para evitar clipping, não
  para decidir se dois sons parecem igualmente altos.
- **RMS:** energia média simples; é útil, mas não inclui a ponderação e o gating
  usados na estimativa perceptiva escolhida.
- **LUFS integrado:** estimativa de loudness durante o programa/loop completo;
  é a medida principal do Audition Manager.
- **LU:** diferença relativa de loudness. Uma correção de `+3 dB` equivale, para
  este controle de ganho, a elevar o resultado medido em aproximadamente `3 LU`.

## Por que -18 LUFS

`-18 LUFS` é o alvo interno de comparação do projeto, não a recomendação de
distribuição da EBU R128, cujo contexto principal é broadcast. O alvo foi mantido
próximo da convenção de normalização usada pelo ecossistema NAM e oferece margem
antes de 0 dBFS para material de guitarra com transientes.

O valor do alvo não escolhe qual timbre é melhor: ele apenas define o ponto comum
de reprodução. A compensação é calculada por:

```text
compensação em dB = -18 LUFS - loudness integrado medido
```

Exemplo: uma cadeia medida em `-12 LUFS` recebe `-6 dB`; uma cadeia em
`-22 LUFS` recebe `+4 dB`. A correção é limitada entre `-24` e `+12 dB`. O ganho
manual é aplicado separadamente, e o checkbox permite ouvir o nível original.

## Medição implementada para a próxima alpha

A aplicação agora mede a saída real da cadeia selecionada:

```text
DI de referência → NAM opcional → IR opcional → medição → compensação → proteção de pico
```

1. Processa a cadeia sem a compensação automática e antes da proteção final de
   pico.
2. Mede loudness integrado com `pyloudnorm`, segundo ITU-R BS.1770, incluindo
   gating para que pausas da DI não reduzam artificialmente o valor.
3. Calcula a diferença para o alvo de -18 LUFS.
4. Limita a correção entre -24 e +12 dB.
5. Aplica a correção, depois o ganho manual escolhido pelo usuário e, por fim,
   a proteção contra clipping.
6. Mostra método, loudness medido e correção calculada.

Pico não é usado como medida principal: sinais com o mesmo pico podem ter
volumes percebidos muito diferentes. Não há fallback RMS nesta versão. Áudio
vazio, silencioso, curto demais ou com resultado não finito usa o metadado NAM
quando disponível; caso contrário, recebe 0 dB. Os dois casos são identificados
e armazenados para evitar repetição.

## Cache e SQLite

Uma medição vale apenas para a cadeia que a produziu. O registro será associado
a:

- identidade da DI: caminho, tamanho e datas de modificação;
- identidade da captura NAM, quando usada;
- identidade do IR, quando usado;
- modo A2 Full/Lite;
- versão do algoritmo e alvo de loudness.

Alterar qualquer item invalida a medição. Assim, não reutilizaremos em outra DI
uma compensação calculada com conteúdo diferente nem combinaremos por engano a
medição de um NAM com outro IR.

## Comportamento da interface

- Checkbox desligado: nível original, ganho manual e proteção de pico.
- Checkbox ligado com medição válida: usar a medição da cadeia completa.
- Enquanto ainda não houver medição completa, o metadado NAM pode servir como
  estimativa identificada, nunca como medição do IR.
- Sem metadado ou medição válida: manter 0 dB e explicar o motivo.
- Sempre permitir desligar o nivelamento para ouvir diferenças reais de saída.

## Critérios de aceite

- Trocar apenas o volume, sem modificar o timbre.
- Repetir a mesma cadeia e obter o mesmo valor dentro da tolerância definida.
- Não recalcular enquanto todas as identidades do cache forem iguais.
- Recalcular após modificar DI, NAM, IR, modo ou versão do algoritmo.
- Não confundir proteção de pico com loudness medido.
- Cobrir NAM com e sem metadado, somente IR, NAM sem IR e cadeia NAM + IR.

## Referências usadas

- [ITU-R BS.1770](https://www.itu.int/rec/R-REC-BS.1770/en): algoritmo de
  loudness e referência para ponderação, canais e gating.
- [EBU R128](https://tech.ebu.ch/publications/r128): uso de loudness integrado e
  gating para normalização; o alvo broadcast não é copiado como alvo do app.
- [pyloudnorm](https://github.com/csteinmetz1/pyloudnorm): implementação MIT de
  BS.1770 usada pelo projeto.
- [Especificação do arquivo NAM](https://github.com/sdatkinson/neural-amp-modeler/blob/main/docs/source/model-file.rst):
  campos opcionais de loudness e calibração.
- [Plugin oficial NeuralAmpModeler](https://github.com/sdatkinson/NeuralAmpModelerPlugin/blob/main/NeuralAmpModeler/NeuralAmpModeler.cpp):
  referência do uso do loudness do modelo no ecossistema NAM.
