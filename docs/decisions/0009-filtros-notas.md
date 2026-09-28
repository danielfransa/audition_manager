# 0009 — Filtros da biblioteca e notas

O usuário pediu busca/filtros e notas no mesmo commit e definiu que o polimento
técnico será iniciado somente depois da validação prática desta entrega.

- Os filtros atuam sobre os IRs válidos do último diretório escaneado. Busca
  compara nome e caminho relativo sem diferenciar maiúsculas/minúsculas;
  favorito e avaliação mínima podem ser combinados.
- A filtragem é feita em memória consultando os metadados persistidos. Ela não
  altera o banco, o stream nem a seleção de áudio ativa. Se o item selecionado
  continuar visível, a seleção visual é preservada; se for ocultado, o áudio
  continua e o rótulo IR ativo permanece como referência.
- Cada linha mostra favorito, caminho relativo e cinco estrelas. O atalho 0
  limpa a avaliação; 1..5 e F mantêm o comportamento persistente existente.
- Notas usam o campo criado na migração inicial. O usuário salva explicitamente
  pelo botão; trocar de item antes de salvar descarta o texto ainda não gravado.
- Atalhos globais são ignorados quando o editor de notas tem foco, permitindo
  digitar F, B, números, setas e espaços sem controlar o player.
- A disposição da janela foi compactada em linhas horizontais para acomodar os
  novos controles sem retirar espaço útil da lista.

O scan permanece síncrono e os filtros fazem uma consulta SQLite por item.
Esses pontos serão medidos com bibliotecas grandes durante a fase de polimento.
