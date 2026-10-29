# 0024 — Internacionalização da aplicação

## Contexto

A interface foi criada inicialmente em Português. A distribuição para Windows e
Linux deve atender também usuários que esperam uma interface em Inglês.

## Decisão

Usar um catálogo Python pequeno e explícito em `audition_manager/i18n.py`, sem
adicionar dependência externa. Português do Brasil (`pt_BR`) permanece como
padrão e Inglês (`en`) é a segunda opção.

O seletor fica na janela principal. A troca ocorre sem reiniciar, atualiza os
principais controles, diálogos, estados do player e mensagens de operação, e é
gravada em `preferences.json`. Valores desconhecidos voltam com segurança para
Português.

Os textos usam a forma em Português como chave do catálogo nesta etapa. A lógica
de áudio, banco e arquivos permanece independente da escolha do idioma.

## Próximos incrementos

O README público será reduzido a uma apresentação bilíngue com links para guias
completos PT/EN. Depois, a documentação técnica e histórica será espelhada por
idioma antes da geração do pacote Windows.
