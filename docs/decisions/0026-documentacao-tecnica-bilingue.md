# 0026 — Documentação técnica bilíngue

Data: 29 de outubro de 2026

## Contexto

Os guias públicos já existiam em Português e Inglês, mas status, arquitetura,
validação, plano e decisões ainda exigiam leitura dos arquivos históricos em
Português. Copiar todo o histórico para duas árvores independentes aumentaria o
risco de divergência a cada incremento.

## Decisão

- Publicar em Inglês os documentos técnicos vigentes de status, arquitetura,
  validação e roadmap.
- Manter os documentos originais em Português como fontes canônicas do histórico
  e fornecer um índice técnico em `docs/pt-BR/`.
- Criar registros PT/EN das decisões, mantendo os ADRs originais imutáveis e
  oferecendo títulos e resultados em Inglês.
- Preservar o prompt inicial somente no idioma em que foi escrito, pois ele é um
  artefato de entrada, não uma instrução vigente.

## Consequências

Leitores dos dois idiomas conseguem instalar, usar e compreender o estado e a
arquitetura. O histórico continua auditável sem duplicar 25 ADRs e centenas de
linhas cronológicas que poderiam divergir. Novos documentos vigentes devem ser
adicionados à navegação dos dois idiomas no mesmo incremento.
