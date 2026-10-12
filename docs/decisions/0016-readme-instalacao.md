# 0016 — README público e instalação multiplataforma

O usuário pediu que a página inicial do repositório apresentasse o produto e
permitisse que uma pessoa nova chegasse ao primeiro teste sem atravessar o
histórico de desenvolvimento.

- O README agora concentra objetivo, estágio do produto, funções disponíveis,
  instalação rápida, primeiro uso, limites e links de acompanhamento.
- Detalhes de mise, venv manual, WSLg, dados locais e solução de problemas foram
  movidos para `docs/installation.md`.
- Arquitetura, ferramentas, testes e limites internos foram movidos para
  `docs/development.md`. O histórico permanece em decisões e validação.
- Linux oferece comandos para famílias Debian, Fedora e Arch. Os nomes das
  bibliotecas XKB/XCB, Mesa, fontes e PortAudio foram conferidos nos catálogos
  oficiais dessas distribuições em 12 de outubro de 2026.
- Windows oferece execução pela venv e criação do ZIP portátil. O README deixa
  claro que ainda não existe Release binária nem instalador validado.
- Como este repositório local ainda não possui remoto, os exemplos usam
  `URL_HTTPS_DESTE_REPOSITORIO` e instruem copiar a URL exibida pelo GitHub. Uma
  URL definitiva deve substituir esse marcador depois da publicação.

Fontes de pacotes consultadas:

- Debian: <https://packages.debian.org/>
- Fedora: <https://packages.fedoraproject.org/>
- Arch Linux: <https://archlinux.org/packages/>
- mise: <https://mise.jdx.dev/getting-started.html>
