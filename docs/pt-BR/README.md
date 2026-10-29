# Audition Manager — Português

O Audition Manager é uma aplicação desktop open source para guitarristas ouvirem,
compararem e organizarem IRs e capturas NAM antes de copiá-los para pedaleiras,
modeladores ou outras bibliotecas.

## Estado atual

Já estão disponíveis:

- seleção de DI WAV e scan recursivo de IRs;
- reprodução offline automática ao trocar IR ou captura;
- capturas NAM A2 Full/Lite e modelos legados compatíveis;
- cadeia `DI → NAM → IR`, com bypasses independentes;
- busca, filtros, favoritos, estrelas e notas para IRs e capturas;
- ganho NAM, ganho geral, medidor de pico, Loop, Play/Pause e Stop;
- exportação dos favoritos em pastas separadas `Capturas` e `IRs`;
- interface em Português e Inglês;
- duas DIs, quatro IRs e duas capturas NAM MIT para testes.

Ainda estão pendentes o pacote portátil validado em Windows real, instalador,
entrada de guitarra ao vivo e transferência direta para BlackBox/IR-Box.

## Começar

1. Siga a [instalação para Linux, Windows ou WSL](installation.md).
2. Abra o [guia de uso](usage.md).
3. Use os arquivos da pasta [`samples/`](../../samples/README.md) no primeiro teste.

## Atalhos

| Tecla | Ação |
| --- | --- |
| Espaço | Play/Pause |
| B | Bypass do IR |
| N | Bypass da captura NAM |
| F | Favoritar IR |
| 1–5 | Avaliar IR |
| 0 | Limpar avaliação do IR |
| ←/→ | Navegar pelos IRs |
| Ctrl+←/→ | Navegar pelas capturas |

## Documentação

- [Instalação](installation.md)
- [Guia de uso](usage.md)
- [Índice da documentação técnica](technical.md)
- [Status detalhado](../status.md)
- [Plano](../../PLAN.md)
- [Desenvolvimento](../development.md)
- [Validação](../validacao.md)
- [Registro das decisões](decisions.md)

## Licença

O código é distribuído sob a [licença MIT](../../LICENSE). Dependências, IRs,
capturas e demais áudios mantêm suas próprias licenças. Consulte a documentação
em [`samples/`](../../samples/README.md) antes de redistribuir exemplos.
