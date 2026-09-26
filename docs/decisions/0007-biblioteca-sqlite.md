# 0007 — Biblioteca SQLite, favoritos e avaliação

O usuário aprovou o incremento anterior e autorizou continuar. Esta rodada
implementa a parte persistente do item 3 do MVP, sem adicionar dependências.

- SQLite da biblioteca padrão armazena caminho absoluto, nome, taxa, canais,
  favorito, avaliação, notas e timestamps. O áudio permanece no sistema de
  arquivos. `schema_version` inicia migrações explícitas na versão 1.
- O caminho segue o sistema: `%LOCALAPPDATA%` no Windows e XDG no Linux. A
  variável `AUDITION_MANAGER_DATA_DIR` permite isolar testes e instalações.
- O scan lê somente o cabeçalho dos WAVs com soundfile. Candidatos inválidos
  não entram na lista nem no banco; a interface mostra quantos foram ignorados.
- Reescaneamento atualiza nome, taxa e canais e preserva favorito, avaliação e
  notas. Registros ausentes da pasta não são apagados, preservando escolhas se
  um disco externo estiver desconectado ou o arquivo voltar depois.
- F alterna favorito; 1..5 define a avaliação. O checkbox também pode ser
  clicado. O valor selecionado aparece em estrelas. Não há nota zero por atalho
  nesta etapa; filtros e editor de notas serão incrementos separados.
- O repositório recebe `Path` e modelos, sem depender de Qt. A janela recebe o
  repositório por injeção; `main.py` compõe a implementação SQLite concreta.
- O scan ainda ocorre na thread da interface. Isso mantém a entrega pequena,
  mas bibliotecas muito grandes podem bloquear a janela temporariamente.

Risco conhecido: caminhos absolutos mudam se a coleção for movida. Uma futura
estratégia de reconciliação por raiz/identidade deve ser definida com dados reais.
