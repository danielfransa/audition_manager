# 0031 — Metadados de nível NAM sem alteração do áudio

## Contexto

O primeiro incremento da comparação equilibrada precisa conhecer os dados já
fornecidos pelo formato NAM antes de aplicar qualquer política de ganho. Os
campos são opcionais e arquivos antigos ou produzidos por ferramentas diferentes
podem omiti-los ou apresentar valores inválidos.

## Decisão

Ler `loudness`, `input_level_dbu` e `output_level_dbu` do objeto `metadata`.
Aceitar somente números finitos, excluindo booleanos; tratar qualquer outro valor
como ausente sem rejeitar a captura.

Persistir os campos como `REAL NULL` na migração SQLite v3 e apresentá-los em uma
linha bilíngue associada à captura selecionada. Não aplicar ganho, normalização ou
compensação neste incremento.

## Consequências

- Capturas antigas continuam compatíveis.
- Um novo scan atualiza os metadados técnicos e preserva favorito, nota e
  avaliação.
- A interface deixa explícita a diferença entre dado ausente e valor zero.
- A política de equalização automática poderá ser implementada e auditada
  separadamente.
