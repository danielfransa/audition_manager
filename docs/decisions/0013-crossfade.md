# 0013 — Crossfade curto na troca de IR

Terceiro incremento do polimento técnico aprovado pelo usuário.

- Trocas de áudio com a mesma taxa e quantidade de canais usam crossfade linear
  de 10 ms. A duração é suficiente para suavizar a descontinuidade entre formas
  de onda e curta para não mascarar a comparação entre IRs.
- A soma das rampas permanece igual a 1. Foi escolhida a rampa linear em vez da
  equal-power porque sinais de DI correlacionados poderiam ganhar até 3 dB no
  meio da transição, prejudicando a comparação e o headroom.
- O transporte prepara somente 10 ms do áudio anterior quando a troca acontece.
  Pesos e contribuição antiga ficam prontos antes do callback; o callback não
  lê arquivos nem calcula a rampa.
- O cursor avança uma única vez pelo áudio novo. Pausa adia a transição até Play,
  Stop descarta a transição, e Loop também é respeitado ao capturar o trecho
  antigo próximo ao fim da faixa.
- Mono para estéreo ou estéreo para mono ainda exige recriar o stream PortAudio.
  Esses formatos não podem coexistir no mesmo buffer do dispositivo, portanto
  essa troca preserva tempo e estado, mas mantém a breve interrupção existente.
- Em áudio estéreo de 48 kHz, a preparação foi medida em aproximadamente 10 µs
  por troca neste ambiente WSL. A medição é de custo computacional, não de
  latência audível ou do dispositivo.
