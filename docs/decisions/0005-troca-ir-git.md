# 0005 — Troca automática de IR e versionamento

O usuário solicitou troca ao clicar ou navegar com setas e início do versionamento.

- Seleção dispara processamento em uma única thread. Enquanto ela trabalha,
  novas seleções substituem a solicitação pendente. Resultados e erros antigos
  não são aplicados. Não acumulamos threads por tecla pressionada.
- O áudio anterior continua tocando enquanto o próximo IR é processado.
  A troca no transporte ocorre sob lock e mantém cursor e estado naquele instante.
  Pausa e Stop continuam disponíveis durante processamento.
- O primeiro IR inicia reprodução automaticamente; Stop durante essa preparação
  permite carregar o resultado sem iniciá-lo. Selecionar IR com player parado
  mantém o estado parado, até Play.
- ↑/↓ usam a navegação nativa da lista; ←/→ são atalhos da janela. O rótulo
  IR ativo só muda quando o resultado é aplicado, inclusive após erros.
- Troca com mesma taxa e canais reutiliza o stream. Alteração do número de
  canais requer reabrir o stream, preservando tempo/estado, mas pode causar
  uma breve interrupção. Não há crossfade nem cache de múltiplos resultados.
- DI ou pasta nova limpa o resultado anterior. A extensão para bypass e demais
  atalhos fica para outro incremento.
- Git inicializado em main usando a identidade já configurada no ambiente.
  Primeiro commit registra a base existente; o seguinte registra esta mudança.
  Sem remoto ou push. Venv, ferramentas locais e exemplos de áudio ficam ignorados.
