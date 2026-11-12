# 0032 — Equalização opcional pelo loudness NAM

## Contexto

O loudness persistido no incremento anterior permite reduzir o viés de volume
sem medir novamente capturas que já fornecem esse dado. A mudança não pode
alterar silenciosamente o comportamento existente nem substituir o ganho manual.

## Decisão

Adicionar o checkbox persistente **Igualar volume automaticamente**, desmarcado
por padrão. Quando ativo e a captura informa `metadata.loudness`, calcular:

`compensação = -18 dB - loudness da captura`

Limitar a compensação entre -24 e +12 dB, aplicá-la antes do ganho NAM manual e
incluí-la na chave do cache. Mostrar o valor aplicado na interface. Quando o dado
estiver ausente, aplicar 0 dB e informar que a função está indisponível.

## Consequências

- Desmarcar o checkbox restaura o nível original, além do ganho manual escolhido.
- O ganho manual continua independente e pode refinar a comparação.
- A proteção de pico existente continua sendo a última barreira da cadeia.
- IRs e NAMs sem loudness aguardam a medição e o cache do próximo incremento.
