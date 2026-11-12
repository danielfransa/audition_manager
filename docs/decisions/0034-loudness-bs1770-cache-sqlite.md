# 0034 — Loudness BS.1770 e cache SQLite da cadeia

## Contexto

A decisão 0033 definiu medir a cadeia completa. A implementação precisa separar
medição e limitador, evitar recalcular combinações já conhecidas e representar
também os casos em que o áudio não permite medição integrada.

## Decisão

Usar `pyloudnorm` 0.2.x, sob licença MIT, como implementação de ITU-R BS.1770.
Renderizar a cadeia sem limite, medir, aplicar a compensação limitada, aplicar o
ganho manual e executar a proteção de pico por último.

A migração SQLite v4 cria `level_measurement`. A chave SHA-256 inclui identidades
de DI, NAM e IR, modo Full/Lite, alvo e versão do algoritmo. Resultados medidos,
fallbacks NAM e indisponibilidade por silêncio/curta duração são persistidos.

## Consequências

- Uma combinação é medida somente na primeira reprodução enquanto sua identidade
  permanecer igual.
- O metadado NAM deixa de ser a fonte principal quando existe medição completa.
- A nova dependência será incluída automaticamente pelo build PyInstaller e deve
  ser confirmada no próximo ZIP Windows.
- A alpha não será publicada antes do teste auditivo e de desempenho.
