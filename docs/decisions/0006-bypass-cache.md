# 0006 — Bypass, atalhos e cache de sessão

O usuário aprovou a troca automática e autorizou continuar. Este incremento
completa bypass, Espaço/B e cache do item 2 do plano, sem avançar para SQLite.

- B alterna bypass; Espaço alterna Play/Pause. Ambos desativam autorrepetição
  para evitar alternância contínua ao segurar a tecla. Operam na janela principal.
- Bypass passa a DI sem convolução pela mesma proteção de pico usada no resultado
  processado. Não amplifica nem equaliza volumes. Mantém sample rate e canais
  da DI. Pode funcionar sem IR selecionado.
- A duração seca não inclui cauda. Se a troca ocorrer já na cauda processada,
  o cursor é limitado ao fim da DI; sem loop termina, com loop reinicia no
  próximo bloco. Mudanças de canais ainda exigem reabrir o stream.
- A seleção usa a mesma fila de uma tarefa ativa e uma solicitação atual:
  toggles rápidos descartam resultados antigos. Stop durante processamento
  continua impedindo reprodução automática.
- Cache LRU em memória: até quatro buffers e 128 MiB. Chave inclui caminhos
  resolvidos, tamanho, mtime e ctime de DI/IR; bypass usa uma chave sem IR.
  Não faz hash integral dos arquivos. Arquivos que mudam durante a leitura
  não têm resultado armazenado. Arquivos grandes demais são processados sem
  entrar no cache. O limite não é um limite global de memória do aplicativo.
- Cache é acessado somente pela thread de renderização; DI/pasta nova substitui
  a instância do cache. Nenhum arquivo ou resultado é gravado em disco.
- Crossfade permanece adiado: precisa tratar duração, estado e layouts de canais
  durante a mistura de buffers. A troca atual pode produzir clicks; isso não
  bloqueia a auditoria de bypass/cache nem o MVP inicial previsto no prompt.

Nenhuma dependência adicional foi incluída.
