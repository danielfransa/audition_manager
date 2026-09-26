# 0008 — Seleção de dispositivo e ganho de saída

Esta rodada conclui as funções do item 4 do MVP no ambiente atual.

- A lista mostra somente dispositivos com canais de saída e inclui o nome da
  API do host (ALSA, WASAPI etc.). A primeira opção deixa PortAudio seguir o
  dispositivo padrão do sistema.
- A seleção guarda o índice PortAudio apenas durante a execução. Se já houver
  áudio, fecha e reabre o stream com o novo dispositivo e restaura posição,
  Play/Pause e Loop. A troca pode produzir uma breve interrupção.
- Se a nova saída falhar, o buffer e a posição permanecem carregados em Pause,
  permitindo escolher outra saída. O erro do backend é mostrado pela interface.
- O ganho é uma atenuação de -24 a 0 dB. A multiplicação acontece no buffer de
  saída, usando operação NumPy in-place; o áudio processado e o cache não mudam.
  Ganho positivo foi excluído para não introduzir clipping após a proteção de pico.
- Lista, seleção e ganho pertencem ao adaptador de saída. A interface não acessa
  sounddevice diretamente. Não foram adicionadas dependências.

Dispositivo e ganho ainda não são persistidos. Índices PortAudio podem mudar
entre execuções, então persistência futura deve preferir uma identidade estável
com fallback claro. Windows/WASAPI e Linux nativo ainda exigem teste manual.
