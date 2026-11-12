# 0030 — Ordem: nivelamento, entrada ao vivo, comparação cega e instalador

## Contexto

O feedback da comunidade apontou que diferenças de volume podem influenciar a
avaliação de capturas e IRs. Arquivos NAM podem fornecer `loudness`,
`input_level_dbu` e `output_level_dbu`, mas o aplicativo ainda não lê esses
campos. IRs e modelos sem metadados precisam de uma medição reproduzível.

Também permanecem no roadmap a entrada de guitarra ao vivo, o modo de comparação
cega e um instalador Windows. O ZIP portátil da primeira alpha já foi validado e
permite adiar o instalador sem bloquear os testes públicos.

## Decisão

1. A próxima alpha reunirá três incrementos, implementados e validados
   separadamente: leitura/persistência de metadados NAM; equalização automática
   opcional; medição e cache de compensação para NAMs sem metadados e IRs.
2. Depois dessa alpha, implementar e consolidar a entrada de guitarra ao vivo.
3. Implementar a comparação cega somente depois da entrada ao vivo.
4. Criar o instalador Windows por último. Até lá, manter o ZIP portátil.

O nivelamento será sempre opcional. Desativá-lo deverá reproduzir o nível
original, sujeito apenas aos controles manuais e à proteção de pico já existentes.

## Consequências

- O SQLite precisará de nova migração para metadados e resultados de medição.
- O cache deve ser invalidado quando o arquivo ou a DI de referência mudar.
- A interface deve distinguir nível original, ganho manual e compensação
  automática.
- A nova alpha só será publicada depois da auditoria prática dos três incrementos.
- A comparação cega não bloqueará o trabalho de áudio em tempo real.
- O instalador não consumirá esforço enquanto a aplicação ainda muda em áreas
  estruturais.
