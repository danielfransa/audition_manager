# 0004 — Player com posição, pausa e loop

Data: 2026-09-26. Escopo: item 1 do MVP de IRs no PLAN.md.

Após confirmar o funcionamento no WSL, o usuário autorizou o próximo incremento.
Esta entrega cobre controle de transporte. Troca contínua de IR, bypass, atalhos
 e persistência seguem para rodadas posteriores.

## Decisões

- `PlaybackTransport` mantém áudio, cursor em frames e estados empty, stopped,
  playing, paused e finished. Não conhece Qt nem dispositivo de áudio.
- `AudioOutput` possui seu próprio `sounddevice.OutputStream`, substituindo as
  funções globais play/stop. O callback copia o resultado já processado e
  preenche com zeros a sobra do último bloco. CallbackStop permite tocar a cauda
  já enfileirada. Não há leitura de arquivo ou convolução dentro do callback.
- Pause para o stream aguardando os buffers pendentes, preservando o cursor.
  Stop aborta o stream e zera o cursor. Play após o fim recomeça do zero.
- Um Lock protege cursor/estado contra acesso simultâneo da GUI e callback.
  As seções críticas são pequenas, mas esta implementação ainda não é indicada
  para baixa latência/entrada ao vivo; essa etapa exigirá rever sincronização.
- Loop pode mudar durante reprodução ou pausa. Mesmo arquivos menores que um
  bloco repetem sem inserir silêncio artificial na fronteira. A cauda original
  continua incluída; crossfade não está implementado.
- O resultado permanece em memória para Pause/Play/Stop, sem nova convolução.
  Selecionar outra DI, IR ou pasta limpa esse resultado e fecha o stream.
- A GUI consulta a posição a cada 100 ms. Ela representa amostras enviadas ao
  dispositivo, não uma medição do instante ouvido. A barra não permite seek.
- Fechar a janela libera o stream. Não adicionamos dependências.

## Limitações

Pause pode levar o tempo de drenagem dos buffers do backend. Windows nativo e
Linux nativo precisam de validação específica. Desconexão de dispositivo durante
reprodução e recuperação automática serão tratadas com seleção de dispositivos.
A troca de IR ainda exige processamento e reinicia a faixa.

Referência: [sounddevice — ciclo de vida e callbacks dos streams](https://python-sounddevice.readthedocs.io/en/latest/api/streams.html).
