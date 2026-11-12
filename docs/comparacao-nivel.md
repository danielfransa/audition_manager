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

## Medição planejada para a próxima alpha

O próximo incremento medirá a saída real da cadeia selecionada:

```text
DI de referência → NAM opcional → IR opcional → medição → compensação → proteção de pico
```

1. Processar a cadeia sem a compensação automática e antes da proteção final de
   pico.
2. Medir loudness integrado segundo a família ITU-R BS.1770/EBU R128, incluindo
   gating para que pausas da DI não reduzam artificialmente o valor.
3. Calcular a diferença para o alvo de -18 LUFS.
4. Limitar a correção entre -24 e +12 dB.
5. Aplicar a correção, depois o ganho manual escolhido pelo usuário e, por fim,
   a proteção contra clipping.
6. Mostrar método, loudness medido, correção calculada e eventual limitação.

Pico não será usado como medida principal: sinais com o mesmo pico podem ter
volumes percebidos muito diferentes. RMS poderá existir apenas como fallback
explicitamente identificado se a medição integrada não for válida. Áudio vazio,
silencioso, curto demais ou com resultado não finito não receberá compensação.

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

Referências técnicas: [ITU-R BS.1770](https://www.itu.int/rec/R-REC-BS.1770/en)
e [EBU R128](https://tech.ebu.ch/publications/r128).
